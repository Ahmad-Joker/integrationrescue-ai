# Limitations (as of 2026-11-18)

IntegrationRescue is a **competition prototype** that runs on simulated integrations with fictional data. It is not
production-ready and has no customers, pilots or revenue.

## What the evidence does and does not show
| Claim | Status |
|---|---|
| Live Gemini diagnoses the five incident families correctly | 31/31 scored live runs (3 evaluation runs, free-tier `gemini-3.1-flash-lite`) |
| Live Gemini repairs **configuration** defects end to end | 11/11 scored runs after the edit-schema fix (8 payment mapping + 3 signing-key rotation); 2/8 before the fix |
| Live Gemini repairs **code** defects | **Not established**: 1 VERIFIED in a standalone run, 0 of 5 scored evaluation runs |
| No false success claims, no duplicate charges | 0 and 0 across all 72 recorded evaluation runs (36 baseline; 36 live, of which 31 scored and 5 excluded as infrastructure errors) |
| Comparison against a general coding agent | **Not run.** The harness and protocol exist (`competition/COMPARISON_PROTOCOL.md`); no results |
| Real-world problem frequency, willingness to pay | **Not validated**: no interviews yet (`competition/PROBLEM_VALIDATION_PLAN.md`) |

Samples are small (2 seeds per variant) and use one cheap model on a free tier, with rate limits that interrupt runs.
Treat the rates as indicative, not as statistically robust reliability figures.

## Product scope
- Simulated billing, webhooks, entitlements and logs only. There is no connector to Stripe, Chargebee, Salesforce or
  any real system, and no CRM simulator yet.
- 5 of 8 planned incident families. Missing: CRM field mapping, duplicate side effect, and one more.
- Screenshots are stored but not analysed (no vision step). No browser reproduction of the customer app.
- One customer-repo template (Python). Real customer stacks vary widely.

## Model and reliability
- The live demo depends on Google's free tier: about 20 requests per day per model on the stronger models. Runs can
  stop with HTTP 429/503. These are reported as infrastructure errors, never as fixes. A paid tier or stronger model
  is a founder decision.
- Claude support is implemented but only tested with a fake client (no Anthropic key).
- Model behaviour can change across model versions; the policy layer, not the prompt, is what holds the safety line
  (for example, the signing-key announcement check was moved into code after the model ignored the prompt).

## Security
- Customer code runs in child processes with an allow-listed environment and, on Linux, CPU, memory, file-size and
  open-file limits. There is no filesystem or network isolation per run. That is fine for the bundled fictional repo,
  but real customer code would need a VM-grade sandbox.
- Forbidden-construct checks on code patches are regex-based. The test suite, regression test and replay
  verification are the real gate.
- The public demo uses one shared access code with no user accounts. Approver names are self-declared.
- Rate limits and caps are in-process: they reset on restart and do not coordinate across several instances. Deploy a
  single instance.

## Operations
- No deployment exists yet. State is ephemeral: a restart wipes the fictional incidents and re-seeds the examples.
- No monitoring or alerting beyond the platform health check and the per-incident audit timeline.
- Windows is the development platform. Linux is exercised in CI and in the container.
