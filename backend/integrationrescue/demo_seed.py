"""Fictional incidents for the competition demo: presets judges can launch, and a seeded example.

Every environment is a freshly generated SQLite simulation with fictional customers; nothing here touches a real
system. The seeded example runs on the deterministic baseline (labelled as such in the UI) and stops at the human
approval gate, so a judge performs the approval; live-model incidents are only ever started by a person.
"""

from __future__ import annotations

from typing import Any

FEATURED: list[dict[str, Any]] = [
    {"key": "paid_still_free", "title": "Paid for Pro, still on Free",
     "impact": "Customer charged, locked out of paid features; support ticket and refund risk.",
     "family": "payment_entitlement", "variant": "stale_price_id", "seed": 4242,
     "faults": {"duplicate_delivery": True}, "recommended_provider": "gemini", "expected_kind": "repair",
     "evidence": "Recommended live demo: live Gemini reached VERIFIED on 8/8 scored runs of this family "
                 "(eval_gemini_20261031_232820)."},
    {"key": "signing_key_rotated", "title": "Billing rotated its webhook signing key",
     "impact": "Every upgrade for one tenant is silently ignored while billing reports success.",
     "family": "signing_key_rotated", "variant": "rotated_monthly", "seed": 5151, "faults": {},
     "recommended_provider": "gemini", "expected_kind": "repair (trust change, medium risk)",
     "evidence": "Live Gemini 3/3 scored runs VERIFIED (eval_gemini_20261101_002233)."},
    {"key": "timeout_false_alarm", "title": "Timeout alerts after a double click",
     "impact": "On-call paged; customer fears a double charge. Correct answer: change nothing, prove it.",
     "family": "ack_timeout", "variant": "lost_ack", "seed": 6161, "faults": {},
     "recommended_provider": "gemini", "expected_kind": "no action needed",
     "evidence": "Live Gemini 3/3 scored runs NO_ACTION_NEEDED, 0 unnecessary patches (eval_gemini_20261101_002233)."},
    {"key": "ledger_outage", "title": "Billing ledger unavailable",
     "impact": "The source of truth is down; the agent must refuse to claim success.",
     "family": "state_unavailable", "variant": "ledger_down", "seed": 7171, "faults": {},
     "recommended_provider": "gemini", "expected_kind": "indeterminate",
     "evidence": "Live Gemini 4/4 scored runs INDETERMINATE across live runs 1 and 2."},
    {"key": "schema_drift", "title": "Billing API version changed the payload (code fix)",
     "impact": "A code change in the sync handler is needed, not a config edit.",
     "family": "schema_drift", "variant": "monthly_line", "seed": 8181, "faults": {},
     "recommended_provider": "gemini", "expected_kind": "repair (code) - experimental",
     "evidence": "Not reliable yet: live code repair VERIFIED once in a standalone run, 0 of 5 scored eval runs."},
]

SEED_EXAMPLES = (("payment_entitlement", "stale_price_id", 4243, {"duplicate_delivery": True}),
                 ("ack_timeout", "lost_ack", 6162, {}))


def seed_demo(svc: Any) -> list[str]:
    """Create and run the baseline examples; the first stops at awaiting_approval for a human."""
    ids = []
    for family, variant, seed, faults in SEED_EXAMPLES:
        iid = svc.create_from_scenario(family, variant, seed, provider="deterministic", faults=faults)
        svc.run(iid)
        ids.append(iid)
    return ids
