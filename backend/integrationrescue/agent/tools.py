"""Typed, permission-controlled tools available to the investigating agent.

Every tool input is validated with Pydantic; every output is redacted and
truncated; every call is budgeted and recorded in the audit trail.
Investigation tools are read-only. The only write the agent can cause is a
*proposal* that deterministic code reviews and applies in a sandbox.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..security.policy import PolicyViolation, redact, safe_relpath
from ..simulators.sync_service import run_handler
from . import sandbox

ALLOWED_ORIGINS = {"http://testserver", "http://127.0.0.1:8100", "http://localhost:8100"}
MAX_OUTPUT_CHARS = 6000


class SimClient:
    """GET-only client for the simulator API, restricted to an origin allow-list."""

    def __init__(self, http: httpx.Client, world_id: str):
        origin = "{0.scheme}://{0.netloc}".format(urlsplit(str(http.base_url)))
        if origin not in ALLOWED_ORIGINS:
            raise PolicyViolation(f"origin {origin} is not on the approved local allow-list")
        self.http, self.world_id = http, world_id

    def get(self, path: str, **params: Any) -> Any:
        if not re.fullmatch(r"[A-Za-z0-9_\-/]+", path):
            raise PolicyViolation(f"illegal API path {path!r}")
        resp = self.http.get(f"/worlds/{self.world_id}/{path.lstrip('/')}",
                             params={k: v for k, v in params.items() if v is not None})
        if resp.status_code >= 400:
            return {"http_status": resp.status_code, "error": resp.text[:500]}
        return resp.json()


@dataclass
class ToolContext:
    incident: dict[str, Any]
    repo_dir: Path
    sim: SimClient
    scratch_dir: Path
    hypotheses: list[dict[str, Any]] = field(default_factory=list)


# ------------------------------------------------------------------ input models
class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NoArgs(Strict):
    pass


class Email(Strict):
    email: str = Field(max_length=200)


class CustomerId(Strict):
    customer_id: str = Field(max_length=64)


class InvoiceId(Strict):
    invoice_id: str = Field(max_length=64)


class PriceId(Strict):
    price_id: str = Field(max_length=128)


class PlanFamily(Strict):
    plan_family: str | None = Field(default=None, max_length=32)


class EventId(Strict):
    event_id: str = Field(max_length=64)


class AccountId(Strict):
    account_id: str = Field(max_length=64)


class LogSearch(Strict):
    q: str | None = Field(default=None, max_length=200)
    service: str | None = Field(default=None, max_length=64)
    level: Literal["info", "warning", "error"] | None = None
    limit: int = Field(default=50, ge=1, le=200)


class RepoPath(Strict):
    path: str = Field(max_length=300)


class RepoSearch(Strict):
    pattern: str = Field(max_length=200)


class Hypothesis(Strict):
    id: str = Field(max_length=16)
    statement: str = Field(max_length=500)
    status: Literal["open", "supported", "refuted", "confirmed"]
    evidence: str = Field(default="", max_length=1000)


class Hypotheses(Strict):
    hypotheses: list[Hypothesis] = Field(max_length=10)


class Diagnosis(Strict):
    root_cause: str = Field(max_length=2000)
    category: Literal["config_mapping", "code_defect", "schema_drift", "delivery", "credentials",
                      "idempotency", "external_state", "unknown"]
    evidence: list[str] = Field(max_length=20)
    affected_files: list[str] = Field(default_factory=list, max_length=10)
    replay_event_id: str = Field(max_length=64)
    confidence: float = Field(ge=0, le=1)


class Edit(Strict):
    op: Literal["json_set", "replace"]
    path: str = Field(max_length=300)
    key_path: list[str] | None = None
    value: Any = None
    old: str | None = None
    new: str | None = None


class PatchProposal(Strict):
    edits: list[Edit] = Field(min_length=1, max_length=5)
    rationale: str = Field(max_length=2000)


class Reason(Strict):
    reason: str = Field(max_length=2000)


# ------------------------------------------------------------------ implementations
def _list_files(ctx: ToolContext, _: NoArgs) -> Any:
    out = []
    for p in sorted(ctx.repo_dir.rglob("*")):
        rel = p.relative_to(ctx.repo_dir).as_posix()
        if p.is_file() and "__pycache__" not in rel and not any(s.startswith(".") for s in rel.split("/")):
            out.append(rel)
    return out


def _read_file(ctx: ToolContext, a: RepoPath) -> Any:
    target = safe_relpath(ctx.repo_dir, a.path)
    if not target.is_file():
        return {"error": f"no such file {a.path}"}
    return target.read_text(encoding="utf-8")[:MAX_OUTPUT_CHARS]


def _search(ctx: ToolContext, a: RepoSearch) -> Any:
    try:
        rx = re.compile(a.pattern)
    except re.error as exc:
        return {"error": f"bad regex: {exc}"}
    hits = []
    for rel in _list_files(ctx, NoArgs()):
        for i, line in enumerate((ctx.repo_dir / rel).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{rel}:{i}: {line.strip()}")
    return hits[:100]


def _dry_run_handler(ctx: ToolContext, a: EventId) -> Any:
    """Run the current handler code against a stored event with no side effects."""
    event = ctx.sim.get(f"billing/events/{a.event_id}")
    if "error" in event:
        return event
    return run_handler(ctx.repo_dir, event, event.get("data", {}).get("tenant", ""))


def _run_tests(ctx: ToolContext, _: NoArgs) -> Any:
    with tempfile.TemporaryDirectory(dir=ctx.scratch_dir) as tmp:
        copy = sandbox.copy_repo(ctx.repo_dir, Path(tmp) / "repo")
        return sandbox.run_tests(copy)


def _compare(ctx: ToolContext, a: CustomerId) -> Any:
    invoices = ctx.sim.get(f"billing/customers/{a.customer_id}/invoices")
    accounts = ctx.sim.get("entitlements/accounts", customer_id=a.customer_id)
    if not isinstance(invoices, list) or not isinstance(accounts, list) or not accounts:
        return {"error": "could not read billing or entitlement state", "invoices": invoices, "accounts": accounts}
    paid = [i for i in invoices if i["status"] == "paid"]
    expected = None
    if paid:
        price = ctx.sim.get(f"billing/prices/{paid[-1]['price_id']}")
        expected = price.get("plan_family") if isinstance(price, dict) else None
    observed = accounts[0]["plan"]
    return {"expected_plan_from_billing": expected, "observed_plan": observed,
            "diverged": expected is not None and expected != observed,
            "latest_paid_invoice": paid[-1] if paid else None}


def _record_hypotheses(ctx: ToolContext, a: Hypotheses) -> Any:
    ctx.hypotheses = [h.model_dump() for h in a.hypotheses]
    return {"recorded": len(ctx.hypotheses)}


def _get_incident(ctx: ToolContext, _: NoArgs) -> Any:
    return {"title": ctx.incident["title"], "description": ctx.incident["description"],
            "severity": ctx.incident.get("severity"), "attachments": ctx.incident.get("attachments", [])}


@dataclass
class Tool:
    name: str
    description: str
    model: type[BaseModel]
    fn: Callable[[ToolContext, Any], Any] | None
    kind: Literal["read", "control", "terminal"] = "read"


def _sim(path_fmt: str, **param_fields: str) -> Callable[[ToolContext, Any], Any]:
    def fn(ctx: ToolContext, a: BaseModel) -> Any:
        values = a.model_dump()
        path = path_fmt.format(**values)
        params = {k: values[v] for k, v in param_fields.items()}
        return ctx.sim.get(path, **params)
    return fn


TOOLS: dict[str, Tool] = {t.name: t for t in [
    Tool("get_incident", "Read the incident ticket (untrusted customer-supplied text).", NoArgs, _get_incident),
    Tool("billing_find_customer", "Look up a billing customer by email.", Email,
         _sim("billing/customers", email="email")),
    Tool("billing_list_invoices", "List a customer's invoices.", CustomerId,
         _sim("billing/customers/{customer_id}/invoices")),
    Tool("billing_get_charges", "List charges for an invoice.", InvoiceId,
         _sim("billing/invoices/{invoice_id}/charges")),
    Tool("billing_get_price", "Get a price from the billing catalog (includes plan_family).", PriceId,
         _sim("billing/prices/{price_id}")),
    Tool("billing_list_prices", "List catalog prices, optionally by plan family.", PlanFamily,
         _sim("billing/prices", plan_family="plan_family")),
    Tool("billing_list_events", "List billing webhook events emitted for a customer.", CustomerId,
         _sim("billing/events", customer_id="customer_id")),
    Tool("webhooks_list_deliveries", "List delivery attempts (status, HTTP code, ack) for an event.", EventId,
         _sim("webhooks/deliveries", event_id="event_id")),
    Tool("entitlements_get_account", "Get the entitlement account (plan, features) for a customer.", CustomerId,
         _sim("entitlements/accounts", customer_id="customer_id")),
    Tool("entitlements_get_audit", "Get the plan-change audit history for an account.", AccountId,
         _sim("entitlements/accounts/{account_id}/audit")),
    Tool("entitlements_processed_event", "Check how the sync service recorded processing of an event.", EventId,
         _sim("entitlements/processed-events/{event_id}")),
    Tool("logs_search", "Search structured service logs (billing, webhooks, entitlement-sync, entitlements).",
         LogSearch, _sim("logs", q="q", service="service", level="level", limit="limit")),
    Tool("compare_billing_vs_entitlement", "Compare the plan billing says was paid with the observed entitlement.",
         CustomerId, _compare),
    Tool("repo_list_files", "List files in the integration repository.", NoArgs, _list_files),
    Tool("repo_read_file", "Read a file from the integration repository.", RepoPath, _read_file),
    Tool("repo_search", "Regex search across the integration repository.", RepoSearch, _search),
    Tool("dry_run_handler", "Run the current handler code on a stored event without side effects.", EventId,
         _dry_run_handler),
    Tool("run_repo_tests", "Run the repository's test-suite in a scratch copy.", NoArgs, _run_tests),
    Tool("record_hypotheses", "Record the current hypothesis list with statuses.", Hypotheses,
         _record_hypotheses, kind="control"),
    Tool("submit_diagnosis", "Submit the root-cause diagnosis (ends investigation).", Diagnosis, None, "terminal"),
    Tool("propose_patch", "Propose a minimal patch as structured edits (json_set or exact replace).",
         PatchProposal, None, "terminal"),
    Tool("declare_indeterminate", "Declare that authoritative evidence is insufficient to conclude.",
         Reason, None, "terminal"),
    Tool("escalate", "Escalate to a human with a reason.", Reason, None, "terminal"),
]}

READ_TOOLS = [n for n, t in TOOLS.items() if t.kind == "read"]
PHASE_TOOLS = {
    "investigate": READ_TOOLS + ["record_hypotheses", "submit_diagnosis", "declare_indeterminate", "escalate"],
    "patch": READ_TOOLS + ["record_hypotheses", "propose_patch", "escalate"],
}


def tool_schemas(phase: str) -> list[dict[str, Any]]:
    return [{"name": n, "description": TOOLS[n].description,
             "input_schema": TOOLS[n].model.model_json_schema()} for n in PHASE_TOOLS[phase]]


@dataclass
class ToolOutcome:
    ok: bool
    output: Any
    terminal: bool = False
    args: dict[str, Any] | None = None


def execute(ctx: ToolContext, phase: str, name: str, raw_args: dict[str, Any]) -> ToolOutcome:
    """Validate and run one tool call under the phase's permission set."""
    if name not in TOOLS:
        return ToolOutcome(False, {"error": f"unknown tool {name}"})
    if name not in PHASE_TOOLS[phase]:
        return ToolOutcome(False, {"error": f"tool {name} is not permitted in phase {phase}"})
    tool = TOOLS[name]
    try:
        args = tool.model.model_validate(raw_args or {})
    except ValidationError as exc:
        return ToolOutcome(False, {"error": "invalid arguments", "details": json.loads(exc.json())[:5]})
    if tool.kind == "terminal":
        return ToolOutcome(True, {"accepted": True}, terminal=True, args=args.model_dump())
    try:
        output = tool.fn(ctx, args)
    except PolicyViolation as exc:
        return ToolOutcome(False, {"error": "policy_violation", "detail": str(exc)})
    except httpx.HTTPError as exc:
        return ToolOutcome(False, {"error": "transport_error", "detail": type(exc).__name__})
    text = output if isinstance(output, str) else json.dumps(output, default=str)
    text = redact(text)
    if len(text) > MAX_OUTPUT_CHARS:
        text = text[:MAX_OUTPUT_CHARS] + "...[truncated]"
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = text
    return ToolOutcome(True, parsed, args=args.model_dump())
