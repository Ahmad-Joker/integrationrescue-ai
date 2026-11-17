# Deployment (competition demo)

**Status: deployment-ready, not deployed.** No public URL exists yet. The container image was built and verified
locally on 2026-11-18 (see [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)). Deploying needs a hosting account,
which only the founder can create ([competition/USER_ACTIONS.md](../competition/USER_ACTIONS.md) A1–A3).

## Shape
One container (`Dockerfile`) runs FastAPI, the simulated services and the built dashboard on one port. State is
SQLite under `/data`, fictional and ephemeral: a restart wipes it and the demo re-seeds itself. Nothing connects
to a real billing or CRM system. Only outbound traffic: the Gemini API, when a key is configured.

Why not Vercel/serverless: the agent runs multi-minute background investigations, spawns child processes and
keeps SQLite state. That needs a long-lived process, so a container host fits better.

## Recommended host: Render (Docker web service)
`render.yaml` is a Blueprint. Use the free plan unless the founder decides to pay for one that doesn't sleep.
1. Render dashboard → New → Blueprint → connect `Ahmad-Joker/integrationrescue-ai` → it reads `render.yaml`.
2. Enter the three secrets Render asks for: `IR_ACCESS_TOKEN`, `IR_ADMIN_TOKEN`, `GEMINI_API_KEY`.
   Generate the codes with `python -c "import secrets; print(secrets.token_urlsafe(18))"`.
3. Deploy. When it is live, from a terminal on your machine:
   ```powershell
   $env:IR_ACCESS_TOKEN = "<the access code>"
   .venv\Scripts\python scripts\verify_deployment.py --url https://<service>.onrender.com
   .venv\Scripts\python scripts\verify_deployment.py --url https://<service>.onrender.com --provider gemini
   ```
   Both must print `15/15 checks passed`. The second run spends about 12–30 free-tier Gemini requests.
4. Record the URL and the two results in `competition/SUBMISSION_READINESS.md` and `docs/JUDGE_ACCESS.md`.

Alternatives that run the same image unchanged: Fly.io (`fly launch --dockerfile Dockerfile`, then set
`fly secrets set ...`), Railway, Google Cloud Run (set `--max-instances=1`, because state is in-process), or any VM
(`docker run`). On a VM with no proxy in front, leave `IR_TRUST_PROXY` unset.

## Environment variables
| Variable | Required | Default | Purpose |
|---|---|---|---|
| `IR_DEMO_MODE` | container sets `1` | `0` | public-demo rules: access code required, no auto-approval, no UI eval runs, seeded examples |
| `IR_ACCESS_TOKEN` | **yes** in demo mode | — | code judges enter before creating, running, approving or rejecting incidents (≥16 chars) |
| `IR_ADMIN_TOKEN` | recommended | — | enables `POST /api/admin/reset` (header `x-admin-token`); must differ from the access code |
| `GEMINI_API_KEY` | for the live agent | — | Google AI Studio key; without it only the baseline runs |
| `IR_PROVIDER` | no | `deterministic` | default decision maker for new incidents (`gemini` on Render) |
| `IR_GEMINI_MODEL` | no | `gemini-2.5-flash` | `gemini-3.1-flash-lite` is the model with recorded live results |
| `IR_MAX_LLM_CALLS` | no | `30` | model calls per incident (1–200) |
| `IR_MAX_LIVE_INCIDENTS_PER_DAY` | no | `15` | protects the model quota; the baseline stays available |
| `IR_MAX_CONCURRENT_RUNS` | no | `3` | parallel investigations |
| `IR_RATE_LIMIT_PER_MIN` | no | `30` | state-changing requests per client per minute |
| `IR_TRUST_PROXY` | behind a proxy | `0` | use the left-most `X-Forwarded-For` as the client address |
| `IR_CORS_ORIGINS` | no | Vite dev origins | exact origins only; not needed when the API serves the dashboard |
| `IR_STATIC_DIR`, `IR_EVIDENCE_DIR`, `IR_VAR_DIR` | container sets | — | dashboard files, committed eval evidence, fictional state |

Startup validation (`backend/integrationrescue/config.py`) stops the app on a missing access code in demo mode,
codes shorter than 16 characters, identical access and admin codes, wildcard or malformed CORS origins, an unknown
provider, or non-numeric limits.

## Reset
- On a deployment: `curl -X POST -H "x-admin-token: <admin code>" https://<host>/api/admin/reset`. This deletes all
  incidents and re-seeds two baseline examples, and refuses while an investigation is running.
- Locally: `./scripts/dev.ps1 reset` (deletes `var/`).

## Local equivalents
- Run the container: `docker build -t integrationrescue .` then
  `docker run -p 8000:8000 -e IR_ACCESS_TOKEN=... -e IR_ADMIN_TOKEN=... integrationrescue`.
- Without Docker: `npm run build --prefix frontend`, then `.venv\Scripts\python scripts\serve_demo.py`. This serves
  http://127.0.0.1:8080, loads `.env`, and prints throwaway codes if none are set.

## CI coverage
The `container` job in `.github/workflows/ci.yml` builds this image and checks that it refuses to start without an
access code. It then runs `scripts/verify_deployment.py` against the container: an incident, the agent run, the
human gate, approval, verification, and a ledger outage giving INDETERMINATE. That job uses the deterministic
baseline and no secrets.
