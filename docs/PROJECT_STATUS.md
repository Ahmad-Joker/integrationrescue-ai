# Project status — updated 2026-10-31

**Phase:** P0 core complete; P1/P2 partially complete. First non-negotiable milestone **met in deterministic mode**.

## Verified (tests executed 2026-10-31)
- Backend: 61 pytest tests pass (unit, integration, adversarial, API, Claude-adapter protocol), ruff clean.
- Frontend: oxlint clean, `tsc -b && vite build` succeeds, 2 Playwright tests pass (full approve→VERIFIED journey with
  duplicate-webhook fault; ledger outage → INDETERMINATE).
- Manual browser walkthrough of the same journey: no console errors.
- Evaluation recorded: see EVALUATION_PLAN.md.

## Implemented
Simulators (billing, entitlements, webhooks, logs) · sync service running customer code in child processes · scenario
families: payment_entitlement (4 variants), schema_drift (2), state_unavailable (1) · orchestrator with persistence,
resume, approval gate · 18 diagnostic tools + 5 control/terminal tools · Claude provider + deterministic baseline ·
sandbox + regression generation · independent verifier · reports · product API · dashboard (7 screens) · eval harness ·
CI workflow file.

## Known defects / limitations
- Live Claude mode never executed against the real API (no credentials) — adapter only tested with a fake client.
- Baseline cannot repair code defects (schema_drift ends DIAGNOSED) — by design, but it means no recorded code repair by an agent yet.
- Screenshots are stored but not analysed; no CRM simulator; 5 incident families missing.
- Child processes not OS-sandboxed; local API unauthenticated.

## CI
Workflow at `.github/workflows/ci.yml`; **never run** — no GitHub remote exists yet (needs founder approval).

## Deployment
None. Local only.
