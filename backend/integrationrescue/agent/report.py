"""Evidence report generation (JSON for the UI, Markdown for humans)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .providers import Provider

LIMITATIONS = [
    "Environment is a local simulation with fictional data; no real SaaS connectors are used.",
    "Patches are limited to tenant configuration and handler files on an allow-list.",
]


def build_report(incident_id: str, data: dict[str, Any], outcome: str | None, prov: Provider) -> dict[str, Any]:
    d = data.get("diagnosis") or {}
    patch = data.get("patch") or {}
    ver = data.get("verification") or {}
    repro = data.get("reproduction") or {}
    report = {
        "incident_id": incident_id,
        "outcome": outcome,
        "mode": prov.mode,
        "provider": prov.name,
        "mode_label": "LIVE AI AGENT" if prov.mode == "live" else "DETERMINISTIC BASELINE (no LLM)",
        "summary": data["ticket"]["title"],
        "root_cause": d.get("root_cause"),
        "category": d.get("category"),
        "evidence": d.get("evidence", []),
        "hypotheses": data.get("hypotheses", []),
        "reproduction": repro,
        "patch": ({k: patch.get(k) for k in ("edits", "rationale", "diff", "review", "regression_files")}
                  if patch else None),
        "tests": patch.get("tests") if patch else None,
        "approval": data.get("approval"),
        "verification": ver,
        "tool_calls": len(data.get("trace", [])),
        "usage": prov.usage(),
        "limitations": LIMITATIONS + (["Outcome was not independently verified."] if outcome != "VERIFIED" else []),
    }
    Path(data["run_dir"], "report.md").write_text(to_markdown(report), encoding="utf-8")
    return report


def to_markdown(r: dict[str, Any]) -> str:
    lines = [f"# Incident report {r['incident_id']}", "",
             f"**Outcome:** {r['outcome']}  ", f"**Mode:** {r['mode_label']} ({r['provider']})  ",
             f"**Tool calls:** {r['tool_calls']}", "", "## Root cause", r.get("root_cause") or "_not established_", ""]
    if r["evidence"]:
        lines += ["## Evidence", *[f"- {e}" for e in r["evidence"]], ""]
    if r["hypotheses"]:
        lines += ["## Hypotheses", *[f"- **{h['id']}** [{h['status']}] {h['statement']} — {h.get('evidence', '')}"
                                     for h in r["hypotheses"]], ""]
    if r.get("reproduction"):
        lines += ["## Reproduction", f"Unpatched replay verification: "
                                     f"{r['reproduction'].get('verification', {}).get('outcome')}", ""]
    if r.get("patch"):
        lines += ["## Tested patch", r["patch"].get("rationale") or "", "", "```diff", r["patch"].get("diff") or "",
                  "```", f"Regression test: {', '.join(r['patch'].get('regression_files') or [])}", ""]
    if r.get("verification"):
        lines += ["## Independent verification", f"Result: **{r['verification'].get('outcome')}**", "",
                  "| assertion | expected | observed | pass |", "|---|---|---|---|",
                  *[f"| {a['name']} | {a['expected']} | {a['observed']} | {'yes' if a['passed'] else 'NO'} |"
                    for a in r["verification"].get("assertions", [])], ""]
    lines += ["## Limitations", *[f"- {x}" for x in r["limitations"]], ""]
    return "\n".join(lines)
