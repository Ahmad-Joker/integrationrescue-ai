"""Durable investigation state machine.

The provider (LLM or deterministic baseline) chooses evidence, hypotheses, tools
and repairs. This module enforces everything else deterministically: phase
transitions, tool permissions, budgets, patch policy, sandboxing, approval gates
and the independent verification that alone can produce a VERIFIED outcome.
"""

from __future__ import annotations

import json
import random
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi.testclient import TestClient

from ..paths import runs_dir
from ..scenarios import REGISTRY
from ..security.policy import PolicyViolation, review_patch
from ..simulators.api import create_sim_app
from ..simulators.world import World
from ..verification import verify
from . import sandbox
from .providers import AgentView, Provider, ProviderError, make_provider
from .store import Store
from .tools import SimClient, ToolContext, execute

OUTCOMES = ("VERIFIED", "NO_ACTION_NEEDED", "PATCH_TESTED_NOT_VERIFIED", "DIAGNOSED", "INDETERMINATE", "ESCALATED",
            "FAILED")
MAX_TOOL_CALLS = 40
MAX_PATCH_ATTEMPTS = 3
MAX_REPRO_RETRIES = 1


class IncidentService:
    def __init__(self, store: Store | None = None, http: httpx.Client | None = None):
        self.store = store or Store()
        self._http = http

    # ------------------------------------------------------------ creation
    def world_path(self, world_id: str) -> Path:
        inc = self.store.get(world_id)
        if not inc:
            raise KeyError(world_id)
        return Path(inc["data"]["world_path"])

    def http(self) -> httpx.Client:
        if self._http is None:
            app = create_sim_app(lambda wid: World(self.world_path(wid)))
            self._http = TestClient(app, base_url="http://testserver")
        return self._http

    def create_from_scenario(self, family: str, variant: str, seed: int, provider: str = "deterministic",
                             auto_approve: bool = False, faults: dict[str, Any] | None = None) -> str:
        incident_id = "inc_" + uuid.uuid4().hex[:10]
        run_dir = runs_dir() / incident_id
        inst = REGISTRY[family].setup(run_dir, random.Random(seed), variant)
        prov = make_provider(provider)
        data = {
            "source": "scenario", "ticket": inst.ticket, "contract": inst.contract,
            "world_path": str(inst.world_path), "repo_dir": str(inst.repo_dir), "run_dir": str(run_dir),
            "auto_approve": auto_approve, "faults": faults or {},
            "trace": [], "feedback": [], "hypotheses": [], "diagnosis": None, "patch": None,
            "reproduction": None, "attempts": [], "verification": {}, "done_steps": [],
            "provider_state": {}, "usage": {}, "repro_retries": 0, "approval": None, "report": None,
        }
        self.store.create(incident_id, data, {"family": family, "variant": variant, "seed": seed, **inst.hidden},
                          mode=prov.mode, provider=prov.name)
        self.store.event(incident_id, "intake", "INTAKE", f"Incident created: {inst.ticket['title']}",
                         {"severity": inst.ticket.get("severity")})
        for name, value in (faults or {}).items():
            World(inst.world_path).set_fault(name, value)
            self.store.event(incident_id, "intake", "FAULT_INJECTED", f"Fault injection enabled: {name}")
        return incident_id

    # ------------------------------------------------------------ driver
    def approve(self, incident_id: str, approver: str) -> None:
        inc = self.store.get(incident_id)
        if not inc or inc["phase"] != "awaiting_approval":
            raise ValueError("incident is not awaiting approval")
        data = inc["data"]
        data["approval"] = {"approver": approver, "decision": "approved"}
        self.store.event(incident_id, "awaiting_approval", "HUMAN_APPROVAL", f"Patch approved by {approver}")
        self.store.save(incident_id, data, "promote", inc["outcome"])

    def reject(self, incident_id: str, approver: str, reason: str) -> None:
        inc = self.store.get(incident_id)
        if not inc or inc["phase"] != "awaiting_approval":
            raise ValueError("incident is not awaiting approval")
        data = inc["data"]
        data["approval"] = {"approver": approver, "decision": "rejected", "reason": reason}
        self.store.event(incident_id, "awaiting_approval", "HUMAN_REJECTION", f"Patch rejected by {approver}: {reason}")
        self.store.save(incident_id, data, "report", "DIAGNOSED")

    def run(self, incident_id: str, provider: Provider | None = None, max_steps: int | None = None) -> dict[str, Any]:
        """Advance the incident until it finishes, needs approval, or max_steps tool calls ran."""
        inc = self.store.get(incident_id)
        if inc is None:
            raise KeyError(incident_id)
        prov = provider or make_provider(inc["provider"])
        prov.load_state(inc["data"].get("provider_state") or {})
        r = _Run(self, incident_id, inc, prov, max_steps)
        r.loop()
        return self.store.get(incident_id)


