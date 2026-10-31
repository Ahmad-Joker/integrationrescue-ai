"""Billing -> entitlement sync handler.

Receives billing webhooks and decides which entitlement changes to make.
The handler is pure: it returns actions; the sync service applies them.
Plan resolution is tenant-configurable via tenants/<tenant>.json.
"""

from __future__ import annotations

import json
from pathlib import Path

TENANT_DIR = Path(__file__).resolve().parent.parent / "tenants"


def load_tenant(tenant: str) -> dict:
    return json.loads((TENANT_DIR / f"{tenant}.json").read_text(encoding="utf-8"))


def resolve_plan(price_id: str, tenant_cfg: dict) -> str | None:
    return tenant_cfg.get("price_plan_map", {}).get(price_id)


def handle(event: dict, tenant_cfg: dict) -> dict:
    if event.get("type") != "invoice.paid":
        return {"status": "ignored", "actions": [], "log": []}
    data = event["data"]
    line = data["lines"][0]
    plan = resolve_plan(line["price_id"], tenant_cfg)
    if plan is None:
        return {
            "status": "unmapped",
            "actions": [],
            "log": [{
                "level": "warning",
                "message": f"no plan mapping for price {line['price_id']}; entitlement left unchanged",
            }],
        }
    return {
        "status": "ok",
        "actions": [{"op": "set_plan", "customer_id": data["customer_id"], "plan": plan}],
        "log": [{"level": "info", "message": f"resolved price {line['price_id']} to plan {plan}"}],
    }
