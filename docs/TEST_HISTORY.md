# Test history

| Date | Scope | Result | Notes |
|---|---|---|---|
| 2026-10-31 | backend pytest (first suite) | 55 passed | first run, no failures |
| 2026-10-31 | backend pytest | 61 passed (115 s) | + API, families, Claude adapter protocol |
| 2026-10-31 | ruff | clean | |
| 2026-10-31 | frontend lint + build | clean | |
| 2026-10-31 | Playwright | 1 failed â†’ 2 passed | failure was an ambiguous test locator (app showed correct INDETERMINATE); locator fixed, app unchanged |
| 2026-10-31 | eval deterministic seeds 101,202 | 14 runs, 10/14 expected outcome, 0 false VERIFIED, 0 duplicate charges | 4 misses = schema_drift code fixes not attempted by baseline |
| â€” | GitHub Actions | not run | no remote |
| â€” | live Claude | not run | no credentials |

## 2026-10-31 — first GitHub Actions runs
- Run 41153893011: FAIL — backend `pip-audit` flagged the CI venv's bundled pip 25.0.1; frontend Playwright journey never
  reached approval because pytest (needed by the sandbox) was only a dev dependency. Real product bug.
- Fix 59e2a3a: pytest made a runtime dependency; missing test runner now escalates (new test); CI upgrades pip.
- Local: 62 backend tests pass, ruff clean. Run 41154637560: PASS (backend and frontend).
