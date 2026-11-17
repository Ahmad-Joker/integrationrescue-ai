"""Print per-run, per-family figures from the committed evaluation results (evidence/eval/*.json).

    python scripts/summarize_evidence.py

Every number in competition/TECHNICAL_EVIDENCE.md can be re-derived with this script. Runs that hit model-service
errors (quota, overload) are listed separately and excluded from scores, exactly as the harness does.
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    for path in sorted((ROOT / "evidence" / "eval").glob("eval_*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        rows = d["rows"]
        scored = [r for r in rows if not r.get("infra_error")]
        live = d["provider"] not in ("deterministic", "heuristic-baseline")
        print(f"\n== {path.name} | {'LIVE ' + d['provider'] if live else 'DETERMINISTIC BASELINE'} | "
              f"{d['created_at']} | seeds {d['seeds']}")
        print(f"   runs {len(rows)}, scored {len(scored)}, infra errors {len(rows) - len(scored)}")
        fams: dict[str, dict] = {}
        for r in scored:
            f = fams.setdefault(r["family"], {"runs": 0, "expected": 0, "diagnosis": 0, "outcomes": {}})
            f["runs"] += 1
            f["expected"] += r["outcome"] == r["expected_outcome"]
            f["diagnosis"] += bool(r["correct_diagnosis"])
            f["outcomes"][r["outcome"]] = f["outcomes"].get(r["outcome"], 0) + 1
        for name, f in fams.items():
            print(f"   {name:<20} runs {f['runs']:>2}  expected {f['expected']:>2}  diagnosis {f['diagnosis']:>2}  "
                  f"{f['outcomes']}")
        print(f"   expected outcome {sum(f['expected'] for f in fams.values())}/{len(scored)} | correct diagnosis "
              f"{sum(f['diagnosis'] for f in fams.values())}/{len(scored)} | false success claims "
              f"{sum(bool(r['false_verified']) for r in scored)} | duplicate charges "
              f"{sum(bool(r['duplicate_charge']) for r in scored)} | unnecessary patches "
              f"{sum(bool(r.get('unnecessary_patch')) for r in scored)} | denied tool calls "
              f"{sum(r.get('denied_tool_calls', 0) for r in scored)}")
        if scored:
            print(f"   tool calls mean {st.mean(r['tool_calls'] for r in scored):.1f} | duration median "
                  f"{st.median(r['duration_s'] for r in scored):.1f} s")
        usage = [r["usage"] for r in scored if r.get("usage", {}).get("calls")]
        if usage:
            print(f"   model calls mean {st.mean(u['calls'] for u in usage):.1f} "
                  f"(range {min(u['calls'] for u in usage)}-{max(u['calls'] for u in usage)}) | input tokens mean "
                  f"{st.mean(u.get('input', 0) for u in usage):,.0f} | output tokens mean "
                  f"{st.mean(u.get('output', 0) for u in usage):,.0f}")
        for r in rows:
            if r.get("infra_error"):
                reason = " ".join(r["infra_error"].split())[:60]
                print(f"   not scored: {r['family']}/{r['variant']} seed {r['seed']}: {reason}")


if __name__ == "__main__":
    main()
