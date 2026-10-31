# Test history

| Date | Scope | Result | Notes |
|---|---|---|---|
| 2026-10-31 | backend pytest (first suite) | 55 passed | first run, no failures |
| 2026-10-31 | backend pytest | 61 passed (115 s) | + API, families, Claude adapter protocol |
| 2026-10-31 | ruff | clean | |
| 2026-10-31 | frontend lint + build | clean | |
| 2026-10-31 | Playwright | 1 failed → 2 passed | failure was an ambiguous test locator (app showed correct INDETERMINATE); locator fixed, app unchanged |
| 2026-10-31 | eval deterministic seeds 101,202 | 14 runs, 10/14 expected outcome, 0 false VERIFIED, 0 duplicate charges | 4 misses = schema_drift code fixes not attempted by baseline |
| — | GitHub Actions | not run | no remote |
| — | live Claude | not run | no credentials |
