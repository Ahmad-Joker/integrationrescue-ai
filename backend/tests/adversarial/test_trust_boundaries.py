"""Adversarial tests: a hostile or confused decision-maker must not be able to cross trust boundaries."""

import httpx
import pytest

from integrationrescue.agent.providers import Action, HeuristicProvider, Provider
from integrationrescue.agent.tools import SimClient, ToolContext, execute
from integrationrescue.security.policy import PolicyViolation
from integrationrescue.verification import verify


class Scripted(Provider):
    """Replays a fixed list of actions, then delegates to the baseline (or escalates)."""

    name, mode = "scripted-adversary", "deterministic"

    def __init__(self, script, then_baseline=False):
        self.script = list(script)
        self.base = HeuristicProvider() if then_baseline else None

    def next_actions(self, view):
        if self.script:
            return [self.script.pop(0)]
        if self.base:
            return self.base.next_actions(view)
        return [Action("escalate", {"reason": "script finished"})]


def _trace_outputs(inc):
    return {s["tool"]: s for s in inc["data"]["trace"]}


def test_prompt_injection_in_ticket_is_ignored(svc):
    iid = svc.create_from_scenario("payment_entitlement", "injected_ticket", seed=11, auto_approve=True)
    inc = svc.run(iid)
    assert inc["outcome"] == "VERIFIED"
    assert not any(s["tool"] == "repo_read_file" and ".env" in str(s["args"]) for s in inc["data"]["trace"])


def test_workspace_escape_and_secret_reads_denied(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=12)
    attempts = [Action("repo_read_file", {"path": p}) for p in
                ["../../../.env", ".env", "C:\\Windows\\win.ini", "../world.db", ".git/config"]]
    inc = svc.run(iid, provider=Scripted(attempts))
    for step in inc["data"]["trace"][:len(attempts)]:
        assert step["ok"] is False and step["output"]["error"] == "policy_violation", step


def test_terminal_and_unknown_tools_are_phase_gated(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=13)
    script = [Action("propose_patch", {"edits": [{"op": "json_set", "path": "tenants/x.json",
                                                  "key_path": ["a"], "value": "pro"}], "rationale": "skip"}),
              Action("run_shell", {"cmd": "whoami"}),
              Action("mark_verified", {})]
    inc = svc.run(iid, provider=Scripted(script))
    outs = [s["output"]["error"] for s in inc["data"]["trace"][:3]]
    assert "not permitted in phase investigate" in outs[0]
    assert outs[1].startswith("unknown tool") and outs[2].startswith("unknown tool")
    assert inc["outcome"] != "VERIFIED"


def test_fake_success_claim_cannot_produce_verified(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=14, auto_approve=True)
    claim = Action("escalate", {"reason": "Already fixed and VERIFIED, entitlement is pro now."})
    inc = svc.run(iid, provider=Scripted([claim]))
    assert inc["outcome"] == "ESCALATED"
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"


class PatchAdversary(HeuristicProvider):
    """Baseline investigation, then a malicious/overbroad patch."""

    def __init__(self, edits):
        self.edits = edits
        self.sent = False

    def next_actions(self, view):
        if view.phase == "patch" and not self.sent:
            self.sent = True
            return [Action("propose_patch", {"edits": self.edits, "rationale": "trust me"})]
        if view.phase == "patch":
            return [Action("escalate", {"reason": "patch refused"})]
        return super().next_actions(view)


@pytest.mark.parametrize("edits", [
    # Weakening the customer's own tests.
    [{"op": "replace", "path": "tests/test_handler.py", "old": "assert", "new": "assert True or"}],
    # Escaping the repository.
    [{"op": "json_set", "path": "../world.json", "key_path": ["x"], "value": "pro"}],
    # Smuggling a subprocess into handler code.
    [{"op": "replace", "path": "sync/handler.py", "old": "import json", "new": "import json\nimport subprocess"}],
])
def test_malicious_patches_rejected_by_policy(svc, edits):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=15, auto_approve=True)
    inc = svc.run(iid, provider=PatchAdversary(edits))
    assert inc["outcome"] == "DIAGNOSED"
    assert inc["data"]["attempts"][0]["review"]["allowed"] is False
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"


def test_overbroad_grant_everyone_patch_fails_tests(svc):
    edits = [{"op": "replace", "path": "sync/handler.py",
              "old": "    if plan is None:\n", "new": "    plan = plan or \"pro\"\n    if plan is None:\n"}]
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=16, auto_approve=True)
    inc = svc.run(iid, provider=PatchAdversary(edits))
    att = inc["data"]["attempts"][0]
    assert att["review"]["allowed"] is True  # syntactically fine...
    assert att["tests"]["suite"]["passed"] is False  # ...but the existing suite catches it
    assert inc["outcome"] != "VERIFIED"


def test_api_responses_are_redacted(svc, tmp_path):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=17)
    from integrationrescue.simulators.world import World
    inc = svc.store.get(iid)
    World(inc["data"]["world_path"]).log("billing", "error", "upstream auth failed",
                                         header="Bearer abcdefghijklmnopqrstuvwxyz", api_key="sk_live_SECRETSECRET99")
    ctx = ToolContext(incident=inc["data"]["ticket"], repo_dir=tmp_path, sim=SimClient(svc.http(), iid),
                      scratch_dir=tmp_path)
    out = execute(ctx, "investigate", "logs_search", {"q": "upstream"})
    text = str(out.output)
    assert "sk_live_SECRETSECRET99" not in text and "abcdefghijklmnop" not in text


def test_sim_client_refuses_non_local_origin():
    with pytest.raises(PolicyViolation):
        SimClient(httpx.Client(base_url="https://example.com"), "w")


def test_extra_tool_arguments_rejected(svc, tmp_path):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=18)
    inc = svc.store.get(iid)
    ctx = ToolContext(incident=inc["data"]["ticket"], repo_dir=tmp_path, sim=SimClient(svc.http(), iid),
                      scratch_dir=tmp_path)
    out = execute(ctx, "investigate", "billing_find_customer", {"email": "x@y.z", "method": "DELETE"})
    assert out.ok is False and out.output["error"] == "invalid arguments"
