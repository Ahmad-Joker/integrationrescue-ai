# Evaluation plan

Harness: `python -m integrationrescue.evaluation [--provider deterministic|claude] [--seeds ...]`. Every incident is
built fresh, run end-to-end with policy auto-approval (labelled as such), then scored against hidden ground truth and an
independent re-verification. Results are saved to `var/eval/*.json` and shown in the Evaluation lab.

## Metrics recorded per run
correct diagnosis (affected file matches ground truth, or INDETERMINATE when expected) · reproduced · patch accepted ·
verified · **false VERIFIED** (VERIFIED but re-check fails or INDETERMINATE was expected) · duplicate charge · tool calls ·
denied tool calls · patch attempts · duration · model usage/cost.

## Latest recorded result (deterministic baseline, seeds 101 & 202, 2026-10-31)
| Family | Runs | Expected outcome reached | Correct diagnosis |
|---|---|---|---|
| payment_entitlement (3 variants + 1 held-out) | 8 | 8 VERIFIED | 8 |
| schema_drift (1 + 1 held-out) | 4 | 0 (DIAGNOSED; baseline does not attempt code fixes) | 4 |
| state_unavailable | 2 | 2 INDETERMINATE | 2 |

Totals: 14 runs, false VERIFIED 0, duplicate charges 0, mean 11.7 tool calls, ~4.3 s per incident.
This measures the **baseline**, not the LLM agent. The live agent has not been evaluated (no credentials).

## Internal targets (8 families) — not yet achievable: only 3 families exist
≥7 diagnosed · ≥6 repaired & verified · indeterminate classified correctly · 0 false VERIFIED · 0 unauthorised
high-impact actions · 0 duplicate payments · resumability demonstrated (covered by a test).

## Baselines to compare
1. Deterministic troubleshooting baseline (exists).
2. Live IntegrationRescue (Claude provider) — pending credentials.
3. General coding agent with the same repo + read-only API access and the same verifier — pending; plan: export the
   incident (ticket, repo copy, API base URL) and score its final repo state with `verify()` after replay.

## Held-out discipline
Held-out variants live in `ScenarioFamily.heldout_variants`; variant names never reach the agent (incident ids are
random, files are named by tenant). Add new held-out variants before tuning prompts on a family.
