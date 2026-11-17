# Test history

| Date | Scope | Result | Notes |
|---|---|---|---|
| 2026-10-31 | backend pytest (first suite) | 55 passed | first run, no failures |
| 2026-10-31 | backend pytest | 61 passed (115 s) | + API, families, Claude adapter protocol |
| 2026-10-31 | ruff | clean | |
| 2026-10-31 | frontend lint + build | clean | |
| 2026-10-31 | Playwright | 1 failed → 2 passed | failure was an ambiguous test locator (app showed correct INDETERMINATE); locator fixed, app unchanged |
| 2026-10-31 | eval deterministic seeds 101,202 | 14 runs, 10/14 expected outcome, 0 false VERIFIED, 0 duplicate charges | 4 misses = schema_drift code fixes not attempted by baseline |
| — | GitHub Actions | not run at the time (no remote) | superseded: see "first GitHub Actions runs" below |
| — | live Claude | not run | no credentials (still true) |

## 2026-10-31 — first GitHub Actions runs
- Run 41153893011: FAIL — backend `pip-audit` flagged the CI venv's bundled pip 25.0.1; frontend Playwright journey never
  reached approval because pytest (needed by the sandbox) was only a dev dependency. Real product bug.
- Fix 59e2a3a: pytest made a runtime dependency; missing test runner now escalates (new test); CI upgrades pip.
- Local: 62 backend tests pass, ruff clean. Run 41154637560: PASS (backend and frontend).

## 2026-10-31 — first live-model evaluations (Gemini free tier)
- Run 1 (`eval_gemini_20261031_230613`): diagnosis 14/14, VERIFIED 2/12; found edit-schema ambiguity and an
  orchestrator TypeError on malformed `replace` edits.
- Fix: per-op Edit validation + policy guard; `test_edit_schema.py` (7 tests). Backend: 79 tests pass, ruff clean.
- Run 2 (`eval_gemini_20261031_232820`): payment_entitlement 8/8 VERIFIED, 3 Google-side infra errors excluded,
  false VERIFIED 0, duplicate charges 0.

## 2026-11-01 — families 4 and 5
- Added signing_key_rotated and ack_timeout (+ `report_no_action_needed`, outcome NO_ACTION_NEEDED). Found and fixed:
  regression fixtures dropped envelope fields (`signing_key_id`), so a correct key-rotation patch failed its own test.
- Backend: 89 tests pass, ruff clean; frontend lint/build clean. Baseline eval 22 runs: 18/22 expected, 0 false claims.

## 2026-11-18 — submission-readiness pass
- New: public demo mode (`test_demo_mode.py`), provider-failure labelling (`test_provider_failures.py`), POSIX resource
  limits (`test_child_limits.py`), comparison harness (`test_comparison.py`), Playwright featured-preset journey.
- Backend: Windows 117 passed + 2 POSIX-only skips; Linux (container image) 119 passed, 0 skipped.
  ruff clean. Frontend lint/build clean; Playwright 3 passed.
- Found and fixed: Playwright backend read the developer's `.env` (two accidental live incidents, free tier);
  ambiguous locator; CI npm-audit would fail on a new unfixable build-tool advisory.
- Container: built locally, refuses to start without an access code, `verify_deployment.py` 15/15.
- Live Gemini end-to-end on the local demo server: 15/15, VERIFIED (`evidence/live/`).
- GitHub Actions: run 44201180724 on `7b04941` green (backend, frontend, container: image build + judge-flow check).
