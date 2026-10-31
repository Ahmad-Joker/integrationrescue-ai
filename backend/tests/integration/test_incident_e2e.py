import pytest

from integrationrescue.scenarios import REGISTRY
from integrationrescue.simulators.world import World
from integrationrescue.verification import verify

FAMILY = REGISTRY["payment_entitlement"]


@pytest.mark.parametrize("variant", FAMILY.variants + FAMILY.heldout_variants)
@pytest.mark.parametrize("seed", [1, 2])
def test_variant_is_verified_end_to_end(svc, variant, seed):
    iid = svc.create_from_scenario("payment_entitlement", variant, seed=seed, auto_approve=True)
    inc = svc.run(iid)
    assert inc["outcome"] == "VERIFIED", svc.store.timeline(iid)[-5:]
    d = inc["data"]
    # Independent re-check straight from the environment, plus exactly one charge.
    result = verify(d["world_path"], d["contract"])
    assert result.outcome == "PASS"
    w = World(d["world_path"])
    assert len(w.query("SELECT * FROM charges WHERE invoice_id=?", (d["contract"]["invoice_id"],))) == 1
    # Patch is scoped to the affected tenant config and a regression test was promoted.
    hidden = svc.store.hidden(iid)
    assert [e["path"] for e in d["patch"]["edits"]] == [hidden["config_file"]]
    assert d["patch"]["tests"]["regression_on_unpatched"]["passed"] is False
    assert all((w.db_path.parent / "repo" / f).exists() for f in d["patch"]["regression_files"])


def test_approval_gate_blocks_promotion(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=3)
    inc = svc.run(iid)
    assert inc["phase"] == "awaiting_approval"
    assert inc["outcome"] == "PATCH_TESTED_NOT_VERIFIED"
    # Live environment untouched before approval.
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"
    svc.approve(iid, "reviewer@example")
    inc = svc.run(iid)
    assert inc["outcome"] == "VERIFIED"


def test_rejection_leaves_environment_unchanged(svc):
    iid = svc.create_from_scenario("payment_entitlement", "case_mismatch", seed=4)
    svc.run(iid)
    svc.reject(iid, "reviewer@example", "prefer code fix")
    inc = svc.run(iid)
    assert inc["outcome"] == "DIAGNOSED"
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"


def test_resumes_after_interruption_without_repeating_work(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=5, auto_approve=True)
    inc = svc.run(iid, max_steps=4)
    assert inc["phase"] == "investigate"
    calls_before = len(inc["data"]["trace"])
    inc = svc.run(iid)
    assert inc["outcome"] == "VERIFIED"
    tools = [s["tool"] for s in inc["data"]["trace"]]
    assert tools.count("get_incident") == 1  # no repeated steps after resume
    assert len(tools) > calls_before


def test_duplicate_webhook_fault_has_single_side_effect(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=6, auto_approve=True,
                                   faults={"duplicate_delivery": True})
    inc = svc.run(iid)
    assert inc["outcome"] == "VERIFIED"
    grant = [a for a in inc["data"]["verification"]["assertions"] if a["name"] == "entitlement_granted_once_for_event"]
    assert grant[0]["passed"]


def test_unavailable_ledger_is_indeterminate_not_verified(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=8, auto_approve=True,
                                   faults={"billing_ledger_unavailable": True})
    inc = svc.run(iid)
    assert inc["outcome"] == "INDETERMINATE"
    assert inc["data"]["patch"] is None


def test_report_written(svc):
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=9, auto_approve=True)
    inc = svc.run(iid)
    rep = inc["data"]["report"]
    assert rep["mode_label"].startswith("DETERMINISTIC")
    assert rep["verification"]["outcome"] == "PASS"
    from pathlib import Path
    assert "Independent verification" in (Path(inc["data"]["run_dir"]) / "report.md").read_text(encoding="utf-8")


def test_missing_test_runner_escalates_instead_of_blaming_patch(svc, monkeypatch):
    from integrationrescue.agent import sandbox
    monkeypatch.setattr(sandbox, "test_runner_available", lambda: False)
    iid = svc.create_from_scenario("payment_entitlement", "stale_price_id", seed=4, auto_approve=True)
    inc = svc.run(iid)
    assert inc["outcome"] == "DIAGNOSED"
    assert "patch" not in inc["data"] or inc["data"]["patch"] is None
    assert any("pytest" in e["summary"] for e in svc.store.timeline(iid) if e["kind"] == "ESCALATED")
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "FAIL"
