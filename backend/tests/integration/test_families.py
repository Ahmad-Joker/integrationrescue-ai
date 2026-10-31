from integrationrescue.verification import verify


def test_schema_drift_is_diagnosed_but_baseline_does_not_claim_repair(svc):
    iid = svc.create_from_scenario("schema_drift", "monthly_line", seed=21, auto_approve=True)
    inc = svc.run(iid)
    d = inc["data"]
    assert d["diagnosis"]["category"] == "code_defect"
    assert d["reproduction"]["verification"]["outcome"] == "FAIL"
    assert inc["outcome"] == "DIAGNOSED"  # baseline escalates code fixes instead of guessing


def test_schema_drift_code_patch_verifies_when_proposed(svc):
    """A correct code-level repair (as a capable model would propose) passes the full pipeline."""
    from integrationrescue.agent.providers import Action, HeuristicProvider

    class CodeFixer(HeuristicProvider):
        def next_actions(self, view):
            if view.phase == "patch":
                return [Action("propose_patch", {"rationale": "accept both line-item shapes", "edits": [{
                    "op": "replace", "path": "sync/handler.py",
                    "old": "    plan = resolve_plan(line[\"price_id\"], tenant_cfg)\n",
                    "new": "    price_id = line.get(\"price_id\") or line.get(\"price\", {}).get(\"id\")\n"
                           "    line = {**line, \"price_id\": price_id}\n"
                           "    plan = resolve_plan(price_id, tenant_cfg)\n"}]})]
            return super().next_actions(view)

    iid = svc.create_from_scenario("schema_drift", "annual_line", seed=22, auto_approve=True)
    inc = svc.run(iid, provider=CodeFixer())
    assert inc["outcome"] == "VERIFIED", svc.store.timeline(iid)[-4:]
    assert inc["data"]["patch"]["review"]["risk"] == "medium"
    assert verify(inc["data"]["world_path"], inc["data"]["contract"]).outcome == "PASS"


def test_state_unavailable_is_indeterminate(svc):
    iid = svc.create_from_scenario("state_unavailable", "ledger_down", seed=23, auto_approve=True)
    inc = svc.run(iid)
    assert inc["outcome"] == "INDETERMINATE"
    assert inc["data"]["patch"] is None
