# Live demo runbook (real Gemini agent)

Goal: show the **live Gemini agent**, not the baseline, solving one fictional incident end to end, with the human
gate and independent verification visible. The run is real, so its exact path varies; never script the result.

## 1. Configuration
| Variable | Value | Notes |
|---|---|---|
| `GEMINI_API_KEY` | your Google AI Studio key | secret; `.env` locally, platform secret when deployed |
| `IR_GEMINI_MODEL` | `gemini-3.1-flash-lite` | the model all recorded live results used; free-tier quotas are per model |
| `IR_PROVIDER` | `gemini` | makes Gemini the default in the New incident form |
| `IR_MAX_LLM_CALLS` | `30` | the selected incident usually needs 12–18 calls |
| `IR_ACCESS_TOKEN` / `IR_ADMIN_TOKEN` | generated codes | demo mode only |

Check quota before recording: in Google AI Studio, see your rate limits and usage for the model. One incident uses
about 12–20 requests, and the free tier allows roughly 20 requests per day on the stronger models (higher on lite
models; check the console, limits change). Plan **one rehearsal plus one recording per day per model**, or use two
models.

## 2. Setup
- **Local** (recommended for recording): `npm run build --prefix frontend`, then
  `.venv\Scripts\python scripts\serve_demo.py` → http://127.0.0.1:8080. Codes print in the terminal if not set.
- **Deployed**: open the public URL and enter the access code (see `docs/JUDGE_ACCESS.md`).
- Reset first: delete `var\demo` (local) or call `POST /api/admin/reset` with the admin code (deployed).
- Browser at 1920×1080, zoom 110%, dark or light theme (both are tested), notifications off.

## 3. Selected incident
**"Paid for Pro, still on Free"**: `payment_entitlement` / `stale_price_id`, fault *duplicate webhook delivery*.
- Why this one: it has the strongest live record (8/8 scored runs VERIFIED in live run 2, plus the 2026-11-18
  end-to-end run in `evidence/live/`). The business impact is obvious, and the duplicate delivery makes the "exactly one
  grant" check meaningful.
- Backup incidents with live records: "Billing rotated its webhook signing key" (3/3), and "Timeout alerts after a
  double click" (3/3 NO ACTION NEEDED). **Do not** demo schema drift live: live code repair is not reliable (0/5 scored).

## 4. What you should see (typical, not guaranteed)
1. Mode banner: **LIVE AI AGENT … (gemini)**. If it says DETERMINISTIC, stop: wrong provider.
2. Investigation: the agent reads the ticket, looks up the customer, then calls `compare_billing_vs_entitlement`
   (paid Pro vs entitlement Free). It records hypotheses (not delivered / handler crashed / mapping missing), checks
   events and webhook deliveries (delivered, 202), the processed-event record, then lists and reads the repo and tenant
   config. It confirms the mapping hypothesis and submits a diagnosis naming `tenants/<tenant>.json`.
3. Reproduction: "failure reproduced in isolation". Replaying the stored event in a sandbox still leaves Free.
4. Patch: one changed line in the tenant config, policy risk **low**, suite PASS, regression test FAILS on unpatched
   code, sandbox replay verification PASS. The order of tool calls and the number of patch attempts can differ.
5. **Human approval point**: the incident waits at *awaiting approval*. Type your name and click **Approve & promote**.
6. Independent verification: invoice paid ✓, exactly one successful charge ✓, no duplicate invoice ✓, entitlement =
   pro ✓, granted once for the event ✓ (despite the duplicate delivery). Outcome **VERIFIED**.
7. Report tab: model usage (calls, tokens) and limitations.

If the model takes a different but valid path (for example, reading logs first), let it run. That is the point of
an agent. If it ends DIAGNOSED (three rejected patches), say so on camera and use the backup recording.

## 5. Quota and failure fallback
- **MODEL UNAVAILABLE** banner (429/503): Google-side. Wait about 1 minute and retry with a new incident, or switch
  `IR_GEMINI_MODEL` to another model with remaining quota and restart.
- Daily quota exhausted: use the pre-recorded live run (see `competition/DEMO_BACKUP_PLAN.md`), clearly captioned
  with its recording date. Never substitute a baseline run while calling it AI.
- Deployed daily cap reached (15 live incidents): reset happens at midnight UTC, or raise
  `IR_MAX_LIVE_INCIDENTS_PER_DAY` and redeploy.

## 6. Reset after the demo
Local: stop the server and delete `var\demo`. Deployed: `POST /api/admin/reset` with `x-admin-token`.

## 7. Never claim
- that a baseline run is the AI agent, or that the live run was scripted or guaranteed;
- that it works on real customer systems, or has customers or pilots;
- reliability beyond the recorded numbers (`competition/TECHNICAL_EVIDENCE.md`), especially code repair;
- that the agent marks things fixed: only the independent verifier can produce VERIFIED.

## 8. Re-checking the live path from a terminal
```powershell
$env:IR_ACCESS_TOKEN = "<access code>"
.venv\Scripts\python scripts\verify_deployment.py --url http://127.0.0.1:8080 --provider gemini
```
This must print `15/15 checks passed`. Recorded example: `evidence/live/README.md`.
