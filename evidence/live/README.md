# Live Gemini end-to-end check — 2026-11-18 (local demo server)

Recorded by running `scripts/verify_deployment.py --provider gemini` against `scripts/serve_demo.py` (the same
single-process app the container runs) on the founder's Windows machine. Output: `verify_deployment_gemini_20261118.log`.

| Item | Value |
|---|---|
| Incident | `inc_7ddeca473e`, family `payment_entitlement` / `stale_price_id`, fault `duplicate_delivery` |
| Decision maker | **live Gemini** `gemini-3.1-flash-lite` (free tier), not the deterministic baseline |
| Model calls / tokens | 14 calls · 48,345 input · 918 output tokens · cost not measured (free tier) |
| Tool sequence | get_incident → billing_find_customer → compare_billing_vs_entitlement → record_hypotheses → billing_list_events → webhooks_list_deliveries → entitlements_processed_event → record_hypotheses → repo_list_files → repo_read_file ×2 → record_hypotheses → submit_diagnosis → propose_patch |
| Diagnosis | paid price id missing from the tenant's plan mapping (correct per hidden ground truth) |
| Patch | 1 changed line in `tenants/<tenant>.json`, policy risk low; suite passed; generated regression test failed on unpatched code |
| Human gate | stopped at `awaiting_approval`; approved by the check script (`deployment-check`), not auto-approved |
| Verification | independent verifier PASS: invoice paid, exactly one successful charge, no duplicate invoice, entitlement = pro, granted once despite duplicate delivery |
| Time | intake 23:09:34Z → report 23:09:57Z (about 23 s including the approval) |
| Result | 15/15 checks passed; the ledger-outage check in the same script uses the deterministic baseline |

One run is a demonstration, not a reliability measurement; the reliability figures are in
[`competition/TECHNICAL_EVIDENCE.md`](../../competition/TECHNICAL_EVIDENCE.md).

## Second live run: screenshot capture, 2026-11-18
`inc_2376f4f829`, same family and fault, `gemini-3.1-flash-lite`, driven through the dashboard by
`frontend/scripts/capture-screenshots.mjs` on a local judge-demo server. 13 model calls · 43,921 input / 765 output
tokens · approved through the human-approval step by the capture script as "Demo reviewer" (the gate was used; auto-approval was off) · VERIFIED. Screenshots and metadata:
`competition/screenshots/` (`capture.json`).
