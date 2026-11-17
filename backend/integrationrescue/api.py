"""Product API used by the dashboard. Run: uvicorn integrationrescue.api:app --port 8000"""

from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field

from . import __version__
from .agent.orchestrator import IncidentService
from .agent.providers import ProviderError, make_provider
from .agent.store import Store
from .config import Settings, load_settings
from .demo_seed import FEATURED, seed_demo
from .evaluation import latest_results, run_suite
from .paths import load_env_file, var_dir
from .scenarios import REGISTRY
from .security.access import ACCESS_HEADER, ADMIN_HEADER, DailyCap, RateLimiter, client_key, token_ok
from .security.policy import redact
from .simulators.api import build_router
from .simulators.world import World

load_env_file()
SETTINGS: Settings = load_settings()  # raises ConfigError: a misconfigured public demo must not start

MAX_UPLOAD_BYTES = 2_000_000
MAX_BODY_BYTES = 2_500_000
ALLOWED_UPLOADS = {".log", ".txt", ".json", ".png", ".jpg", ".jpeg"}
MUTATING = {"POST", "PUT", "PATCH", "DELETE"}

app = FastAPI(title="IntegrationRescue", version=__version__)
app.add_middleware(CORSMiddleware, allow_origins=list(SETTINGS.cors_origins), allow_methods=["GET", "POST"],
                   allow_headers=["content-type", ACCESS_HEADER, ADMIN_HEADER])

_svc: IncidentService | None = None
_running: set[str] = set()
_lock = threading.Lock()
_eval_state: dict[str, Any] = {"running": False, "error": None}
_limiter = RateLimiter(SETTINGS.rate_limit_per_min)
_live_cap = DailyCap(SETTINGS.max_live_incidents_per_day)


def _deny(status: int, detail: str) -> JSONResponse:
    return JSONResponse({"detail": detail}, status_code=status)


@app.middleware("http")
async def guard(request: Request, call_next: Any) -> Response:
    """Access code, admin code, body size and rate limit for state-changing requests; security headers for all."""
    path = request.url.path
    if request.method in MUTATING and path.startswith(("/api/", "/sim/")):
        try:
            if int(request.headers.get("content-length") or 0) > MAX_BODY_BYTES:
                return _deny(413, "request body too large")
        except ValueError:
            return _deny(400, "invalid content-length")
        if path.startswith("/api/admin/"):
            if not SETTINGS.admin_token:
                return _deny(404, "admin endpoints are disabled (IR_ADMIN_TOKEN not set)")
            if not token_ok(request.headers.get(ADMIN_HEADER), SETTINGS.admin_token):
                return _deny(401, "admin code required")
        elif not token_ok(request.headers.get(ACCESS_HEADER), SETTINGS.access_token):
            return _deny(401, "access code required")
        if not _limiter.allow(client_key(request, SETTINGS.trust_proxy)):
            return _deny(429, "too many requests; wait a minute and retry")
    response: Response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "DENY")
    if not path.startswith(("/docs", "/redoc")):  # Swagger UI loads its assets from a CDN
        response.headers.setdefault("Content-Security-Policy",
                                    "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                                    "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
    return response


def svc() -> IncidentService:
    global _svc
    if _svc is None:
        _svc = IncidentService(Store())
    return _svc


app.include_router(build_router(lambda wid: World(svc().world_path(wid))), prefix="/sim")


class ScenarioRequest(BaseModel):
    family: str = "payment_entitlement"
    variant: str = "stale_price_id"
    seed: int = Field(default=42, ge=0, le=10_000_000)
    provider: str | None = Field(default=None, max_length=40)  # None: the server's IR_PROVIDER
    faults: dict[str, Any] = Field(default_factory=dict)
    auto_approve: bool = False
    description: str | None = Field(default=None, max_length=5000)
    autorun: bool = True


class Decision(BaseModel):
    approver: str = Field(min_length=1, max_length=120)
    reason: str = Field(default="", max_length=1000)


ALLOWED_FAULTS = {"duplicate_delivery", "lost_ack", "billing_ledger_unavailable"}


def _ensure_capacity() -> None:
    with _lock:
        if len(_running) >= SETTINGS.max_concurrent_runs:
            raise HTTPException(429, f"{len(_running)} investigations already running; retry in a minute")


def _run_bg(iid: str) -> None:
    with _lock:
        if iid in _running:
            return
        _running.add(iid)

    def work() -> None:
        try:
            svc().run(iid)
        finally:
            with _lock:
                _running.discard(iid)

    threading.Thread(target=work, daemon=True).start()


def _live_providers() -> dict[str, bool]:
    return {"claude": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")),
            "gemini": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))}


