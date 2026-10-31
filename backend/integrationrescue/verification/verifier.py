"""Independent business-outcome verifier.

Deliberately separate from the agent: it never sees agent output, opens the
environment read-only, and derives the expected state from the authoritative
billing ledger rather than from any claim made during the investigation.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..simulators.world import World


@dataclass
class Assertion:
    name: str
    expected: Any
    observed: Any
    passed: bool


@dataclass
class VerificationResult:
    outcome: str  # PASS | FAIL | INDETERMINATE
    assertions: list[Assertion] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"outcome": self.outcome, "reason": self.reason,
                "assertions": [asdict(a) for a in self.assertions]}


def verify(world_path: Path | str, contract: dict[str, Any]) -> VerificationResult:
    path = Path(world_path)
    if not path.exists():
        return VerificationResult("INDETERMINATE", reason="environment state not found")
    try:
        world = World(path, readonly=True)
        if contract["kind"] == "paid_invoice_grants_plan":
            return _paid_invoice_grants_plan(world, contract)
        return VerificationResult("INDETERMINATE", reason=f"no verifier for contract {contract['kind']}")
    except sqlite3.Error as exc:
        return VerificationResult("INDETERMINATE", reason=f"authoritative state unreadable: {exc}")


def _paid_invoice_grants_plan(world: World, contract: dict[str, Any]) -> VerificationResult:
    if world.fault("billing_ledger_unavailable"):
        return VerificationResult("INDETERMINATE", reason="billing ledger unavailable; expected state unknown")

    a: list[Assertion] = []
    inv = world.query("SELECT * FROM invoices WHERE id=?", (contract["invoice_id"],))
    if not inv:
        return VerificationResult("INDETERMINATE", reason="invoice not found in billing ledger")
    inv = inv[0]
    charges = world.query("SELECT * FROM charges WHERE invoice_id=?", (inv["id"],))
    succeeded = [c for c in charges if c["status"] == "succeeded"]
    unknown = [c for c in charges if c["status"] not in ("succeeded", "failed", "refunded")]
    if unknown:
        return VerificationResult("INDETERMINATE", reason="charge status ambiguous in billing ledger")

    a.append(Assertion("invoice_paid", "paid", inv["status"], inv["status"] == "paid"))
    a.append(Assertion("exactly_one_successful_charge", 1, len(succeeded), len(succeeded) == 1))
    invoices_same_price = world.query(
        "SELECT COUNT(*) AS n FROM invoices WHERE customer_id=? AND price_id=?",
        (contract["customer_id"], inv["price_id"]))[0]["n"]
    a.append(Assertion("no_duplicate_invoice", 1, invoices_same_price, invoices_same_price == 1))

    price = world.query("SELECT * FROM prices WHERE id=?", (inv["price_id"],))
    if not price:
        return VerificationResult("INDETERMINATE", assertions=a, reason="price missing from catalog")
    expected_plan = price[0]["plan_family"]

    acct = world.query("SELECT * FROM accounts WHERE customer_id=?", (contract["customer_id"],))
    observed_plan = acct[0]["plan"] if acct else None
    a.append(Assertion("entitlement_matches_paid_plan", expected_plan, observed_plan,
                       observed_plan == expected_plan))
    if acct:
        grants = world.query(
            "SELECT COUNT(*) AS n FROM entitlement_audit WHERE account_id=? AND source_event=? AND new_plan=?",
            (acct[0]["id"], contract["event_id"], expected_plan))[0]["n"]
        a.append(Assertion("entitlement_granted_once_for_event", 1, grants, grants == 1))

    outcome = "PASS" if all(x.passed for x in a) else "FAIL"
    return VerificationResult(outcome, assertions=a)
