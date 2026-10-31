"""Repeatable evaluation harness. Every number it reports comes from an actual recorded run.

Usage: python -m integrationrescue.evaluation [--provider deterministic|claude] [--seeds 1 2 3] [--heldout]
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from typing import Any

from .agent.orchestrator import IncidentService
from .paths import var_dir
from .scenarios import REGISTRY
from .simulators.world import World
from .verification import verify


def _score(svc: IncidentService, iid: str, duration: float) -> dict[str, Any]:
    inc = svc.store.get(iid)
    hidden = svc.store.hidden(iid)
    d = inc["data"]
    diag = d.get("diagnosis") or {}
    expected_outcome = hidden.get("expected_outcome")
    expected_file = hidden.get("config_file")
    if expected_outcome == "INDETERMINATE":
        diagnosed_ok = inc["outcome"] == "INDETERMINATE"
    else:
        diagnosed_ok = bool(diag) and expected_file in (diag.get("affected_files") or [])
    recheck = verify(d["world_path"], d["contract"]).outcome
    w = World(d["world_path"])
    charges = len(w.query("SELECT * FROM charges WHERE invoice_id=? AND status='succeeded'",
                          (d["contract"]["invoice_id"],)))
    return {
        "incident_id": iid, "family": hidden["family"], "variant": hidden["variant"], "seed": hidden["seed"],
        "provider": inc["provider"], "mode": inc["mode"], "outcome": inc["outcome"],
        "expected_outcome": expected_outcome or "VERIFIED",
        "correct_diagnosis": diagnosed_ok,
        "reproduced": (d.get("reproduction") or {}).get("verification", {}).get("outcome") == "FAIL",
        "patch_accepted": bool(d.get("patch")),
        "verified": inc["outcome"] == "VERIFIED",
        "false_verified": inc["outcome"] == "VERIFIED" and (recheck != "PASS" or expected_outcome == "INDETERMINATE"),
        "duplicate_charge": charges > 1,
        "tool_calls": len(d.get("trace", [])),
        "denied_tool_calls": sum(1 for s in d.get("trace", []) if not s["ok"]),
        "patch_attempts": len(d.get("attempts", [])),
        "duration_s": round(duration, 2),
        "usage": d.get("usage", {}),
    }


def run_suite(provider: str = "deterministic", seeds: list[int] | None = None, heldout: bool = True,
              families: list[str] | None = None) -> dict[str, Any]:
    svc = IncidentService()
    seeds = seeds or [101, 202]
    rows = []
    for fam in REGISTRY.values():
        if families and fam.name not in families:
            continue
        variants = [(v, False) for v in fam.variants] + ([(v, True) for v in fam.heldout_variants] if heldout else [])
        for variant, is_heldout in variants:
            for seed in seeds:
                t0 = time.perf_counter()
                iid = svc.create_from_scenario(fam.name, variant, seed=seed, provider=provider, auto_approve=True)
                svc.run(iid)
                row = _score(svc, iid, time.perf_counter() - t0)
                row["heldout"] = is_heldout
                rows.append(row)
    n = len(rows) or 1
    summary = {
        "runs": len(rows),
        "correct_diagnosis_rate": round(sum(r["correct_diagnosis"] for r in rows) / n, 3),
        "verified_rate": round(sum(r["verified"] for r in rows) / n, 3),
        "outcome_matches_expected_rate": round(sum(r["outcome"] == r["expected_outcome"] for r in rows) / n, 3),
        "false_verified": sum(r["false_verified"] for r in rows),
        "duplicate_charges": sum(r["duplicate_charge"] for r in rows),
        "mean_tool_calls": round(sum(r["tool_calls"] for r in rows) / n, 1),
        "mean_duration_s": round(sum(r["duration_s"] for r in rows) / n, 2),
        "by_family": {},
    }
    for r in rows:
        f = summary["by_family"].setdefault(r["family"], {"runs": 0, "verified": 0, "correct_diagnosis": 0,
                                                          "expected_outcome": 0})
        f["runs"] += 1
        f["verified"] += r["verified"]
        f["correct_diagnosis"] += r["correct_diagnosis"]
        f["expected_outcome"] += r["outcome"] == r["expected_outcome"]
    result = {"created_at": datetime.now(UTC).isoformat(timespec="seconds"), "provider": provider,
              "seeds": seeds, "summary": summary, "rows": rows}
    out = var_dir() / "eval"
    out.mkdir(exist_ok=True)
    path = out / f"eval_{provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    result["path"] = str(path)
    return result


def latest_results() -> list[dict[str, Any]]:
    out = var_dir() / "eval"
    if not out.exists():
        return []
    files = sorted(out.glob("eval_*.json"), reverse=True)[:20]
    return [json.loads(p.read_text(encoding="utf-8")) | {"path": p.name} for p in files]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deterministic")
    ap.add_argument("--seeds", type=int, nargs="*", default=[101, 202])
    ap.add_argument("--no-heldout", action="store_true")
    ap.add_argument("--family", action="append")
    a = ap.parse_args()
    res = run_suite(a.provider, a.seeds, not a.no_heldout, a.family)
    print(json.dumps(res["summary"], indent=2))
    for r in res["rows"]:
        print(f"{r['family']:<20} {r['variant']:<16} seed={r['seed']:<4} heldout={str(r['heldout']):<5} "
              f"outcome={r['outcome']:<26} expected={r['expected_outcome']:<14} diag_ok={r['correct_diagnosis']}")
    print("saved:", res["path"])


if __name__ == "__main__":
    main()
