"""Entitlement sync service: the webhook receiver that runs the customer's handler code.

The handler runs in a child process with a timeout and a stripped environment;
its returned actions are validated before being applied to Entitlements.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .world import PLAN_FEATURES, Subscriber, World

RUNNER = Path(__file__).resolve().parent / "runner.py"
HANDLER_TIMEOUT_S = 15


def _child_env() -> dict[str, str]:
    keep = {"SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "TEMP", "TMP", "PATH"}
    return {k: v for k, v in os.environ.items() if k.upper() in keep}


def run_handler(repo_dir: Path, event: dict[str, Any], tenant: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-I", str(RUNNER), str(repo_dir), tenant],
        input=json.dumps(event), capture_output=True, text=True,
        timeout=HANDLER_TIMEOUT_S, env=_child_env(), cwd=str(repo_dir),
    )
    if proc.returncode != 0:
        return {"error": f"runner exited {proc.returncode}", "stderr": proc.stderr[-2000:]}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"error": "runner produced no JSON", "stdout": proc.stdout[-2000:]}


def make_subscriber(repo_dir: Path) -> Subscriber:
    repo_dir = Path(repo_dir)

    def subscriber(world: World, event: dict[str, Any]) -> tuple[int, str]:
        event_id = event["id"]
        done = world.query("SELECT result FROM processed_events WHERE event_id=?", (event_id,))
        if done and done[0]["result"] == "applied":
            world.log("entitlement-sync", "info", "duplicate event ignored (already applied)", event_id=event_id)
            return 200, "duplicate ignored"

        tenant = event.get("data", {}).get("tenant", "")
        out = run_handler(repo_dir, event, tenant)
        if "error" in out:
            world.log("entitlement-sync", "error", "handler failed", event_id=event_id, error=out["error"])
            return 500, out["error"]

        result = out["result"]
        for entry in result.get("log", []):
            world.log("entitlement-sync", entry.get("level", "info"), entry.get("message", ""),
                      event_id=event_id, tenant=tenant)

        applied = 0
        for action in result.get("actions", []):
            # Validate untrusted handler output before any side effect.
            if (action.get("op") != "set_plan" or action.get("plan") not in PLAN_FEATURES
                    or action.get("customer_id") != event["data"].get("customer_id")):
                world.log("entitlement-sync", "error", "rejected invalid action", event_id=event_id,
                          action=action)
                continue
            world.set_plan(action["customer_id"], action["plan"], source_event=event_id)
            applied += 1

        outcome = "applied" if applied else result.get("status", "noop")
        with world.conn() as c:
            c.execute("INSERT OR REPLACE INTO processed_events(event_id, result, processed_at)"
                      " VALUES(?,?,datetime('now'))", (event_id, outcome))
        # Like many real receivers, it acknowledges with 202 even when nothing was applied.
        return 202, f"accepted ({outcome})"

    return subscriber
