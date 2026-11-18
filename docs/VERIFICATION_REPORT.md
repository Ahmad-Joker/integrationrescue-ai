# Verification report: 2026-11-18 (second pass)

| | |
|---|---|
| Base commit | `a3ffbcdba0db4a58ee4e0b870270b2e066b8d1a9` (CI run [44201542793](https://github.com/Ahmad-Joker/integrationrescue-ai/actions/runs/44201542793): backend, frontend, container all successful) plus this session's uncommitted changes (deck, pitch, validation kit, scripts, one test-diagnostics change, one UI fix) |
| Machine | Windows 11 Home (10.0.26200), Git Bash + PowerShell 5.1, Docker Desktop 29.9.2 |
| Python | 3.13.0 (venv) · 3.12.16 in the container image |
| Node / npm | 24.14.0 / 11.9.0 |
| Tools | ruff 0.17.3 · pytest · oxlint · TypeScript via `tsc -b` · Playwright 1.64.1 · pip-audit 2.10.1 · python-pptx 1.0.2 (dev only) · PowerPoint (slide rendering) |
| Live-provider calls this pass | **one** live Gemini incident (`inc_2376f4f829`, gemini-3.1-flash-lite, free tier, 13 calls) to capture the deck screenshots. No Claude calls. CI never calls a model |

## Results
| # | Command (repo root unless noted) | Result |
|---|---|---|
| 1 | `./scripts/dev.ps1 preflight` (new: ruff, pytest, frontend lint and build, docker build, refusal check, 15-check judge flow in the container) | **PREFLIGHT PASSED** (third run; see "Flaky failure" below) |
| 2 | `cd backend; ..\.venv\Scripts\python -m pytest -q -rs` (Windows) | **117 passed, 2 skipped** (POSIX-only resource-limit tests) |
| 3 | Same suite on Linux in the image: `docker run … integrationrescue:preflight python -m pytest` | **119 passed**, 0 skipped |
| 4 | `ruff check backend` · `ruff check scripts --config backend/pyproject.toml` | pass |
| 5 | `npm run lint --prefix frontend` · `npm run build --prefix frontend` | pass |
| 6 | `cd frontend; npx playwright test` | **3 passed** |
| 7 | `pip-audit --skip-editable` | no known vulnerabilities |
| 8 | `npm audit --omit=dev --audit-level=high` · full tree `--audit-level=critical` | 0 shipped vulnerabilities · full tree passes at critical (5 high: picomatch build-tool advisory, unchanged, documented) |
| 9 | `python -m integrationrescue.evaluation --seeds 101` (deterministic smoke) | 11 runs, expected outcome 9/11 (the 2 misses are schema_drift, by design), false VERIFIED 0, duplicate charges 0 |
| 10 | Container: `docker build`; refusal without access code; `verify_deployment.py` | build ok; refuses to start; **15/15** |
| 11 | `node frontend/scripts/capture-screenshots.mjs` against a live-Gemini judge demo | 14 screenshots; incident VERIFIED through the human-approval step |
| 12 | `python scripts/build_deck.py` + `scripts/render_deck.ps1` | 15 slides rendered; all inspected (DECK_QA.md); every notes page has an evidence source |
| 13 | `python scripts/check_links.py` | 54 Markdown files, 0 broken links |
| 14 | `python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md competition/PITCH_SCRIPT_6_MIN.md` | demo 236 words = 1:41 at 140 wpm (1:48 at 130); presentation 512 words = 3:39 at 140 wpm, full pitch 5:39 (5:56 at 130) |
| 15 | `python scripts/summarize_evidence.py` | reproduces TECHNICAL_EVIDENCE figures (unchanged) |
| 16 | Searches: false UAE-location phrases, stale CI runs, "every software company", secrets, local paths, the session's throwaway codes | none found in the changed files (see FINAL_RELEASE_CHECKLIST) |

## Flaky failure (reported, not hidden)
In the second preflight run, `tests/integration/test_demo_mode.py::test_judge_flow_requires_human_approval` failed
once. The summary line did not show the assertion because the preflight filtered its output. It did not reproduce in
the next four runs: the file alone (17 passed), all integration tests (56 passed), the full suite on Windows
(117 + 2 skipped), and the full suite on Linux (119). The preflight passed on its third run. The test was **not**
loosened. Instead, every assertion in it now carries the response text or phase/outcome details, its wait helper
reports the last timeline events on timeout, and the preflight prints `-rf --tb=short`, so a repeat will show the
cause. The likely cause is machine load (Docker Desktop's VM had just started) against a 120-second wait, but that
is unconfirmed.

## Changes verified in this pass
- Evaluation lab: runs excluded as infrastructure errors now show "—" instead of a diagnosis ✓ (build + Playwright).
- `scripts/deploy_preflight.ps1` (new) fixed after two script bugs found while running it: PowerShell 5.1 turned the
  expected refusal's stderr into a terminating error, and a quoting error.
- `scripts/record_demo.ps1`, `scripts/render_deck.ps1`: parse-checked; render_deck used for all deck previews.

## Not covered
No public deployment (needs the founder's Render account). CI has not run on this pass's changes (not pushed). One
live incident is a demonstration, not a reliability measurement. No Python type checker is configured.
