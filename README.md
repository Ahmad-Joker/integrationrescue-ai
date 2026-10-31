# IntegrationRescue

**The AI agent that investigates broken software integrations, safely repairs them, and proves the actual business outcome.**

A customer pays for Pro. Billing says *succeeded*, the webhook returns *202 Accepted*, and the customer is still on Free.
IntegrationRescue investigates incidents like this with real tools against running services, reproduces the failure in an
isolated copy, tests a minimal repair, and only reports **VERIFIED** when an independent verifier confirms the business
state (correct plan, exactly one charge, exactly one grant).

> Status: competition prototype. Local simulated services with fictional data. See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md).

## What works today (verified by tests)
- Simulated billing, entitlements, webhook delivery (retries, duplicates, lost acks) and logs on SQLite, with an HTTP API
- A fictional customer integration repo whose tenant mapping / handler code contains injected defects
- Durable investigation state machine: intake → investigate (hypotheses + tools) → reproduce → patch → policy check →
  sandbox tests → fail-before/pass-after regression test → sandbox replay verification → human approval → promote → independent verification → report
- Outcomes: `VERIFIED`, `PATCH_TESTED_NOT_VERIFIED`, `DIAGNOSED`, `INDETERMINATE`, `ESCALATED`, `FAILED`
- Three decision makers behind one interface: **live Gemini** (function calling), **live Claude** (tool use) and a
  **deterministic rule-based baseline** (offline, clearly labelled, used in CI)
- Security: typed tools, phase-gated permissions, path allow-lists, patch policy, redaction, local-origin allow-list, prompt-injection tests
- Dashboard: incidents, submission with evidence upload and fault injection, live investigation, repair review & approval, verification, report, evaluation lab
- Evaluation harness scored against hidden ground truth including held-out variants

Not yet: vision analysis of screenshots, 3 of the 8 planned incident families (CRM field mapping needs a CRM simulator), deployment. See [docs/NEXT_ACTIONS.md](docs/NEXT_ACTIONS.md).

## Quick start (Windows PowerShell)
```powershell
./scripts/dev.ps1 install
./scripts/dev.ps1 backend     # terminal 1  -> http://127.0.0.1:8000/docs
./scripts/dev.ps1 frontend    # terminal 2  -> http://127.0.0.1:5173
./scripts/dev.ps1 demo        # or run the first incident in the terminal
./scripts/dev.ps1 test
```
Live model mode: put `GEMINI_API_KEY` (Google AI Studio) or `ANTHROPIC_API_KEY` in `.env` (git-ignored) and choose
"Live AI agent" in the UI, or `python -m integrationrescue.demo --provider gemini|claude`. Defaults: `gemini-2.5-flash`
(`IR_GEMINI_MODEL`; the free tier has per-model daily request limits), `claude-opus-5-5` (`IR_MODEL`); call budget
`IR_MAX_LLM_CALLS` (30 per incident).

## Docs
[Architecture](docs/ARCHITECTURE.md) · [Security model](docs/SECURITY_MODEL.md) · [Evaluation](docs/EVALUATION_PLAN.md) ·
[Competitors](docs/COMPETITOR_RESEARCH.md) · [Requirements](docs/PRODUCT_REQUIREMENTS.md) · [Competition materials](competition/)
