# Architecture

```
            ┌──────────────── React dashboard (frontend/) ────────────────┐
            │ dashboard · submit · investigation · repair · verify · eval │
            └───────────────────────────┬─────────────────────────────────┘
                                        │ /api
┌───────────────────────────────────────▼──────────────────────────────────────────┐
│ FastAPI product API (api.py)                                                     │
│   IncidentService ── _Run state machine (agent/orchestrator.py) ── Store (SQLite) │
│        │  decides: Provider ──► ClaudeProvider (live) | HeuristicProvider (det.)  │
│        │  enforces: tools.execute (typed, phase-gated, redacted, budgeted)        │
│        │            security.policy (paths, patch review)                          │
│        │            sandbox (copy repo, apply edits, pytest, replay)               │
│        │            verification.verify (read-only, independent)                   │
│        ▼                                                                           │
│ Simulator API (/sim/worlds/{id}/...) — GET-only for the agent                     │
└───────────────────────────────────────┬──────────────────────────────────────────┘
                                        │
      per-incident run dir var/runs/<id>/: world.db · repo/ · repro/ · sandbox/attempt_n/ · report.md
```

## Components
- **World** (`simulators/world.py`): one SQLite file per environment holding billing (customers, prices, invoices,
  charges with idempotency keys, events), webhook deliveries, entitlements (accounts, audit, processed events) and logs.
  A deterministic logical clock keeps runs reproducible. `clone_to()` snapshots an environment for sandbox replay.
  Faults: `duplicate_delivery`, `lost_ack`, `billing_ledger_unavailable`.
- **Sync service** (`simulators/sync_service.py`): the webhook receiver. Runs the *customer's* handler code in a child
  process (`python -I`, stripped env, timeout), validates returned actions, applies them, dedups by event id and — like
  many real receivers — answers 202 even when nothing was applied (the silent failure).
- **Customer repo** (`templates/entitlement_sync`): handler + tenant price→plan mappings + its own tests. Scenarios copy
  it per incident and inject defects.
- **Scenarios** (`scenarios/`): families with training and held-out variants; names/ids/prices randomised per seed.
  Ground truth stored separately (`incidents.hidden`) and read only by the evaluator.
- **Orchestrator** (`agent/orchestrator.py`): phases `intake → investigate → reproduce → patch → awaiting_approval →
  promote → verify_live → report → done`. Every step is checkpointed; promotion is idempotent and guarded by
  `done_steps`, so an interrupted run resumes without repeating side effects.
- **Providers** (`agent/providers.py`): `ClaudeProvider` runs a manual Messages-API tool-use loop (append-only history,
  every `tool_use` answered with a matching `tool_result`, call budget, refusal handling, server-side fallbacks);
  `HeuristicProvider` is a rule-based baseline following billing → webhook → sync → entitlement.
- **Verifier** (`verification/verifier.py`): opens the environment read-only, derives the expected plan from the paid
  invoice's price in the billing ledger, and asserts paid invoice, exactly one successful charge, no duplicate invoice,
  matching entitlement, exactly one grant for the event. Ledger unavailable/ambiguous → `INDETERMINATE`.

## Patch pipeline
propose (agent) → `review_patch` (allow-list, op types, plan values, forbidden code, size) → copy repo → apply →
generate regression test from the captured event + ledger (not from the agent) → regression must FAIL on unpatched
copy → full suite must PASS on patched copy → clone world, replay original event, verify → await human approval →
apply to incident repo, redeliver event → verify again.

## Key decisions
See [DECISION_LOG.md](DECISION_LOG.md). Notably: single orchestrator instead of multi-agent; no LangGraph (the state
machine is ~400 lines and fully inspectable); SQLite per environment for cheap cloning; deterministic baseline doubles as
CI fixture and evaluation baseline.
