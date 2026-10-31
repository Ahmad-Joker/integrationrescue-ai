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
This measures the **baseline**, not the LLM agent.

## Live run 1 — Gemini `gemini-3.1-flash-lite` (free tier), seeds 101 & 202, 2026-10-31
File `var/eval/eval_gemini_20261031_230613.json`. Same 14 incidents, same verifier, auto-approval (evaluation mode).
| Family | Runs | VERIFIED | Correct diagnosis | Other outcomes |
|---|---|---|---|---|
| payment_entitlement | 8 | 2 | 8 | 5 DIAGNOSED, 1 FAILED |
| schema_drift (code fix) | 4 | 0 | 4 | 3 DIAGNOSED, 1 FAILED |
| state_unavailable | 2 | — | 2 | 2 INDETERMINATE (correct) |

Totals: correct diagnosis 14/14, VERIFIED 2/12 fixable, false VERIFIED 0, duplicate charges 0, mean 16.9 tool calls,
14–23 model calls per incident. (Mean duration is not meaningful: the machine slept mid-run.)

**Failure analysis — mostly our tool design, not reasoning.** 9 of the 10 unrepaired incidents had a *correct* fix
idea. For config fixes the model put the plan in `new` instead of `value` on `json_set`; the policy answered
"unknown plan value None", which gave it nothing to correct, so it repeated the mistake. Two runs FAILED on an
orchestrator crash (a `replace` edit with no `old` reached the sandbox: TypeError). Code-fix attempts were blocked
for editing tests (policy, correct) or used replace text that did not match. Fixed: per-op edit validation with
actionable errors, field descriptions in the schema, and a policy-level guard (tests in `test_edit_schema.py`).
A separate single run on the same model repaired schema drift and reached VERIFIED (inc_f30a3b491b), the first
code repair by a live model.

## Live run 2 — same model and seeds, after the edit-schema fix, 2026-10-31
File `var/eval/eval_gemini_20261031_232820.json`. 14 incidents run; 3 hit Google-side errors (one 429 rate limit,
two 503 "high demand") and are reported as infrastructure errors, not scored.
| Family | Scored runs | VERIFIED | Correct diagnosis | Other outcomes |
|---|---|---|---|---|
| payment_entitlement (incl. held-out, injected ticket) | 8 | **8** (run 1: 2) | 8 | — |
| schema_drift (code fix) | 1 | 0 | 1 | 1 DIAGNOSED (3 rejected attempts) |
| state_unavailable | 2 | — | 2 | 2 INDETERMINATE (correct) |

Totals over 11 scored runs: correct diagnosis 11/11, expected outcome 10/11, false VERIFIED 0, duplicate charges 0,
mean 14.2 tool calls, ~63 s per incident. Code repair by the live model is **not yet established**: one VERIFIED in a
standalone run, zero in the evals, and only 1 scored schema_drift run here. Needs more runs (ideally a stronger model).

Earlier attempts on `gemini-3.5-flash` and `gemini-2.5-flash` hit the free tier's ~20 requests/day/model limit and
are excluded (moved to `var/eval/invalid/`); the eval now reports such quota failures as infrastructure errors.

## Internal targets (8 families) — not yet achievable: only 3 families exist
≥7 diagnosed · ≥6 repaired & verified · indeterminate classified correctly · 0 false VERIFIED · 0 unauthorised
high-impact actions · 0 duplicate payments · resumability demonstrated (covered by a test).

## Baselines to compare
1. Deterministic troubleshooting baseline (exists).
2. Live IntegrationRescue — Gemini recorded above; Claude pending credentials.
3. General coding agent with the same repo + read-only API access and the same verifier — pending; plan: export the
   incident (ticket, repo copy, API base URL) and score its final repo state with `verify()` after replay.

## Held-out discipline
Held-out variants live in `ScenarioFamily.heldout_variants`; variant names never reach the agent (incident ids are
random, files are named by tenant). Add new held-out variants before tuning prompts on a family.
