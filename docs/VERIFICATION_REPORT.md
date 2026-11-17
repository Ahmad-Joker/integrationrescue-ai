# Verification report: 2026-11-18

| | |
|---|---|
| Base commit | `de04559c68973b37d808fb5ce8403afe0a7513d8` plus the uncommitted 2026-11-18 changes (this report describes the working tree that the proposed commits will contain) |
| Machine | Windows 11 Home (10.0.26200), Git Bash + PowerShell 5.1 |
| Python | 3.13.0 (project venv) · 3.12.16 in the container image (`python:3.12-slim`) |
| Node / npm | 24.14.0 / 11.9.0 |
| Tools | ruff 0.17.3 · pytest (runtime dependency) · oxlint · TypeScript 7 via `tsc -b` · Playwright 1.64.1 (Chromium) · pip-audit 2.10.1 · Docker 29.9.2 |
| Live-provider tests | **one** live Gemini end-to-end run (`gemini-3.1-flash-lite`, free tier, `verify_deployment.py --provider gemini`); no Claude calls. CI never calls a model |

## Results
| # | Command (from repo root unless noted) | Result |
|---|---|---|
| 1 | `cd backend; ..\.venv\Scripts\ruff check .` and `ruff check scripts --config backend/pyproject.toml` | pass |
| 2 | `cd backend; ..\.venv\Scripts\python -m pytest -o addopts="-p no:cacheprovider" -q -rs` (Windows) | **117 passed, 2 skipped** in 254 s. The skips are the POSIX-only resource-limit tests |
| 3 | Same suite on Linux inside the image: `docker run --rm -v <repo>/backend:/src:ro -w /src integrationrescue:local python -m pytest ...` | **119 passed, 0 skipped** in 273 s (Python 3.12.16), including the POSIX resource-limit tests |
| 4 | `npm run lint --prefix frontend` (oxlint) | pass, 0 warnings |
| 5 | `npm run build --prefix frontend` (`tsc -b && vite build`) | pass, about 248 kB JS (76 kB gzip) |
| 6 | `cd frontend; npx playwright test` | **3 passed** (approve → VERIFIED journey with duplicate delivery; ledger outage → INDETERMINATE; featured preset → NO ACTION NEEDED without a patch) |
| 7 | `.venv\Scripts\pip-audit --skip-editable` | no known vulnerabilities |
| 8 | `npm audit --prefix frontend --omit=dev --audit-level=high` | 0 vulnerabilities in shipped dependencies |
| 9 | `npm audit --prefix frontend` (full tree) | 5 high, all one advisory: picomatch ReDoS (GHSA-fc5q-39xc-vjpf), reached through Vite build tooling, no fixed release. CI now audits build tooling at `critical` (rationale in SECURITY_MODEL) |
| 10 | `docker build -t integrationrescue:local .` | pass; image 287 MB |
| 11 | `docker run --rm integrationrescue:local python -c "import integrationrescue.api"` (no access code) | refuses to start (ConfigError), as intended |
| 12 | Container in demo mode + `scripts/verify_deployment.py --url http://127.0.0.1:8090` | **15/15**; `HEAD /` 200; the 5 committed evaluation runs are visible in the Evaluation lab; runs as uid 10001; health check "healthy"; admin reset re-seeds 2 examples |
| 13 | `scripts/serve_demo.py` + `verify_deployment.py` (baseline) | 15/15 |
| 14 | `scripts/serve_demo.py` (live config) + `verify_deployment.py --provider gemini` | **15/15**, incident `inc_7ddeca473e` VERIFIED, 14 model calls ([evidence/live](../evidence/live/README.md)) |
| 15 | `python scripts/check_links.py` | 0 broken relative links |
| 16 | `python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md competition/PITCH_SCRIPT_6_MIN.md` | demo 218 words (1:33 at 140 wpm); presentation 451 words (3:13) |
| 17 | `python scripts/summarize_evidence.py` | reproduces every figure in TECHNICAL_EVIDENCE |

## Defects found and fixed during verification
1. **Playwright backend loaded the developer's real `.env` key.** A new test selected a featured preset whose
   recommended provider is Gemini, so two accidental live incidents started. They were cut off when the test
   server stopped and used a few free-tier requests, at no money cost. Fix: `IR_SKIP_DOTENV=1` in
   `frontend/playwright.config.ts`. The tests now pass on the baseline. Backend tests already had this isolation.
2. **Ambiguous browser-test locator** after adding featured incident cards with the same text as a fault checkbox.
   Fix: target the checkbox by role (same intent, not weakened).
3. **CI would fail today on `npm audit --audit-level=high`** (new picomatch advisory with no fix). Fix: separate
   audits for shipped and build-time dependencies (documented).
4. A test imported the old private `_child_env` helper, which moved to `security/child.py`. Updated the import; the
   assertion is unchanged.

## Warnings and limitations of this verification
- `ruff format --check` reports 31 files that would be reformatted. Formatting is not an enforced project check (only
  `ruff check`), so the code was not mass-reformatted, to keep the diff reviewable.
- No Python type checker (mypy/pyright) is configured. Typing is enforced only by Pydantic at runtime.
- **CI has not run on these changes** (not pushed). The last green CI run is for `de04559` (run 41254875454).
- The container was tested on Docker Desktop (Linux VM), not on the hosting platform. No public deployment exists.
- One live end-to-end run is a demonstration, not a reliability measurement.
- Local helper packages installed in the venv only (not project dependencies): `pyyaml` (validating workflow YAML)
  and `python-pptx` (building the deck draft).
