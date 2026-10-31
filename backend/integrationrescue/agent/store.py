"""Durable incident state + append-only audit timeline (SQLite)."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..paths import var_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY, created_at TEXT, updated_at TEXT, phase TEXT, outcome TEXT,
  mode TEXT, provider TEXT, data TEXT NOT NULL, hidden TEXT);
CREATE TABLE IF NOT EXISTS timeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT, incident_id TEXT, ts TEXT, phase TEXT,
  kind TEXT, summary TEXT, payload TEXT);
CREATE INDEX IF NOT EXISTS timeline_incident ON timeline(incident_id, id);
"""

_lock = threading.Lock()


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class Store:
    def __init__(self, path: Path | None = None):
        self.path = path or var_dir() / "incidents.db"
        with self.conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        with _lock:
            c = sqlite3.connect(self.path, timeout=10)
            c.row_factory = sqlite3.Row
            try:
                yield c
                c.commit()
            finally:
                c.close()

    def create(self, incident_id: str, data: dict[str, Any], hidden: dict[str, Any], mode: str,
               provider: str) -> None:
        ts = now()
        with self.conn() as c:
            c.execute("INSERT INTO incidents VALUES(?,?,?,?,?,?,?,?,?)",
                      (incident_id, ts, ts, "intake", None, mode, provider, json.dumps(data), json.dumps(hidden)))

    def save(self, incident_id: str, data: dict[str, Any], phase: str, outcome: str | None) -> None:
        with self.conn() as c:
            c.execute("UPDATE incidents SET data=?, phase=?, outcome=?, updated_at=? WHERE id=?",
                      (json.dumps(data, default=str), phase, outcome, now(), incident_id))

    def get(self, incident_id: str) -> dict[str, Any] | None:
        with self.conn() as c:
            row = c.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
        if not row:
            return None
        return {"id": row["id"], "created_at": row["created_at"], "updated_at": row["updated_at"],
                "phase": row["phase"], "outcome": row["outcome"], "mode": row["mode"],
                "provider": row["provider"], "data": json.loads(row["data"])}

    def hidden(self, incident_id: str) -> dict[str, Any]:
        """Ground truth for the evaluator only."""
        with self.conn() as c:
            row = c.execute("SELECT hidden FROM incidents WHERE id=?", (incident_id,)).fetchone()
        return json.loads(row["hidden"]) if row and row["hidden"] else {}

    def list(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.conn() as c:
            rows = c.execute("SELECT id, created_at, updated_at, phase, outcome, mode, provider, data "
                             "FROM incidents ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = json.loads(r["data"])
            out.append({"id": r["id"], "created_at": r["created_at"], "updated_at": r["updated_at"],
                        "phase": r["phase"], "outcome": r["outcome"], "mode": r["mode"],
                        "provider": r["provider"], "title": d["ticket"]["title"],
                        "source": d.get("source", "manual")})
        return out

    def event(self, incident_id: str, phase: str, kind: str, summary: str, payload: Any = None) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO timeline(incident_id, ts, phase, kind, summary, payload) VALUES(?,?,?,?,?,?)",
                      (incident_id, now(), phase, kind, summary[:500], json.dumps(payload, default=str)))

    def timeline(self, incident_id: str) -> list[dict[str, Any]]:
        with self.conn() as c:
            rows = c.execute("SELECT * FROM timeline WHERE incident_id=? ORDER BY id", (incident_id,)).fetchall()
        return [{"seq": r["id"], "ts": r["ts"], "phase": r["phase"], "kind": r["kind"],
                 "summary": r["summary"], "payload": json.loads(r["payload"]) if r["payload"] else None}
                for r in rows]