class _Run:
    def __init__(self, svc: IncidentService, iid: str, inc: dict[str, Any], prov: Provider, max_steps: int | None):
        self.svc, self.iid, self.prov = svc, iid, prov
        self.data = inc["data"]
        self.phase = inc["phase"]
        self.outcome = inc["outcome"]
        self.steps_left = max_steps
        self.run_dir = Path(self.data["run_dir"])
        self.repo = Path(self.data["repo_dir"])
        self.world = World(self.data["world_path"])
        self.ctx = ToolContext(incident=self.data["ticket"], repo_dir=self.repo,
                               sim=SimClient(svc.http(), iid), scratch_dir=self.run_dir,
                               hypotheses=self.data["hypotheses"])

    # ---------------------------------------------------------------- utils
    def ev(self, kind: str, summary: str, payload: Any = None) -> None:
        self.svc.store.event(self.iid, self.phase, kind, summary, payload)

    def save(self) -> None:
        self.data["hypotheses"] = self.ctx.hypotheses
        self.data["provider_state"] = self.prov.state()
        self.data["usage"] = self.prov.usage()
        self.svc.store.save(self.iid, self.data, self.phase, self.outcome)

    def goto(self, phase: str, outcome: str | None = None) -> None:
        self.phase = phase
        if outcome:
            self.outcome = outcome
        self.save()

    # ---------------------------------------------------------------- loop
    def loop(self) -> None:
        handlers = {
            "intake": self.intake, "investigate": self.agent_phase, "reproduce": self.reproduce,
            "patch": self.agent_phase, "promote": self.promote, "verify_live": self.verify_live,
            "report": self.report,
        }
        while self.phase in handlers:
            if self.steps_left is not None and self.steps_left <= 0:
                self.ev("CHECKPOINT", "Run paused; state persisted for resume")
                self.save()
                return
            try:
                handlers[self.phase]()
            except ProviderError as exc:
                self.ev("PROVIDER_ERROR", str(exc))
                self.goto("report", "ESCALATED" if self.data.get("diagnosis") is None else "DIAGNOSED")
            except Exception as exc:  # unexpected: never leave an incident in a half state
                self.ev("ORCHESTRATOR_ERROR", f"{type(exc).__name__}: {exc}")
                self.goto("report", "FAILED")
            if self.phase == "awaiting_approval" and self.data.get("auto_approve"):
                self.data["approval"] = {"approver": "policy:auto_approve (evaluation mode)", "decision": "approved"}
                self.ev("HUMAN_APPROVAL", "Auto-approved by evaluation policy (not a human)")
                self.goto("promote")

    def intake(self) -> None:
        self.ev("PARSE_EVIDENCE", "Ticket treated as untrusted evidence; investigation started",
                {"provider": self.prov.name, "mode": self.prov.mode})
        self.goto("investigate")

    # ------------------------------------------------------- agent phases
    def agent_phase(self) -> None:
        phase = self.phase
        view = AgentView(phase=phase, incident=self.data["ticket"], trace=self.data["trace"],
                         feedback=self.data["feedback"], diagnosis=self.data["diagnosis"])
        if len(self.data["trace"]) >= MAX_TOOL_CALLS:
            self.ev("BUDGET_EXHAUSTED", f"Tool-call budget of {MAX_TOOL_CALLS} exhausted")
            self.goto("report", "DIAGNOSED" if self.data["diagnosis"] else "ESCALATED")
            return
        actions = self.prov.next_actions(view)
        results = []
        for action in actions:
            outcome = execute(self.ctx, phase, action.tool, action.args)
            step = {"n": len(self.data["trace"]) + 1, "phase": phase, "tool": action.tool, "args": action.args,
                    "rationale": action.rationale, "ok": outcome.ok, "output": outcome.output}
            self.data["trace"].append(step)
            kind = "TOOL_CALL" if outcome.ok else "TOOL_DENIED"
            self.ev(kind, f"{action.tool}({_short(action.args)})", {"rationale": action.rationale,
                                                                       "ok": outcome.ok})
            results.append((action, outcome))
            if self.steps_left is not None:
                self.steps_left -= 1
            if outcome.terminal:
                self.terminal(action.tool, outcome.args or {})
                break
        self.prov.observe(results)
        self.save()

    def terminal(self, tool: str, args: dict[str, Any]) -> None:
        if tool == "submit_diagnosis":
            self.data["diagnosis"] = args
            self.ev("LOCALIZE_ROOT_CAUSE", args["root_cause"][:300], args)
            self.goto("reproduce", "DIAGNOSED")
        elif tool == "declare_indeterminate":
            self.ev("INDETERMINATE", args["reason"])
            self.goto("report", "INDETERMINATE")
        elif tool == "escalate":
            self.ev("ESCALATED", args["reason"])
            self.goto("report", "DIAGNOSED" if self.data["diagnosis"] else "ESCALATED")
        elif tool == "propose_patch":
            self.handle_patch(args)
        elif tool == "report_no_action_needed":
            self.handle_no_action(args)

    def _unannounced_keys(self, edits: list[dict[str, Any]]) -> list[str]:
        """Key ids a patch would newly trust that billing's own logs never announced for that tenant."""
        out: list[str] = []
        for e in edits:
            if e.get("op") != "json_set" or (e.get("key_path") or [None])[0] != "accepted_signing_keys":
                continue
            cfg_path = self.repo / e["path"]
            current = set(json.loads(cfg_path.read_text(encoding="utf-8")).get("accepted_signing_keys", [])
                          if cfg_path.is_file() else [])
            tenant = Path(e["path"]).stem
            announced = {json.loads(r["context"]).get("new_key_id") for r in self.world.query(
                "SELECT context FROM logs WHERE service='billing' AND message='webhook signing key rotated'")
                if json.loads(r["context"]).get("tenant") == tenant}
            out += [k for k in e.get("value") or [] if k not in current and k not in announced]
        return out

    def handle_no_action(self, args: dict[str, Any]) -> None:
        # The agent's claim is only accepted if the independent verifier sees the contract already met.
        result = verify(self.world.db_path, self.data["contract"])
        self.ev("VERIFY_BUSINESS_OUTCOME", f"Agent reports no action needed; independent verification: "
                                           f"{result.outcome}", result.to_dict())
        self.data["verification"] = result.to_dict()
        if result.outcome == "PASS":
            self.goto("report", "NO_ACTION_NEEDED")
        elif result.outcome == "INDETERMINATE":
            self.goto("report", "INDETERMINATE")
        elif self.data.get("no_action_rejected"):
            self.ev("ESCALATED", "No-action claim contradicted by the verifier twice")
            self.goto("report", "ESCALATED")
        else:
            self.data["no_action_rejected"] = True
            failed = [a["name"] for a in result.to_dict()["assertions"] if not a["passed"]]
            self.data["feedback"].append(f"report_no_action_needed rejected: independent verification FAILED "
                                         f"({', '.join(failed)}); the business outcome is not correct yet")

    # ------------------------------------------------------- reproduction
    def reproduce(self) -> None:
        contract = self.data["contract"]
        d = self.data["diagnosis"]
        if d.get("replay_event_id") != contract["event_id"]:
            self.ev("NOTE", f"Agent nominated event {d.get('replay_event_id')}; the verifier contract uses "
                            f"{contract['event_id']} from the billing ledger")
        repro = self.run_dir / "repro"
        repo = sandbox.copy_repo(self.repo, repro / "repo")
        w = self.world.clone_to(repro / "world.db")
        replay = sandbox.replay_event(repo, w, contract["event_id"])
        result = verify(w.db_path, contract)
        self.data["reproduction"] = {"replay": replay, "verification": result.to_dict()}
        if result.outcome == "FAIL":
            self.ev("REPRODUCE_FAILURE", "Failure reproduced in isolated copy: replaying the original event "
                                         "with unpatched code leaves the business contract unmet",
                    result.to_dict())
            self.goto("patch")
        elif result.outcome == "INDETERMINATE":
            self.ev("INDETERMINATE", f"Reproduction inconclusive: {result.reason}")
            self.goto("report", "INDETERMINATE")
        else:
            self.data["repro_retries"] += 1
            msg = "reproduction did not show the failure: replaying the event with current code satisfies the contract"
            self.ev("REPRODUCTION_MISMATCH", msg)
            if self.data["repro_retries"] > MAX_REPRO_RETRIES:
                self.goto("report", "ESCALATED")
            else:
                self.data["feedback"].append(msg)
                self.data["diagnosis"] = None
                self.goto("investigate")

    # ------------------------------------------------------- patch testing
    def handle_patch(self, args: dict[str, Any]) -> None:
        n = len(self.data["attempts"]) + 1
        edits = args["edits"]
        attempt: dict[str, Any] = {"n": n, "edits": edits, "rationale": args.get("rationale", "")}
        self.data["attempts"].append(attempt)
        self.ev("PROPOSE_PATCH", f"Patch attempt {n}: {len(edits)} edit(s)", args)

        review = review_patch(self.repo, edits)
        attempt["review"] = review.__dict__
        if not review.allowed:
            self.ev("SECURITY_CHECK", f"Patch rejected by policy: {'; '.join(review.findings)}", review.__dict__)
            return self._patch_failed(f"patch rejected by policy: {'; '.join(review.findings)}")
        unannounced = self._unannounced_keys(edits)
        if unannounced:
            # Trust comes from the authoritative system, never from the event or the agent: a forged event could
            # carry any key id.
            msg = (f"refusing to trust signing key(s) {unannounced}: billing never announced them "
                   "(no 'webhook signing key rotated' log for this tenant)")
            self.ev("SECURITY_CHECK", f"Patch rejected: {msg}")
            return self._patch_failed(f"patch rejected by policy: {msg}")
        self.ev("SECURITY_CHECK", f"Policy review passed (risk={review.risk})", review.__dict__)

        if not sandbox.test_runner_available():
            # Infrastructure fault, not a bad patch: stop without spending patch attempts or claiming a fix.
            self.ev("ESCALATED", "Sandbox test runner (pytest) is not installed; the patch cannot be tested")
            return self.goto("report", "DIAGNOSED")

        box = self.run_dir / "sandbox" / f"attempt_{n}"
        repo = sandbox.copy_repo(self.repo, box / "repo")
        try:
            attempt["diff"] = sandbox.apply_edits(repo, edits)
        except PolicyViolation as exc:
            return self._patch_failed(f"patch could not be applied: {exc}")
        self.ev("SANDBOX_EXECUTION", f"Patch applied in isolated workspace attempt_{n}", {"diff": attempt["diff"]})

        # Regression test: generated from the captured event + billing ledger, never from the agent.
        event = self.world.get_event(self.data["contract"]["event_id"])
        expected = verify(self.world.db_path, self.data["contract"])
        exp_plan = next((a.expected for a in expected.assertions if a.name == "entitlement_matches_paid_plan"), None)
        if exp_plan is None:
            return self._patch_failed("could not derive expected plan from billing ledger")
        reg_files = sandbox.write_regression_test(repo, self.iid, event, exp_plan)
        unpatched = sandbox.copy_repo(self.repo, box / "unpatched")
        sandbox.write_regression_test(unpatched, self.iid, event, exp_plan)
        before = sandbox.run_tests(unpatched, [reg_files[0]])
        tests = sandbox.run_tests(repo)
        attempt["tests"] = {"suite": tests, "regression_on_unpatched": before}
        self.ev("TEST_PATCH", f"Test suite {'passed' if tests['passed'] else 'FAILED'}; regression test "
                              f"{'fails' if not before['passed'] else 'PASSES'} on unpatched code",
                {"suite": tests["output"][-800:], "unpatched": before["output"][-800:]})
        if not tests["passed"]:
            return self._patch_failed("patched test suite failed:\n" + tests["output"][-1200:])
        if before["passed"]:
            return self._patch_failed("generated regression test does not fail on unpatched code")

        w = self.world.clone_to(box / "world.db")
        replay = sandbox.replay_event(repo, w, self.data["contract"]["event_id"])
        result = verify(w.db_path, self.data["contract"])
        attempt["sandbox_verification"] = {"replay": replay, "verification": result.to_dict()}
        self.ev("VERIFY_BUSINESS_OUTCOME", f"Sandbox replay verification: {result.outcome}", result.to_dict())
        if result.outcome != "PASS":
            failed = [a["name"] for a in result.to_dict()["assertions"] if not a["passed"]]
            return self._patch_failed(
                f"sandbox verification {result.outcome}: failed assertions {failed} {result.reason}")

        attempt["accepted"] = True
        attempt["regression_files"] = reg_files
        attempt["sandbox_repo"] = str(repo)
        self.data["patch"] = attempt
        self.ev("GENERATE_REGRESSION", f"Regression test {reg_files[0]} fails before / passes after the patch")
        self.goto("awaiting_approval", "PATCH_TESTED_NOT_VERIFIED")

    def _patch_failed(self, reason: str) -> None:
        self.data["feedback"].append(reason)
        self.ev("PATCH_REJECTED", reason[:400])
        if len(self.data["attempts"]) >= MAX_PATCH_ATTEMPTS:
            self.goto("report", "DIAGNOSED")
        else:
            self.save()

    # ------------------------------------------------------- promotion
    def promote(self) -> None:
        if (self.data.get("approval") or {}).get("decision") != "approved":
            raise PolicyViolation("promotion requires approval")
        if "promote" not in self.data["done_steps"]:
            patch = self.data["patch"]
            sandbox.apply_edits(self.repo, patch["edits"])  # idempotent edits
            src = Path(patch["sandbox_repo"])
            for rel in patch["regression_files"]:
                (self.repo / rel).write_bytes((src / rel).read_bytes())
            self.data["done_steps"].append("promote_applied")
            self.save()
            # Replay redelivers the stored event only; billing is never re-charged.
            replay = sandbox.replay_event(self.repo, self.world, self.data["contract"]["event_id"])
            self.data["done_steps"].append("promote")
            self.ev("PROMOTE", "Approved patch applied to the incident environment; original event redelivered",
                    replay)
        self.goto("verify_live")

    def verify_live(self) -> None:
        result = verify(self.world.db_path, self.data["contract"])
        self.data["verification"] = result.to_dict()
        self.ev("VERIFY_BUSINESS_OUTCOME", f"Independent verification of environment: {result.outcome}",
                result.to_dict())
        outcome = {"PASS": "VERIFIED", "FAIL": "PATCH_TESTED_NOT_VERIFIED"}.get(result.outcome, "INDETERMINATE")
        self.goto("report", outcome)

    def report(self) -> None:
        from .report import build_report  # noqa: PLC0415

        self.data["report"] = build_report(self.iid, self.data, self.outcome, self.prov)
        self.ev("REPORT", f"Final outcome: {self.outcome}")
        self.goto("done")


def _short(args: dict[str, Any]) -> str:
    s = ", ".join(f"{k}={v!r}" for k, v in args.items())
    return s if len(s) < 120 else s[:117] + "..."
