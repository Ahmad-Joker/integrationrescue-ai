"""Persistent simulated SaaS world: billing, entitlements, webhook delivery and logs.

Each World is one SQLite file, so an incident's "live" environment can be cloned
into a sandbox copy for patch replay without touching the original.
All data is fictional.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS faults (name TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, service TEXT, level TEXT,
  message TEXT, context TEXT);

-- Service A: billing
CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY, tenant TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  name TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS prices (
  id TEXT PRIMARY KEY, product TEXT, plan_family TEXT NOT NULL,
  amount INTEGER NOT NULL, currency TEXT NOT NULL, interval TEXT, active INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS invoices (
  id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, price_id TEXT NOT NULL,
  amount INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT);
CREATE TABLE IF NOT EXISTS charges (
  id TEXT PRIMARY KEY, invoice_id TEXT NOT NULL, amount INTEGER NOT NULL,
  status TEXT NOT NULL, idempotency_key TEXT NOT NULL UNIQUE, created_at TEXT);
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY, type TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT);

-- Service D: webhook delivery
CREATE TABLE IF NOT EXISTS deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, attempt INTEGER NOT NULL,
  status TEXT NOT NULL, http_status INTEGER, acked INTEGER NOT NULL, detail TEXT, created_at TEXT);

-- Service B: entitlements
CREATE TABLE IF NOT EXISTS accounts (
  id TEXT PRIMARY KEY, tenant TEXT NOT NULL, customer_id TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL, plan TEXT NOT NULL, updated_at TEXT);
CREATE TABLE IF NOT EXISTS entitlement_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_id TEXT NOT NULL, old_plan TEXT,
  new_plan TEXT, source_event TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS processed_events (
  event_id TEXT PRIMARY KEY, result TEXT, processed_at TEXT);
"""

PLAN_FEATURES = {
    "free": ["dashboard"],
    "pro": ["dashboard", "advanced_reports", "api_access", "priority_support"],
}

EPOCH = datetime(2026, 10, 1, 9, 0, 0, tzinfo=UTC)

# Subscriber signature: (world, event) -> (http_status, detail)
Subscriber = Callable[["World", dict[str, Any]], tuple[int, str]]


@dataclass
class DeliveryResult:
    event_id: str
    attempts: int
    final_status: str
    http_status: int | None


