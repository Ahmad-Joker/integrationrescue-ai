"""The coding-agent comparison harness: no ground truth in the export, same verifier for scoring."""

import json

from integrationrescue import comparison
from integrationrescue.paths import var_dir


def _private(out):
    cid = (out / ".comparison_id").read_text(encoding="utf-8").strip()
    return json.loads((var_dir() / "compare" / cid / "meta.json").read_text(encoding="utf-8"))


def test_export_hides_ground_truth(tmp_path):
    out = comparison.export("payment_entitlement", "stale_price_id", 7, tmp_path / "x")
    blob = " ".join(p.read_text(encoding="utf-8", errors="ignore") for p in out.rglob("*") if p.is_file())
    assert "stale_price_id" not in blob and "tenant_price_mapping_missing" not in blob
    assert not (out / "evidence" / "meta.json").exists() and not (out / "evidence" / "faults.json").exists()
    assert "idempotency_key" not in (out / "evidence" / "charges.json").read_text(encoding="utf-8")
    assert (out / "TASK.md").is_file() and (out / "repo" / "tests").is_dir()


def test_scoring_unchanged_correct_and_cheating_repos(tmp_path):
    out = comparison.export("payment_entitlement", "stale_price_id", 7, tmp_path / "x")
    untouched = comparison.score(out)
    assert untouched["verdict"] == "NOT_VERIFIED" and untouched["changed_files"] == []

    hidden = _private(out)["hidden"]
    cfg_path = out / "repo" / hidden["config_file"]
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["price_plan_map"][hidden["paid_price"]] = "pro"
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    fixed = comparison.score(out)
    assert fixed["verdict"] == "VERIFIED" and fixed["tests_modified"] is False
    assert fixed["outside_allow_list"] == []

    test_file = out / "repo" / "tests" / "test_handler.py"
    test_file.write_text(test_file.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
    assert comparison.score(out)["tests_modified"] is True


def test_no_action_case_is_scored_as_such(tmp_path):
    out = comparison.export("ack_timeout", "lost_ack", 3, tmp_path / "y")
    r = comparison.score(out)
    assert r["verdict"] == "NO_ACTION_NEEDED" and r["expected_outcome"] == "NO_ACTION_NEEDED"
    assert r["unnecessary_change"] is False