@app.on_event("startup")
def _startup() -> None:
    if SETTINGS.demo_mode and not svc().store.list(limit=1):
        threading.Thread(target=seed_demo, args=(svc(),), daemon=True).start()


@app.get("/api/health")
def health() -> dict[str, Any]:
    live = _live_providers()
    return {"status": "ok", "version": __version__, "live_model_configured": any(live.values()), "live_providers": live,
            "default_provider": SETTINGS.default_provider, "live_incidents_remaining_today": _live_cap.remaining(),
            "data": "simulated services, fictional data", **SETTINGS.public()}


@app.get("/api/demo/featured")
def featured() -> list[dict[str, Any]]:
    """Curated fictional incidents for judges (presets for the New incident form)."""
    return FEATURED


@app.post("/api/access/check")
def access_check() -> dict[str, bool]:
    # The guard middleware already validated the access code; this lets the dashboard test a code before use.
    return {"ok": True}


@app.get("/api/scenarios")
def scenarios() -> list[dict[str, Any]]:
    # Variant names are shown to the operator for demo setup; they are never given to the agent.
    return [{"family": f.name, "description": f.description, "variants": f.variants,
             "heldout_variants": f.heldout_variants} for f in REGISTRY.values()]


@app.post("/api/incidents")
def create_incident(req: ScenarioRequest) -> dict[str, Any]:
    fam = REGISTRY.get(req.family)
    if fam is None or req.variant not in fam.variants + fam.heldout_variants:
        raise HTTPException(400, "unknown scenario")
    if set(req.faults) - ALLOWED_FAULTS:
        raise HTTPException(400, f"faults must be among {sorted(ALLOWED_FAULTS)}")
    if req.auto_approve and SETTINGS.demo_mode:
        raise HTTPException(403, "auto-approval is disabled in the competition demo: a human approves every repair")
    provider = (req.provider or SETTINGS.default_provider).lower()
    try:
        prov = make_provider(provider)
    except ProviderError as exc:
        raise HTTPException(400, str(exc)) from exc
    if req.autorun:
        _ensure_capacity()
    if prov.mode == "live" and SETTINGS.demo_mode and not _live_cap.take():
        raise HTTPException(429, "today's live-model incident limit is reached (protects the model quota); "
                                 "the deterministic baseline is still available")
    iid = svc().create_from_scenario(req.family, req.variant, req.seed, provider=provider,
                                     auto_approve=req.auto_approve, faults=req.faults)
    if req.description:
        inc = svc().store.get(iid)
        inc["data"]["ticket"]["operator_notes"] = req.description
        svc().store.save(iid, inc["data"], inc["phase"], inc["outcome"])
    if req.autorun:
        _run_bg(iid)
    return {"id": iid}


@app.post("/api/incidents/{iid}/evidence")
async def upload_evidence(iid: str, file: UploadFile) -> dict[str, Any]:
    inc = svc().store.get(iid)
    if not inc:
        raise HTTPException(404)
    name = Path(file.filename or "upload").name
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_UPLOADS:
        raise HTTPException(400, f"file type {ext} not allowed")
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "file too large")
    dest = Path(inc["data"]["run_dir"]) / "evidence"
    dest.mkdir(exist_ok=True)
    (dest / name).write_bytes(raw)
    att = {"name": name, "type": ext.lstrip("."), "bytes": len(raw)}
    if ext in {".log", ".txt", ".json"}:
        att["text"] = redact(raw.decode("utf-8", errors="replace")[:20000])
    else:
        att["note"] = "image stored as evidence; vision analysis requires a configured live model"
    inc["data"]["ticket"].setdefault("attachments", []).append(att)
    svc().store.save(iid, inc["data"], inc["phase"], inc["outcome"])
    svc().store.event(iid, inc["phase"], "EVIDENCE_UPLOADED", f"Evidence uploaded: {name} ({len(raw)} bytes)")
    return att


@app.get("/api/incidents")
def list_incidents() -> list[dict[str, Any]]:
    return svc().store.list()


