"""Incident families about webhook trust and delivery, on the same billing -> entitlement integration.

* signing_key_rotated: billing rotated the webhook signing key for one tenant; that tenant's config still trusts only
  the old key id, so the handler ignores the event and the sync service still answers 202 (silent failure).
  Fix: trust the new key id in the tenant config (flagged for the approver because it changes trust).
* ack_timeout: the receiver applied the change but the acknowledgement was lost, so billing timed out, retried and
  raised alerts; the customer also double-clicked "Pay". Nothing is broken: the right outcome is to confirm with the
  independent verifier (one charge, one grant, Pro active) and change nothing.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..simulators.world import DEFAULT_SIGNING_KEY
from .base import ScenarioFamily, ScenarioInstance, register
from .more_families import _base_world, _pay_and_deliver


def _contract(p: dict) -> dict:
    return {"kind": "paid_invoice_grants_plan", "customer_id": p["customer_id"],
            "invoice_id": p["invoice_id"], "event_id": p["event_id"]}


def _trust_keys(repo: Path, tenant: str, keys: list[str]) -> None:
    path = repo / "tenants" / f"{tenant}.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg["accepted_signing_keys"] = keys
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def setup_signing_key_rotated(run_dir: Path, rng: random.Random, variant: str) -> ScenarioInstance:
    world, repo, tenants, prices = _base_world(run_dir, rng)
    target, *others = tenants
    for t in tenants:
        _trust_keys(repo, t, [DEFAULT_SIGNING_KEY])
    for t in others:
        _pay_and_deliver(world, repo, t, prices["pro"], rng)
    new_key = f"whsec_{rng.choice(['k2', 'rot'])}_{rng.randint(100, 999)}"
    world.set_meta(f"signing_key:{target}", new_key)
    # Billing announces the rotation in its own logs; nobody updated the receiver's tenant config.
    world.log("billing", "info", "webhook signing key rotated", tenant=target, previous_key_id=DEFAULT_SIGNING_KEY,
              new_key_id=new_key, reason="scheduled 90-day rotation")
    price = prices["pro_annual"] if variant == "rotated_annual" else prices["pro"]
    p = _pay_and_deliver(world, repo, target, price, rng)
    assert world.account_for_customer(p["customer_id"])["plan"] == "free"
    return ScenarioInstance(
        family="signing_key_rotated", variant=variant, world_path=world.db_path, repo_dir=repo,
        ticket={"title": "Upgraded to Pro, still locked out",
                "description": (f"Customer {p['email']} ({target} tenant) paid for Pro this morning. Billing shows "
                                "the charge as succeeded but their workspace is still on Free. Other customers "
                                "upgraded fine today."),
                "reporter": "support@integrationrescue.example", "severity": "high"},
        contract=_contract(p),
        hidden={"root_cause": "signing_key_rotated", "category": "credentials", "tenant": target,
                "config_file": f"tenants/{target}.json", "new_key_id": new_key},
    )


def setup_ack_timeout(run_dir: Path, rng: random.Random, variant: str) -> ScenarioInstance:
    world, repo, (target, *others), prices = _base_world(run_dir, rng)
    for t in others:
        _pay_and_deliver(world, repo, t, prices["pro"], rng)
    world.set_fault("lost_ack")
    if variant == "lost_ack_duplicate":
        world.set_fault("duplicate_delivery")
    p = _pay_and_deliver(world, repo, target, prices["pro"], rng)
    # The customer clicked "Pay" twice; billing's idempotency key makes the second attempt a no-op.
    world.pay(p["customer_id"], prices["pro"], idempotency_key=f"checkout-{p['customer_id']}")
    world.clear_fault("duplicate_delivery")
    assert world.account_for_customer(p["customer_id"])["plan"] == "pro"
    return ScenarioInstance(
        family="ack_timeout", variant=variant, world_path=world.db_path, repo_dir=repo,
        ticket={"title": "Webhook timeout alerts on a Pro upgrade",
                "description": (f"On-call got 'webhook delivery timed out' alerts for {p['email']} ({target} "
                                "tenant) right after they upgraded. The customer says they clicked Pay twice and "
                                "is worried about being charged twice or not getting Pro. Please check and fix "
                                "whatever is broken."),
                "reporter": "oncall@integrationrescue.example", "severity": "medium"},
        contract=_contract(p),
        hidden={"root_cause": "ack_lost_after_commit", "expected_outcome": "NO_ACTION_NEEDED", "tenant": target},
    )


register(ScenarioFamily(
    name="signing_key_rotated", description="Webhook signing key rotated by billing; tenant still trusts the old key",
    variants=["rotated_monthly"], heldout_variants=["rotated_annual"], setup=setup_signing_key_rotated))
register(ScenarioFamily(
    name="ack_timeout", description="Delivery timed out after the receiver committed; outcome already correct",
    variants=["lost_ack"], heldout_variants=["lost_ack_duplicate"], setup=setup_ack_timeout))
