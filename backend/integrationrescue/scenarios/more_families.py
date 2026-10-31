"""Additional incident families built on the same billing -> entitlement integration.

* schema_drift: a tenant was moved to a newer webhook API version whose line-item
  shape differs; the handler crashes and every delivery attempt returns 500.
* state_unavailable: the same symptom, but the authoritative billing ledger is
  unavailable, so the only correct outcome is INDETERMINATE.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..simulators.sync_service import make_subscriber
from ..simulators.world import World
from .base import TENANTS, ScenarioFamily, ScenarioInstance, copy_template_repo, fictional_person, register


def _base_world(run_dir: Path, rng: random.Random) -> tuple[World, Path, list[str], dict[str, str]]:
    run_dir.mkdir(parents=True, exist_ok=True)
    repo = copy_template_repo(run_dir / "repo")
    world = World(run_dir / "world.db")
    world.set_meta("id_salt", f"{rng.randint(0, 0xFFFF):04x}")
    year = rng.choice([2026, 2027])
    prices = {"free": "price_free", "pro": f"price_pro_{rng.choice(['m', 'monthly'])}_{year}",
              "pro_annual": f"price_pro_annual_{year}"}
    world.add_price(prices["free"], "free", 0)
    world.add_price(prices["pro"], "pro", rng.choice([2900, 3200]))
    world.add_price(prices["pro_annual"], "pro", rng.choice([29000, 32000]), interval="year")
    tenants = rng.sample(TENANTS, 3)
    mapping = {prices["free"]: "free", prices["pro"]: "pro", prices["pro_annual"]: "pro"}
    for t in tenants:
        cfg = {"tenant": t, "schema_version": 3, "price_plan_map": mapping}
        (repo / "tenants").mkdir(exist_ok=True)
        (repo / "tenants" / f"{t}.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return world, repo, tenants, prices


def _pay_and_deliver(world: World, repo: Path, tenant: str, price: str, rng: random.Random) -> dict:
    name, email = fictional_person(rng, tenant)
    ids = world.create_customer(tenant, email, name)
    pay = world.pay(ids["customer_id"], price, idempotency_key=f"checkout-{ids['customer_id']}")
    world.deliver(pay["event_id"], make_subscriber(repo))
    return {**ids, **pay, "email": email}


def _ticket(email: str, tenant: str) -> dict:
    return {"title": "Upgrade paid but features still locked",
            "description": (f"{email} on the {tenant} workspace completed checkout for Pro. "
                            "Card was charged but the account is still Free. Customer is asking for a refund "
                            "if this is not fixed today."),
            "reporter": "support@integrationrescue.example", "severity": "high"}


def setup_schema_drift(run_dir: Path, rng: random.Random, variant: str) -> ScenarioInstance:
    world, repo, (target, *others), prices = _base_world(run_dir, rng)
    for t in others:
        _pay_and_deliver(world, repo, t, prices["pro"], rng)
    world.set_meta(f"api_version:{target}", "2026-09-01")
    world.log("billing", "info", "webhook endpoint api_version upgraded", tenant=target, api_version="2026-09-01")
    price = prices["pro_annual"] if variant == "annual_line" else prices["pro"]
    p = _pay_and_deliver(world, repo, target, price, rng)
    assert world.account_for_customer(p["customer_id"])["plan"] == "free"
    return ScenarioInstance(
        family="schema_drift", variant=variant, world_path=world.db_path, repo_dir=repo,
        ticket=_ticket(p["email"], target),
        contract={"kind": "paid_invoice_grants_plan", "customer_id": p["customer_id"],
                  "invoice_id": p["invoice_id"], "event_id": p["event_id"]},
        hidden={"root_cause": "webhook_schema_drift", "category": "schema_drift", "tenant": target,
                "config_file": "sync/handler.py"},
    )


def setup_state_unavailable(run_dir: Path, rng: random.Random, variant: str) -> ScenarioInstance:
    world, repo, (target, *_), prices = _base_world(run_dir, rng)
    # A real mapping defect exists, but the ledger is down so expected state cannot be established.
    cfg_path = repo / "tenants" / f"{target}.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["price_plan_map"].pop(prices["pro"])
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    p = _pay_and_deliver(world, repo, target, prices["pro"], rng)
    world.set_fault("billing_ledger_unavailable")
    return ScenarioInstance(
        family="state_unavailable", variant=variant, world_path=world.db_path, repo_dir=repo,
        ticket=_ticket(p["email"], target),
        contract={"kind": "paid_invoice_grants_plan", "customer_id": p["customer_id"],
                  "invoice_id": p["invoice_id"], "event_id": p["event_id"]},
        hidden={"root_cause": "authoritative_state_unavailable", "expected_outcome": "INDETERMINATE",
                "tenant": target},
    )


register(ScenarioFamily(
    name="schema_drift", description="Webhook API version drift broke the handler for one tenant",
    variants=["monthly_line"], heldout_variants=["annual_line"], setup=setup_schema_drift))
register(ScenarioFamily(
    name="state_unavailable", description="Authoritative billing state unavailable; must not claim success",
    variants=["ledger_down"], heldout_variants=[], setup=setup_state_unavailable))