@app.get("/api/incidents/{iid}")
def get_incident(iid: str) -> dict[str, Any]:
    inc = svc().store.get(iid)
    if not inc:
        raise HTTPException(404)
    d = inc["data"]
    return {
        "id": iid, "phase": inc["phase"], "outcome": inc["outcome"], "mode": inc["mode"],
        "provider": inc["provider"], "created_at": inc["created_at"], "updated_at": inc["updated_at"],
        "running": iid in _running, "ticket": d["ticket"], "faults": d.get("faults", {}),
        "trace": d["trace"], "hypotheses": d["hypotheses"], "diagnosis": d["diagnosis"],
        "reproduction": d["reproduction"], "attempts": d["attempts"], "patch": d["patch"],
        "approval": d["approval"], "verification": d["verification"], "report": d["report"],
        "usage": d.get("usage", {}), "provider_error": d.get("provider_error"),
        "timeline": svc().store.timeline(iid),
    }


@app.post("/api/incidents/{iid}/run")
def run_incident(iid: str) -> dict[str, Any]:
    if not svc().store.get(iid):
        raise HTTPException(404)
    if iid not in _running:
        _ensure_capacity()
    _run_bg(iid)
    return {"started": True}


@app.post("/api/incidents/{iid}/approve")
def approve(iid: str, d: Decision) -> dict[str, Any]:
    _ensure_capacity()
    try:
        svc().approve(iid, d.approver)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    _run_bg(iid)
    return {"approved": True}


@app.post("/api/incidents/{iid}/reject")
def reject(iid: str, d: Decision) -> dict[str, Any]:
    _ensure_capacity()
    try:
        svc().reject(iid, d.approver, d.reason or "rejected")
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    _run_bg(iid)
    return {"rejected": True}


@app.get("/api/incidents/{iid}/report.md", response_class=PlainTextResponse)
def report_md(iid: str) -> str:
    inc = svc().store.get(iid)
    if not inc:
        raise HTTPException(404)
    path = Path(inc["data"]["run_dir"]) / "report.md"
    if not path.exists():
        raise HTTPException(404, "report not ready")
    return path.read_text(encoding="utf-8")


@app.get("/api/stats")
def stats() -> dict[str, Any]:
    rows = svc().store.list(limit=10_000)
    outcomes: dict[str, int] = {}
    for r in rows:
        if r["outcome"] and r["phase"] == "done":
            outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    return {
        "total": len(rows),
        "active": sum(1 for r in rows if r["phase"] not in ("done", "awaiting_approval")),
        "awaiting_approval": sum(1 for r in rows if r["phase"] == "awaiting_approval"),
        "outcomes": outcomes,
        "latest_eval": (latest_results() or [{}])[0].get("summary"),
    }


class EvalRequest(BaseModel):
    seeds: list[int] = Field(default_factory=lambda: [101], max_length=5)
    heldout: bool = True


@app.post("/api/eval/run")
def eval_run(req: EvalRequest) -> dict[str, Any]:
    # Only the deterministic suite can be launched from the UI so it never spends model credits.
    if SETTINGS.demo_mode:
        raise HTTPException(403, "running the evaluation suite is disabled on the public demo; results are shown")
    if _eval_state["running"]:
        raise HTTPException(409, "evaluation already running")
    _eval_state.update(running=True, error=None)

    def work() -> None:
        try:
            run_suite("deterministic", req.seeds, req.heldout)
        except Exception as exc:  # surfaced to the UI
            _eval_state["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            _eval_state["running"] = False

    threading.Thread(target=work, daemon=True).start()
    return {"started": True}


@app.get("/api/eval/results")
def eval_results() -> dict[str, Any]:
    return {"state": _eval_state, "results": latest_results()}


@app.post("/api/admin/reset")
def admin_reset() -> dict[str, Any]:
    """Delete all fictional demo state and re-seed. Guarded by IR_ADMIN_TOKEN in the middleware."""
    global _svc
    with _lock:
        if _running:
            raise HTTPException(409, "investigations are running; retry when they finish")
        _svc = None
        root = var_dir()
        shutil.rmtree(root / "runs", ignore_errors=True)
        (root / "incidents.db").unlink(missing_ok=True)
    seeded = seed_demo(svc()) if SETTINGS.demo_mode else []
    return {"reset": True, "seeded": seeded}


# ------------------------------------------------------------------ dashboard (single-service deployment)
@app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
def dashboard(path: str) -> Response:
    """Serve the built dashboard when IR_STATIC_DIR is set; unknown paths fall back to index.html (hash routing)."""
    if not SETTINGS.static_dir or path.startswith(("api/", "sim/")):
        raise HTTPException(404)
    root = Path(SETTINGS.static_dir).resolve()
    target = (root / path).resolve()
    if path and target.is_file() and target.is_relative_to(root):
        return FileResponse(target)
    return FileResponse(root / "index.html", headers={"Cache-Control": "no-cache"})
