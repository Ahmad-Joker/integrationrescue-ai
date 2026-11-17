"""End-to-end check of a running IntegrationRescue demo (local or deployed).

    python scripts/verify_deployment.py --url https://<host> [--provider deterministic|gemini]

The access code is read from IR_ACCESS_TOKEN (never pass it on the command line: shells keep history).
Checks: health, dashboard, access control, fictional incident, agent run, human-approval gate, approval,
independent verification, and safe failure (ledger outage -> INDETERMINATE, never VERIFIED).
`--provider gemini` spends live-model quota (about 12-30 calls per incident); the default spends none.
Exit code 0 only if every check passed.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import httpx

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{' - ' + detail if detail else ''}")
    return ok


def wait(c: httpx.Client, iid: str, phases: tuple[str, ...], timeout: float) -> dict:
    end = time.time() + timeout
    inc: dict = {}
    while time.time() < end:
        inc = c.get(f"/api/incidents/{iid}").json()
        if inc["phase"] in phases and not inc["running"]:
            return inc
        time.sleep(2)
    return inc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--provider", default="deterministic", choices=["deterministic", "gemini"])
    ap.add_argument("--timeout", type=float, default=600)
    a = ap.parse_args()
    token = os.environ.get("IR_ACCESS_TOKEN", "")
    h = {"x-access-token": token} if token else {}
    c = httpx.Client(base_url=a.url.rstrip("/"), timeout=60, follow_redirects=True)

    health = c.get("/api/health")
    if not check("health endpoint", health.status_code == 200 and health.json().get("status") == "ok",
                 f"HTTP {health.status_code}"):
        return 1
    hj = health.json()
    print(f"       version={hj.get('version')} demo_mode={hj.get('demo_mode')} "
          f"live_providers={hj.get('live_providers')} default={hj.get('default_provider')}")
    check("health exposes no secrets", token not in health.text if token else True)
    page = c.get("/")
    check("dashboard served", page.status_code == 200 and "<div id=\"root\"" in page.text, f"HTTP {page.status_code}")
    if hj.get("access_required"):
        check("state change without access code is refused",
              c.post("/api/incidents", json={"autorun": False}).status_code == 401)
        if not token:
            check("IR_ACCESS_TOKEN provided to this script", False, "set it to run the remaining checks")
            return 1
        check("auto-approval refused (human gate cannot be skipped)",
              c.post("/api/incidents", json={"auto_approve": True, "autorun": False}, headers=h).status_code == 403)
    if a.provider == "gemini" and not (hj.get("live_providers") or {}).get("gemini"):
        check("live Gemini configured on the server", False, "GEMINI_API_KEY missing on the server")
        return 1

    r = c.post("/api/incidents", headers=h, json={"family": "payment_entitlement", "variant": "stale_price_id",
                                                  "seed": int(time.time()) % 100000, "provider": a.provider,
                                                  "faults": {"duplicate_delivery": True}})
    if not check("fictional incident created", r.status_code == 200, r.text[:200]):
        return 1
    iid = r.json()["id"]
    inc = wait(c, iid, ("awaiting_approval", "done"), a.timeout)
    check("agent ran with tools", len(inc.get("trace", [])) > 3, f"{len(inc.get('trace', []))} tool calls, "
          f"mode={inc.get('mode')} provider={inc.get('provider')}")
    if inc.get("provider_error"):
        check("model available", False, f"{inc['provider_error']['kind']}: {inc['provider_error']['message']}")
    if not check("stopped at the human approval gate", inc.get("phase") == "awaiting_approval" and not inc["approval"],
                 f"phase={inc.get('phase')} outcome={inc.get('outcome')}"):
        return summary()
    tests = (inc.get("patch") or {}).get("tests") or {}
    check("sandbox tests passed and regression test fails on unpatched code",
          tests.get("suite", {}).get("passed") is True
          and tests.get("regression_on_unpatched", {}).get("passed") is False)
    ok = c.post(f"/api/incidents/{iid}/approve", json={"approver": "deployment-check"}, headers=h)
    check("human approval accepted", ok.status_code == 200, ok.text[:200])
    inc = wait(c, iid, ("done",), a.timeout)
    v = inc.get("verification") or {}
    check("independent verification PASS", v.get("outcome") == "PASS", v.get("reason", ""))
    check("outcome VERIFIED", inc.get("outcome") == "VERIFIED", str(inc.get("outcome")))
    names = {x["name"]: x["passed"] for x in v.get("assertions", [])}
    check("exactly one charge and one grant despite duplicate delivery",
          names.get("exactly_one_successful_charge") is True and any("grant" in k and p for k, p in names.items()))

    r = c.post("/api/incidents", headers=h, json={"family": "payment_entitlement", "variant": "stale_price_id",
                                                  "seed": 99, "provider": "deterministic",
                                                  "faults": {"billing_ledger_unavailable": True}})
    if check("ledger-outage incident created", r.status_code == 200, r.text[:200]):
        inc = wait(c, r.json()["id"], ("done", "awaiting_approval"), a.timeout)
        check("safe failure: INDETERMINATE, never VERIFIED", inc.get("outcome") == "INDETERMINATE",
              f"phase={inc.get('phase')} outcome={inc.get('outcome')}")
    return summary()


def summary() -> int:
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
