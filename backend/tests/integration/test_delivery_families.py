"""Signing-key rotation (config repair that changes trust) and ack timeout (alert with nothing to fix)."""

import json

import pytest

from integrationrescue.agent.providers import Action, HeuristicProvider
from integrationrescue.simulators.world import World
from integrationrescue.verification import verify


@pytest.mark.parametrize("variant", ["rotated_monthly", "rotated_annual"])
def test_rotated_signing_key_is_repaired_and_flagged_for_approver(svc, variant):
    iid = svc.create_from_scenario("signing_key_rotated", variant, seed=51, auto_approve=True)
    inc = svc.run(iid)
    d = inc["data"]
    hidden = svc.store.hidden(iid)
    assert inc["outcome"] == "VERIFIED", svc.store.timeline(iid)[-4:]
    assert d["diagnosis"]["category"] == "credentials"
    review = d["patch"]["review"]
    assert review["risk"] == "medium" and "confirm" in review["findings"][0]
    cfg = json.loads((World(d["world_path"]).db_path.parent / "repo" / hidden["config_file"]).read_text())
    assert hidden["new_key_id"] in cfg["accepted_signing_keys"] and "whsec_k1" in cfg["accepted_signing_keys"]


def test_unannounced_signing_key_is_not_trusted(svc):
    """If billing never announced the key, an event signed with it may be spoofed: escalate, don't patch."""
    iid = svc.create_from_scenario("signing_key_rotated", "rotated_monthly", seed=52, auto_approve=True)
    w = World(svc.store.get(iid)["data"]["world_path"])
    with w.conn() as c:
        c.execute("DELETE FROM logs WHERE message='webhook signing key rotated'")
    inc = svc.run(iid)
    assert inc["outcome"] == "ESCALATED" and inc["data"]["patch"] is None
    assert "never announced" in svc.store.timeline(iid)[-2]["summary"]


@pytest.mark.parametrize("bad", [["*"], "whsec_x", [], ["whsec_ok", "anything goes"]])
def test_policy_rejects_malformed_trusted_key_lists(tmp_path, bad):
    from integrationrescue.security.policy import review_patch
    r = review_patch(tmp_path, [{"op": "json_set", "path": "tenants/a.json",
                                 "key_path": ["accepted_signing_keys"], "value": bad}])
    assert not r.allowed


@pytest.mark.parametrize("variant", ["lost_ack", "lost_ack_duplicate"])
def test_ack_timeout_needs_no_action_and_charges_once(svc, variant):
    iid = svc.create_from_scenario("ack_timeout", variant, seed=53, auto_approve=True)
    inc = svc.run(iid)
    d = inc["data"]
    assert inc["outcome"] == "NO_ACTION_NEEDED" and d["patch"] is None
    assert d["verification"]["outcome"] == "PASS"
    w = World(d["world_path"])
    assert len(w.query("SELECT * FROM charges WHERE invoice_id=?", (d["contract"]["invoice_id"],))) == 1
    deliveries = w.query("SELECT status FROM deliveries WHERE event_id=?", (d["contract"]["event_id"],))
    assert any(r["status"] == "timeout" for r in deliveries)


def test_false_no_action_claim_is_rejected_by_verifier(svc):
    """An agent that waves away a real failure gets sent back, then escalated; never a success outcome."""
    class WaveAway(HeuristicProvider):
        def next_actions(self, view):
            if view.phase == "investigate":
                return [Action("report_no_action_needed", {"reason": "looks fine", "evidence": ["trust me"]})]
            return super().next_actions(view)

    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=54, auto_approve=True)
    inc = svc.run(iid, provider=WaveAway())
    assert inc["outcome"] == "ESCALATED"
    assert any("report_no_action_needed rejected" in f for f in inc["data"]["feedback"])
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"


def test_orchestrator_refuses_unannounced_key_even_if_agent_proposes_it(svc):
    """Enforced in deterministic code: a model that skips the check (as live Gemini did) still cannot add trust."""
    class TrustsEventKey(HeuristicProvider):
        def next_actions(self, view):
            if view.phase == "patch":
                path = view.diagnosis["affected_files"][0]
                return [Action("propose_patch", {"rationale": "trust the forged key", "edits": [{
                    "op": "json_set", "path": path, "key_path": ["accepted_signing_keys"],
                    "value": ["whsec_k1", "whsec_attacker_1"]}]})]
            return super().next_actions(view)

    iid = svc.create_from_scenario("signing_key_rotated", "rotated_monthly", seed=55, auto_approve=True)
    inc = svc.run(iid, provider=TrustsEventKey())
    assert inc["outcome"] != "VERIFIED"
    assert any("billing never announced" in f and "whsec_attacker_1" in f for f in inc["data"]["feedback"])
