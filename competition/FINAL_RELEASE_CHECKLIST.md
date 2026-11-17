# Final release checklist (2026-11-18)

Results of the release gate run in this session. Details and exact commands: [docs/VERIFICATION_REPORT.md](../docs/VERIFICATION_REPORT.md).

| # | Gate | Result |
|---|---|---|
| 1 | All relevant automated checks re-run | ✅ backend (Windows + Linux), frontend lint/build, Playwright, audits, container |
| 2 | Frontend production build | ✅ `tsc -b && vite build` |
| 3 | Backend tests | ✅ Windows: 117 passed, 2 skipped (POSIX-only) · Linux (container image): 119 passed, 0 skipped |
| 4 | Lint and type checks | ✅ ruff (backend + scripts), oxlint, TypeScript via `tsc -b`. No Python type checker is configured in this repo |
| 5 | Security and prompt-injection tests | ✅ `tests/adversarial`, `test_policy.py`, `test_edit_schema.py`, `test_demo_mode.py`, `test_provider_failures.py`, `test_child_limits.py` |
| 6 | Demonstration path locally | ✅ `verify_deployment.py` 15/15: local demo server (baseline), container (baseline), local demo server (live Gemini) |
| 7 | No secrets committed | ✅ scan of all tracked and new files for API-key patterns, the session's throwaway codes, personal email and local paths; `.env` ignored and excluded from the Docker context. Note: `.claude/launch.json` (already tracked) contains a local path; it is left out of the commit plan (USER_ACTIONS B5) |
| 8 | Internal links work | ✅ `python scripts/check_links.py` (45+ Markdown files, 0 broken) |
| 9 | No unsupported claims | ✅ figures cross-checked against `evidence/` via `scripts/summarize_evidence.py`; no market numbers, customers, pilots or testimonials; hypotheses labelled |
| 10 | Two-minute script fits | ✅ 218 words ≈ 1:33 at 140 wpm (`scripts/script_timing.py`) |
| 11 | Six-minute script fits | ✅ 2:00 demo + 451 words ≈ 3:13 at 140 wpm |
| 12 | `git diff` inspected | ✅ changes limited to the features and docs listed in the session report |
| 13 | `git status` inspected | ✅ nothing deleted; no history rewritten; committed and pushed after founder OK; run 44201180724 green |
| 14 | This checklist | ✅ |
| 15 | SUBMISSION_READINESS final status | ✅ updated |

Not covered by this gate: a CI run on the new commit (needs the push), a public deployment, the recordings, customer
evidence.
