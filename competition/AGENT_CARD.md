# Agent Card: IntegrationRescue

| | |
|---|---|
| **Name** | IntegrationRescue |
| **Version** | 0.1.0 (competition prototype, 2026-11-18) |
| **Purpose** | Investigates a broken SaaS integration ("paid but still on Free"), tests a bounded repair in isolation, and, after human approval, proves the business outcome with an independent verifier. |
| **Target user** | Integration, support or platform engineers at B2B SaaS companies that connect billing to product access. The buyer would be the head of engineering, support or revenue operations (hypothesis, unvalidated). |
| **Problem** | A transaction "succeeds" in every system (card charged, webhook 202) while the business action silently fails. Engineers trace it by hand across billing, webhooks, sync code and entitlement data. |
| **Deployment mode** | Single container with simulated services and fictional data. Not deployed yet (see `docs/JUDGE_ACCESS.md`). Local and CI runs only so far. |
| **Owner / contact** | Ahmad (founder) · `<email to be added>` · repository: github.com/Ahmad-Joker/integrationrescue-ai |

## Inputs
Support ticket text and optional uploads (logs, JSON, screenshots), all treated as **untrusted data**. Read-only
access to the simulated billing ledger, webhook deliveries, entitlements and logs. Read access to allow-listed files
of the customer's integration repo.

## What the model decides vs what code enforces
| The model (live Gemini) decides | Deterministic code enforces |
|---|---|
| which evidence to gather and in what order | which tools exist in each phase (typed, `extra="forbid"`) |
| hypotheses, and when they are confirmed or refuted | budgets: 40 tool calls, 3 patch attempts, 30 model calls per incident |
| the root cause and the affected file | patch allow-list (`tenants/*.json`, `sync/*.py`), ≤5 edits, ≤40 lines, no tests or conftest |
| the repair (or that no repair is needed, or that it cannot tell) | trust changes need billing's own announcement (signing keys) |
| | sandbox tests, a fail-before/pass-after regression test, and sandbox replay |
| | human approval before promotion; independent verification after |

## Tools (18 diagnostic, 6 control/terminal)
Billing lookups (customers, invoices, charges, prices, events), webhook deliveries, entitlement and processed-event
state, log search, billing-vs-entitlement comparison, repo list/read, hypothesis recording, plus control tools:
`record_hypotheses`, `submit_diagnosis`, `propose_patch`, `report_no_action_needed`, `declare_indeterminate`, `escalate`. All are
GET-only against the simulators (`dry_run_handler` and `run_repo_tests` run the customer code in a limited child process; results are returned, never applied). No tool can write to billing, create a charge, or mark anything verified.

## Permitted actions
Read the simulated systems. Propose a patch to a sandbox copy. Replay a stored billing event in a sandbox.
Conclude NO ACTION NEEDED (accepted only if the verifier agrees) or INDETERMINATE.

## Prohibited actions (enforced in code, not only by the prompt)
Editing tests, the verifier or files outside the allow-list. Reading `.env`, keys, `.git` or absolute paths.
Creating charges (replay redelivers stored events only). Promoting without a human. Marking itself VERIFIED.
Trusting a signing key that billing never announced. Network access beyond the local simulator origin.

## Data
Fictional customers and payments generated per incident in SQLite. Tool output is redacted (keys, tokens) and
truncated before reaching the model. No personal data from real people is used; the generated regression test
keeps only the event envelope (no email).

## Human approval points
1. Every repair, after sandbox evidence is shown (diff, risk, tests, regression test, replay). Approve or reject.
2. Medium-risk patches (trust changes) carry an explicit "confirm with the billing provider" note.
3. On the public demo, auto-approval is disabled. The evaluation harness auto-approves and labels it as such.

## Verification method
`verification/verifier.py` opens the simulated database **read-only**. It derives the expected plan from the
billing ledger, never from agent output, and asserts: invoice paid, exactly one successful charge, no duplicate
invoice, entitlement = paid plan, granted exactly once for the event. Only a PASS here can produce VERIFIED.

## Model / provider
Live: Google Gemini via function calling (`gemini-3.1-flash-lite` for all recorded live runs; free tier).
Claude (Anthropic tool use) is implemented but only tested with a fake client. A deterministic rule-based baseline
exists for tests, CI and comparison. **It is not an LLM and is always labelled as the baseline.**

## Failure states
VERIFIED · NO ACTION NEEDED · PATCH TESTED, NOT VERIFIED · DIAGNOSED (no safe repair) · INDETERMINATE (source of
truth unavailable) · ESCALATED · FAILED (orchestrator error). Model outages are shown as MODEL UNAVAILABLE with
kind infrastructure/budget/model, and never count as success.

## Monitoring
A per-incident append-only audit timeline (every tool call, denial, policy decision, approval and verification),
token and call usage per incident, a health endpoint, and container health checks. No alerting yet.

## Test evidence
- Backend tests: `backend/tests` (unit, integration, adversarial, prompt injection, demo mode, provider failures).
  CI: `.github/workflows/ci.yml`. Results: `docs/VERIFICATION_REPORT.md`.
- Evaluations: `competition/TECHNICAL_EVIDENCE.md`; raw files in `evidence/eval/`.
- Live end-to-end run: `evidence/live/README.md`.

## Risk rating: **Medium** (for the prototype as deployed with fictional data: **Low**)
Residual risks:
- Customer code runs without filesystem or network isolation (resource limits only), so it must not be used with
  real customer code.
- Live code repair is unreliable (0/5 scored). The agent usually stops at DIAGNOSED, which is safe but less useful.
- Small evaluation samples on one free-tier model.
- Shared access code, no per-user identity.
- Regex-based code-patch screening.
- Prompt-injection resistance is tested on one injected-ticket variant (2/2 live), which is not a guarantee.

Full list: `docs/LIMITATIONS.md` · `docs/SECURITY_MODEL.md`.