class World:
    def __init__(self, db_path: Path | str, readonly: bool = False):
        self.db_path = Path(db_path)
        self.readonly = readonly
        if not readonly:
            with self.conn() as c:
                c.executescript(SCHEMA)

    # ------------------------------------------------------------------ infra
    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        if self.readonly:
            uri = f"file:{self.db_path.as_posix()}?mode=ro"
            c = sqlite3.connect(uri, uri=True, timeout=5)
        else:
            c = sqlite3.connect(self.db_path, timeout=5)
        c.row_factory = sqlite3.Row
        try:
            yield c
            if not self.readonly:
                c.commit()
        finally:
            c.close()

    def clone_to(self, dest: Path | str) -> World:
        """Snapshot this world into a new database file (used for sandbox replay)."""
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()
        src = sqlite3.connect(self.db_path)
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            src.close()
            dst.close()
        return World(dest)

    def _tick(self, c: sqlite3.Connection) -> str:
        """Deterministic logical clock so runs are reproducible."""
        row = c.execute("SELECT value FROM meta WHERE key='clock'").fetchone()
        n = int(row["value"]) + 1 if row else 1
        c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('clock', ?)", (str(n),))
        return (EPOCH + timedelta(seconds=n)).isoformat().replace("+00:00", "Z")

    def _next_id(self, c: sqlite3.Connection, prefix: str) -> str:
        key = f"seq_{prefix}"
        row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        n = int(row["value"]) + 1 if row else 1
        c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, str(n)))
        salt = self.get_meta("id_salt") or "0000"
        return f"{prefix}_{salt}{n:04d}"

    def set_meta(self, key: str, value: str) -> None:
        with self.conn() as c:
            c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, value))

    def get_meta(self, key: str) -> str | None:
        with self.conn() as c:
            row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    def log(self, service: str, level: str, message: str, **context: Any) -> None:
        with self.conn() as c:
            ts = self._tick(c)
            c.execute(
                "INSERT INTO logs(ts, service, level, message, context) VALUES(?,?,?,?,?)",
                (ts, service, level, message, json.dumps(context, sort_keys=True)),
            )

    # ------------------------------------------------------------- faults
    def set_fault(self, name: str, value: Any = True) -> None:
        with self.conn() as c:
            c.execute("INSERT OR REPLACE INTO faults(name, value) VALUES(?, ?)", (name, json.dumps(value)))

    def clear_fault(self, name: str) -> None:
        with self.conn() as c:
            c.execute("DELETE FROM faults WHERE name=?", (name,))

    def fault(self, name: str) -> Any:
        with self.conn() as c:
            row = c.execute("SELECT value FROM faults WHERE name=?", (name,)).fetchone()
        return json.loads(row["value"]) if row else None

    # ------------------------------------------------------------- billing
    def add_price(self, price_id: str, plan_family: str, amount: int, interval: str = "month",
                  product: str = "Workspace", active: bool = True, currency: str = "usd") -> None:
        with self.conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO prices VALUES(?,?,?,?,?,?,?)",
                (price_id, product, plan_family, amount, currency, interval, int(active)),
            )

    def create_customer(self, tenant: str, email: str, name: str) -> dict[str, Any]:
        with self.conn() as c:
            ts = self._tick(c)
            cid = self._next_id(c, "cus")
            c.execute("INSERT INTO customers VALUES(?,?,?,?,?)", (cid, tenant, email, name, ts))
            aid = self._next_id(c, "acct")
            c.execute("INSERT INTO accounts VALUES(?,?,?,?,?,?)", (aid, tenant, cid, email, "free", ts))
        self.log("billing", "info", "customer created", customer_id=cid, tenant=tenant)
        self.log("entitlements", "info", "account provisioned on free plan", account_id=aid, customer_id=cid)
        return {"customer_id": cid, "account_id": aid}

    def pay(self, customer_id: str, price_id: str, idempotency_key: str) -> dict[str, Any]:
        """Charge a customer for a price. Idempotent on idempotency_key: never double-charges."""
        with self.conn() as c:
            existing = c.execute(
                "SELECT * FROM charges WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing:
                inv = c.execute("SELECT * FROM invoices WHERE id=?", (existing["invoice_id"],)).fetchone()
                replay = True
                result = {"invoice_id": inv["id"], "charge_id": existing["id"], "event_id": None,
                          "idempotent_replay": replay}
            else:
                price = c.execute("SELECT * FROM prices WHERE id=?", (price_id,)).fetchone()
                if price is None:
                    raise ValueError(f"unknown price {price_id}")
                cust = c.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
                if cust is None:
                    raise ValueError(f"unknown customer {customer_id}")
                ts = self._tick(c)
                inv_id = self._next_id(c, "in")
                ch_id = self._next_id(c, "ch")
                c.execute("INSERT INTO invoices VALUES(?,?,?,?,?,?)",
                          (inv_id, customer_id, price_id, price["amount"], "paid", ts))
                c.execute("INSERT INTO charges VALUES(?,?,?,?,?,?)",
                          (ch_id, inv_id, price["amount"], "succeeded", idempotency_key, ts))
                ev_id = self._next_id(c, "evt")
                # Tenants can be pinned to a newer webhook API version with a different line shape.
                row = c.execute("SELECT value FROM meta WHERE key=?", (f"api_version:{cust['tenant']}",)).fetchone()
                api_version = row["value"] if row else "2026-06-01"
                if api_version >= "2026-09-01":
                    line = {"price": {"id": price_id, "interval": price["interval"]},
                            "amount": price["amount"], "currency": price["currency"]}
                else:
                    line = {"price_id": price_id, "amount": price["amount"],
                            "currency": price["currency"], "interval": price["interval"]}
                payload = {
                    "id": ev_id, "type": "invoice.paid", "created": ts, "api_version": api_version,
                    "data": {
                        "invoice_id": inv_id, "customer_id": customer_id,
                        "customer_email": cust["email"], "tenant": cust["tenant"],
                        "lines": [line],
                    },
                }
                c.execute("INSERT INTO events VALUES(?,?,?,?)", (ev_id, "invoice.paid", json.dumps(payload), ts))
                result = {"invoice_id": inv_id, "charge_id": ch_id, "event_id": ev_id, "idempotent_replay": False}
        if result["idempotent_replay"]:
            self.log("billing", "info", "idempotent payment replay; no new charge",
                     idempotency_key=idempotency_key, charge_id=result["charge_id"])
        else:
            self.log("billing", "info", "charge succeeded", charge_id=result["charge_id"],
                     invoice_id=result["invoice_id"], customer_id=customer_id)
            self.log("billing", "info", "event emitted", event_id=result["event_id"], type="invoice.paid")
        return result

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with self.conn() as c:
            row = c.execute("SELECT payload FROM events WHERE id=?", (event_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    # ---------------------------------------------------------- webhooks
    def deliver(self, event_id: str, subscriber: Subscriber, max_attempts: int = 3) -> DeliveryResult:
        """Deliver an event with retries. Faults model duplicates, timeouts and lost acks."""
        event = self.get_event(event_id)
        if event is None:
            raise ValueError(f"unknown event {event_id}")
        with self.conn() as c:
            prev = c.execute("SELECT COALESCE(MAX(attempt),0) AS n FROM deliveries WHERE event_id=?",
                             (event_id,)).fetchone()["n"]
        attempt = prev
        http_status: int | None = None
        status = "failed"
        for _ in range(max_attempts):
            attempt += 1
            try:
                http_status, detail = subscriber(self, event)
            except Exception as exc:  # subscriber crashed -> 500 from the receiver's side
                http_status, detail = 500, f"subscriber error: {type(exc).__name__}: {exc}"
            acked = 200 <= http_status < 300
            if acked and self.fault("lost_ack"):
                # Receiver committed but the ack never reached the sender.
                self.clear_fault("lost_ack")
                acked, status_txt, detail = False, "timeout", "ack lost in transit (receiver may have committed)"
                http_status = None
            else:
                status_txt = "delivered" if acked else "failed"
            self._record_delivery(event_id, attempt, status_txt, http_status, acked, detail)
            if acked:
                status = "delivered"
                break
        if status == "delivered" and self.fault("duplicate_delivery"):
            self.clear_fault("duplicate_delivery")
            attempt += 1
            dup_status, dup_detail = subscriber(self, event)
            self._record_delivery(event_id, attempt, "delivered", dup_status, True, "duplicate delivery: " + dup_detail)
        return DeliveryResult(event_id, attempt, status, http_status)

    def _record_delivery(self, event_id: str, attempt: int, status: str, http_status: int | None,
                         acked: bool, detail: str) -> None:
        with self.conn() as c:
            ts = self._tick(c)
            c.execute(
                "INSERT INTO deliveries(event_id, attempt, status, http_status, acked, detail, created_at)"
                " VALUES(?,?,?,?,?,?,?)",
                (event_id, attempt, status, http_status, int(acked), detail, ts),
            )
        self.log("webhooks", "info" if status == "delivered" else "warning",
                 f"delivery attempt {attempt} {status}", event_id=event_id, http_status=http_status)

    # ------------------------------------------------------ entitlements
    def account_for_customer(self, customer_id: str) -> dict[str, Any] | None:
        with self.conn() as c:
            row = c.execute("SELECT * FROM accounts WHERE customer_id=?", (customer_id,)).fetchone()
        return dict(row) if row else None

    def set_plan(self, customer_id: str, plan: str, source_event: str) -> dict[str, Any]:
        if plan not in PLAN_FEATURES:
            raise ValueError(f"unknown plan {plan}")
        with self.conn() as c:
            acct = c.execute("SELECT * FROM accounts WHERE customer_id=?", (customer_id,)).fetchone()
            if acct is None:
                raise ValueError(f"no account for customer {customer_id}")
            ts = self._tick(c)
            c.execute("UPDATE accounts SET plan=?, updated_at=? WHERE id=?", (plan, ts, acct["id"]))
            c.execute(
                "INSERT INTO entitlement_audit(account_id, old_plan, new_plan, source_event, created_at)"
                " VALUES(?,?,?,?,?)", (acct["id"], acct["plan"], plan, source_event, ts))
        self.log("entitlements", "info", "plan changed", account_id=acct["id"],
                 old_plan=acct["plan"], new_plan=plan, source_event=source_event)
        return {"account_id": acct["id"], "old_plan": acct["plan"], "new_plan": plan}

    # --------------------------------------------------------- queries
    def query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.conn() as c:
            return [dict(r) for r in c.execute(sql, params).fetchall()]
