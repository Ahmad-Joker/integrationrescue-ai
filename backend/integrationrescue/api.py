"""Product API used by the dashboard. Run: uvicorn integrationrescue.api:app --port 8000"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from . import __version__
from .agent.orchestrator import IncidentService
from .agent.providers import ProviderError, make_provider
from .agent.store import Store
from .evaluation import latest_results, run_suite
from .paths import load_env_file
from .scenarios import REGISTRY
from .security.policy import redact
from .simulators.api import build_router
from .simulators.world import World

load_env_file()

MAX_UPLOAD_BYTES = 2_000_000
ALLOWED_UPLOADS = {".log", ".txt", ".json", ".png", ".jpg", ".jpeg"}

app = FastAPI(title="IntegrationRescue", version=__version__)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])

_svc: IncidentService | None = None
_running: set[str] = set()
_lock = threading.Lock()
_eval_state: dict[str, Any] = {"running": False, "error": None}


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
    provider: str = "deterministic"
    faults: dict[str, Any] = Field(default_factory=dict)
    auto_approve: bool = False
    description: str | None = Field(default=None, max_length=5000)
    autorun: bool = True


class Decision(BaseModel):
    approver: str = Field(min_length=1, max_length=120)
    reason: str = Field(default="", max_length=1000)


ALLOWED_FAULTS = {"duplicate_delivery", "lost_ack", "billing_ledger_unavailable"}


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


@app.get("/api/health")
def health() -> dict[str, Any]:
    live = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    return {"status": "ok", "version": __version__, "live_model_configured": live,
            "default_provider": os.environ.get("IR_PROVIDER", "deterministic")}


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
    try:
        make_provider(req.provider)
    except ProviderError as exc:
        raise HTTPException(400, str(exc)) from exc
    iid = svc().create_from_scenario(req.family, req.variant, req.seed, provider=req.provider,
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
        "usage": d.get("usage", {}),
        "timeline": svc().store.timeline(iid),
    }


@app.post("/api/incidents/{iid}/run")
def run_incident(iid: str) -> dict[str, Any]:
    if not svc().store.get(iid):
        raise HTTPException(404)
    _run_bg(iid)
    return {"started": True}


@app.post("/api/incidents/{iid}/approve")
def approve(iid: str, d: Decision) -> dict[str, Any]:
    try:
        svc().approve(iid, d.approver)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    _run_bg(iid)
    return {"approved": True}


@app.post("/api/incidents/{iid}/reject")
def reject(iid: str, d: Decision) -> dict[str, Any]:
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
