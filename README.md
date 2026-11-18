# IntegrationRescue

**The AI agent that investigates broken software integrations, safely repairs them, and proves the actual business outcome.**

A customer pays for Pro. Billing says *succeeded*, the webhook returns *202 Accepted*, and the customer is still on Free.
IntegrationRescue investigates incidents like this with real tools against running services, reproduces the failure in an
isolated copy, tests a minimal repair, waits for a human to approve it, and only reports **VERIFIED** when an independent
verifier confirms the business state (correct plan, exactly one charge, exactly one grant).

> **Status:** competition prototype for the Create AI Agents Championship (Best Business AI Agent), built by Ahmad
> Essam Abdelaziz (BSc Artificial Intelligence student, AAST; based in Egypt). All services are simulated and all data is
> fictional. No customers, pilots or deployment yet. Submission window: 4 December 2026 – 4 January 2027.
> See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Competition submission
| | |
|---|---|
| Judge access | [docs/JUDGE_ACCESS.md](docs/JUDGE_ACCESS.md). Public URL: **not yet deployed** (deployment-ready: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)) |
| Agent Card | [competition/AGENT_CARD.md](competition/AGENT_CARD.md) |
| Evidence | [competition/TECHNICAL_EVIDENCE.md](competition/TECHNICAL_EVIDENCE.md) · raw results [evidence/](evidence/) · tests [docs/VERIFICATION_REPORT.md](docs/VERIFICATION_REPORT.md) |
| Safety and oversight | [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) · [docs/LIMITATIONS.md](docs/LIMITATIONS.md) |
| Live demo | [docs/LIVE_DEMO_RUNBOOK.md](docs/LIVE_DEMO_RUNBOOK.md) · [competition/DEMO_SCRIPT_2_MIN.md](competition/DEMO_SCRIPT_2_MIN.md) |
| Pitch | [competition/PITCH_SCRIPT_6_MIN.md](competition/PITCH_SCRIPT_6_MIN.md) · deck (final-design candidate awaiting founder assets): [competition/IntegrationRescue_Competition_Deck.pptx](competition/IntegrationRescue_Competition_Deck.pptx), [spec](competition/PITCH_DECK.md), [QA](competition/DECK_QA.md) · [competition/BUSINESS_MODEL_CANVAS.md](competition/BUSINESS_MODEL_CANVAS.md) |
| Validation | plan and interview kit: [competition/PROBLEM_VALIDATION_PLAN.md](competition/PROBLEM_VALIDATION_PLAN.md). **No interviews completed yet** |
| CI | latest green run: [44201542793](https://github.com/Ahmad-Joker/integrationrescue-ai/actions/runs/44201542793) on `a3ffbcd` (backend, frontend, container) |
| Readiness | [competition/SUBMISSION_READINESS.md](competition/SUBMISSION_READINESS.md) · founder actions [competition/USER_ACTIONS.md](competition/USER_ACTIONS.md) · placeholders [competition/PLACEHOLDER_REGISTER.md](competition/PLACEHOLDER_REGISTER.md) |

## What the evidence shows (recorded, reproducible)
- **Live Gemini agent** (`gemini-3.1-flash-lite`, free tier) diagnosed 31/31 scored incidents correctly across 3
  evaluation runs. After the edit-schema fix it reached the correct outcome in 16/17 runs: 11/11 configuration and
  trust-change repairs VERIFIED, 3/3 no-action cases, 2/2 outages INDETERMINATE.
- **Code repair by the live model is not established** (0/5 scored runs; 1 standalone success).
- **0 false success claims and 0 duplicate charges** in all 72 recorded runs (36 baseline, 36 live).
- The **deterministic baseline** (rule-based, *not* an LLM) gets 18/22 on 5 families and is used for CI and comparison.

## How it works
Intake → investigate (hypotheses + typed, phase-gated tools) → reproduce in an isolated copy → patch (policy check,
sandbox tests, a regression test that must fail before and pass after, sandbox replay) → **human approval** → promote →
**independent read-only verification** → report. Outcomes: `VERIFIED`, `NO_ACTION_NEEDED`,
`PATCH_TESTED_NOT_VERIFIED`, `DIAGNOSED`, `INDETERMINATE`, `ESCALATED`, `FAILED`. The model chooses evidence, hypotheses
and repairs. Deterministic code enforces permissions, budgets, sandboxing, approval and verification.

Implemented: simulated billing, entitlements, webhook delivery (retries, duplicates, lost acks) and logs on SQLite;
5 incident families (payment mapping, schema drift, ledger outage, signing-key rotation, ack timeout); live Gemini
provider, Claude provider (fake-client tested only) and the baseline; prompt-injection and policy tests; dashboard;
evaluation harness with held-out variants; coding-agent comparison harness; public demo mode with access code,
limits and reset; container image.
Not yet: vision analysis of screenshots, 3 of 8 planned families (CRM field mapping needs a CRM simulator), per-run
OS isolation for customer code, a coding-agent comparison run, deployment. See [docs/NEXT_ACTIONS.md](docs/NEXT_ACTIONS.md).

## Quick start (Windows PowerShell)
```powershell
./scripts/dev.ps1 install
./scripts/dev.ps1 backend     # terminal 1  -> http://127.0.0.1:8000/docs
./scripts/dev.ps1 frontend    # terminal 2  -> http://127.0.0.1:5173
./scripts/dev.ps1 test        # backend tests + lint + frontend build + browser tests
```
Judge-demo mode locally (one process, like the container): `./scripts/dev.ps1 judge-demo` → http://127.0.0.1:8080.
Container: `docker build -t integrationrescue .` then
`docker run -p 8000:8000 -e IR_ACCESS_TOKEN=<16+ chars> integrationrescue`.

Live model: put `GEMINI_API_KEY` in `.env` (git-ignored) and choose "Live AI agent (Gemini)", or run
`python -m integrationrescue.demo --provider gemini`. Recorded live runs used `IR_GEMINI_MODEL=gemini-3.1-flash-lite`.
The free tier has per-model daily request limits. Calls per incident are capped by `IR_MAX_LLM_CALLS` (30).
Live calls never run in CI.

## Docs
[Architecture](docs/ARCHITECTURE.md) · [Security model](docs/SECURITY_MODEL.md) · [Evaluation](docs/EVALUATION_PLAN.md) ·
[Deployment](docs/DEPLOYMENT.md) · [Verification report](docs/VERIFICATION_REPORT.md) · [Status](docs/PROJECT_STATUS.md) ·
[Competition materials](competition/)
