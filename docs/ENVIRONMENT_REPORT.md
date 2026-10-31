# Environment report

Inspected 2026-10-31 on the founder's machine (Windows 11 Home 10.0.26200, ~16 GB RAM, ~0.6 GB free RAM at inspection).

| Tool | Version | Status |
|---|---|---|
| Python | 3.13.0 (also 3.11, 3.9 installed) | OK — project venv `.venv` on 3.13 |
| Node.js / npm | 24.14.0 / 11.9.0 | OK |
| Git | 2.56.0.windows.2 | OK |
| GitHub CLI | 2.102.0, logged in as `Ahmad-Joker` (scopes: repo, workflow, gist, read:org) | OK — no remote created yet (needs founder approval) |
| Docker | 29.6.2 CLI; **Docker Desktop fails to start** (WSL bootstrap error 0x40010004) | Not used; not required |
| Browsers | Playwright Chromium installed project-locally | OK |
| Anthropic credentials | `ANTHROPIC_API_KEY` unset, `ant` CLI absent | **Blocker for live mode** |

Python deps (venv): fastapi 0.162, starlette 1.10, pydantic 2.14, httpx 0.28, uvicorn 0.54, anthropic 2.3, pytest 9.2, ruff 0.17.
Frontend deps: React 19.3, Vite 8.3, TypeScript 7.0, oxlint 1.89, @playwright/test.

## Selected architecture
Local processes only (no Docker): FastAPI backend (also hosts simulator APIs) on :8000, Vite dev server on :5173,
SQLite files under `var/`. Everything installs into `.venv` and `frontend/node_modules`; no system-wide changes made.

Phase 0 gate: backend and frontend dependencies install and both processes start — **met** (verified by Playwright runs).
