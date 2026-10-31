"""HTTP API for the simulated services. The agent's tools talk to these endpoints."""

from __future__ import annotations

import json
from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException, Query

from .world import PLAN_FEATURES, World

WorldResolver = Callable[[str], World]


def build_router(resolve: WorldResolver) -> APIRouter:
    r = APIRouter()

    def world(wid: str) -> World:
        try:
            return resolve(wid)
        except KeyError:
            raise HTTPException(404, f"unknown environment {wid}") from None

    def billing(wid: str) -> World:
        w = world(wid)
        if w.fault("billing_ledger_unavailable"):
            raise HTTPException(503, "billing ledger temporarily unavailable")
        return w

    # ---------------- billing
    @r.get("/worlds/{wid}/billing/customers")
    def find_customers(wid: str, email: str | None = None, customer_id: str | None = None):
        w = world(wid)
        if email:
            return w.query("SELECT * FROM customers WHERE lower(email)=lower(?)", (email,))
        if customer_id:
            return w.query("SELECT * FROM customers WHERE id=?", (customer_id,))
        raise HTTPException(400, "email or customer_id required")

    @r.get("/worlds/{wid}/billing/customers/{cid}/invoices")
    def invoices(wid: str, cid: str):
        return billing(wid).query("SELECT * FROM invoices WHERE customer_id=? ORDER BY created_at", (cid,))

    @r.get("/worlds/{wid}/billing/invoices/{iid}/charges")
    def charges(wid: str, iid: str):
        rows = billing(wid).query("SELECT * FROM charges WHERE invoice_id=?", (iid,))
        for row in rows:
            row.pop("idempotency_key", None)
        return rows

    @r.get("/worlds/{wid}/billing/prices")
    def prices(wid: str, plan_family: str | None = None):
        w = world(wid)
        if plan_family:
            return w.query("SELECT * FROM prices WHERE plan_family=?", (plan_family,))
        return w.query("SELECT * FROM prices")

    @r.get("/worlds/{wid}/billing/prices/{pid}")
    def price(wid: str, pid: str):
        rows = world(wid).query("SELECT * FROM prices WHERE id=?", (pid,))
        if not rows:
            raise HTTPException(404, "price not found")
        return rows[0]

    @r.get("/worlds/{wid}/billing/events")
    def events(wid: str, customer_id: str | None = None):
        rows = billing(wid).query("SELECT payload FROM events ORDER BY created_at")
        out = [json.loads(x["payload"]) for x in rows]
        if customer_id:
            out = [e for e in out if e.get("data", {}).get("customer_id") == customer_id]
        return out

    @r.get("/worlds/{wid}/billing/events/{eid}")
    def event(wid: str, eid: str):
        ev = billing(wid).get_event(eid)
        if ev is None:
            raise HTTPException(404, "event not found")
        return ev

    # ---------------- webhooks
    @r.get("/worlds/{wid}/webhooks/deliveries")
    def deliveries(wid: str, event_id: str):
        return world(wid).query("SELECT * FROM deliveries WHERE event_id=? ORDER BY attempt", (event_id,))

    # ---------------- entitlements
    @r.get("/worlds/{wid}/entitlements/accounts")
    def accounts(wid: str, customer_id: str | None = None, email: str | None = None):
        w = world(wid)
        if customer_id:
            rows = w.query("SELECT * FROM accounts WHERE customer_id=?", (customer_id,))
        elif email:
            rows = w.query("SELECT * FROM accounts WHERE lower(email)=lower(?)", (email,))
        else:
            raise HTTPException(400, "customer_id or email required")
        for row in rows:
            row["features"] = PLAN_FEATURES.get(row["plan"], [])
        return rows

    @r.get("/worlds/{wid}/entitlements/accounts/{aid}/audit")
    def audit(wid: str, aid: str):
        return world(wid).query("SELECT * FROM entitlement_audit WHERE account_id=? ORDER BY id", (aid,))

    @r.get("/worlds/{wid}/entitlements/processed-events/{eid}")
    def processed(wid: str, eid: str):
        return world(wid).query("SELECT * FROM processed_events WHERE event_id=?", (eid,))

    # ---------------- logs
    @r.get("/worlds/{wid}/logs")
    def logs(wid: str, q: str | None = None, service: str | None = None,
             level: str | None = None, limit: int = Query(50, le=200)):
        sql, params = "SELECT * FROM logs WHERE 1=1", []
        if q:
            sql += " AND (message LIKE ? OR context LIKE ?)"
            params += [f"%{q}%", f"%{q}%"]
        if service:
            sql += " AND service=?"
            params.append(service)
        if level:
            sql += " AND level=?"
            params.append(level)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        return list(reversed(world(wid).query(sql, tuple(params))))

    return r


def create_sim_app(resolve: WorldResolver) -> FastAPI:
    app = FastAPI(title="IntegrationRescue simulators")
    app.include_router(build_router(resolve))
    return app
