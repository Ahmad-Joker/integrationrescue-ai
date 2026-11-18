# Judge access

> **Public URL: not yet deployed.** The founder fills this in after deployment and a passing
> `scripts/verify_deployment.py` run ([USER_ACTIONS.md](../competition/USER_ACTIONS.md) A4–A5).

| | |
|---|---|
| URL | [PLACEHOLDER: public demo URL] (only after `verify_deployment.py` passes against it) |
| Access code | sent privately with the submission (never in this public repository) |
| Data | every customer, payment, webhook and log is simulated and fictional |
| Availability | [PLACEHOLDER: host and plan]. On the free Render plan the service sleeps when idle, so the first load can take about a minute |
| Contact if it is down | [PLACEHOLDER: founder email] |

## Five-minute tour
1. Open the URL. The purple banner confirms that this is a simulation. Enter the access code and press **Unlock**.
2. **Dashboard** has two pre-seeded examples, both from the *deterministic baseline* (labelled, not the AI). One
   waits at the approval gate, so you can review its repair and approve it yourself.
3. **New incident** → choose **"Paid for Pro, still on Free"** → *Decision maker: Live AI agent (Gemini)* →
   **Create and investigate**. The run is not scripted: it takes roughly 20–90 seconds and usually 12–20 model calls.
4. **Investigation** tab: every tool call, its arguments and its rationale, plus hypotheses being confirmed or refuted.
5. **Repair** tab: the one-line diff, the policy risk, the test suite, the generated regression test (it must *fail* on
   the unpatched code), and the sandbox replay. Enter your name and **Approve & promote**. Nothing reaches the live
   simulation without this click.
6. **Verification** tab: the independent verifier's checks (paid plan, exactly one charge, granted once), each with
   expected and observed values, plus the same checks failing before the fix.
7. Try a failure case: **"Billing ledger unavailable"** should end **INDETERMINATE**, never VERIFIED.
   **"Timeout alerts after a double click"** should end **NO ACTION NEEDED**, with no patch.
8. **Evaluation lab**: all recorded evaluation runs, with live Gemini and the baseline shown separately.

## Limits you may hit
- 15 live-model incidents per day across all judges. After that the baseline still works and says so.
- 3 investigations at once, and 30 actions per minute per visitor.
- If Google's free tier is overloaded, the incident shows **MODEL UNAVAILABLE**. That is an infrastructure failure,
  never a claimed fix. Retry later or use the baseline.
- The code-repair scenario (schema drift) is experimental: the live model rarely completes it (see TECHNICAL_EVIDENCE).

## Running it yourself instead
See [DEPLOYMENT.md](DEPLOYMENT.md): `docker run`, or `scripts/serve_demo.py` with your own `GEMINI_API_KEY`.
