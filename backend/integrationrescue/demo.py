"""Terminal demo of the first milestone incident.

python -m integrationrescue.demo [--provider deterministic|claude] [--fault duplicate_delivery] [--seed N]
"""

from __future__ import annotations

import argparse

from .agent.orchestrator import IncidentService


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="deterministic")
    ap.add_argument("--variant", default="stale_price_id")
    ap.add_argument("--family", default="payment_entitlement")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--fault", action="append", default=[])
    a = ap.parse_args()

    svc = IncidentService()
    iid = svc.create_from_scenario(a.family, a.variant, a.seed, provider=a.provider,
                                   faults={f: True for f in a.fault})
    inc = svc.run(iid)
    banner = "LIVE AI AGENT" if inc["mode"] == "live" else "DETERMINISTIC BASELINE (no LLM)"
    print(f"== {iid} [{banner}] ==")
    for e in svc.store.timeline(iid):
        print(f"{e['phase']:<18} {e['kind']:<24} {e['summary'][:110]}")
    if inc["phase"] == "awaiting_approval":
        if input("\nApprove the tested patch? [y/N] ").strip().lower() == "y":
            svc.approve(iid, "terminal-operator")
            inc = svc.run(iid)
            for e in svc.store.timeline(iid)[-4:]:
                print(f"{e['phase']:<18} {e['kind']:<24} {e['summary'][:110]}")
        else:
            svc.reject(iid, "terminal-operator", "declined in demo")
            inc = svc.run(iid)
    print(f"\nFinal outcome: {inc['outcome']}")
    print(f"Report: {inc['data']['run_dir']}\\report.md")


if __name__ == "__main__":
    main()
