# Project status (updated 2026-11-18)

**Phase:** competition prototype, submission preparation. Core loop complete. Public demo mode and container are
ready but not deployed. Business validation has not started.

## Verified on 2026-11-18 (details: [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md))
- Backend: full pytest suite passes on Windows (Python 3.13) and on Linux inside the container image (Python 3.12),
  including POSIX resource-limit tests. ruff clean.
- Frontend: oxlint clean, `tsc -b && vite build` succeeds, Playwright browser tests pass.
- Container: image builds, refuses to start without an access code, runs as uid 10001, and passes
  `scripts/verify_deployment.py` 15/15 (deterministic).
- Live Gemini end-to-end on the local demo server: 15/15, VERIFIED ([evidence/live](../evidence/live/README.md)).
- CI: latest pushed commit `a3ffbcd` is green on GitHub (run 44201542793: backend, frontend, container). The deck,
  pitch and validation-kit changes made later on 2026-11-18 are awaiting the founder's push approval.

## Implemented
Simulators (billing, entitlements, webhooks, logs) · sync service running customer code in limited child processes ·
5 incident families: payment_entitlement (4 variants), schema_drift (2), state_unavailable (1),
signing_key_rotated (2), ack_timeout (2) · orchestrator with persistence, resume and the approval gate ·
18 diagnostic tools + 6 control/terminal tools · live Gemini provider, Claude provider (fake-client tested) and the
deterministic baseline · sandbox + regression generation · independent verifier · reports · product API · dashboard ·
evaluation harness · coding-agent comparison harness · public demo mode (access code, admin reset, rate limit,
live-run cap, featured incidents, seeded examples, security headers, config validation) · Dockerfile, Render
Blueprint, deployment check script · CI with backend, frontend and container jobs.

## Evaluation (raw files in `evidence/eval/`)
Live Gemini: diagnosis 31/31 scored; after the edit-schema fix the expected outcome was reached in 16/17 runs.
Code repair is not established (0/5 scored). Baseline: 18/22. 0 false success claims and 0 duplicate charges in 72
runs. See [competition/TECHNICAL_EVIDENCE.md](../competition/TECHNICAL_EVIDENCE.md).

## Known gaps
See [LIMITATIONS.md](LIMITATIONS.md): no deployment, no customer validation, no coding-agent comparison run,
unreliable live code repair, no per-run OS isolation, 3 of 8 families missing, no vision analysis.

## Deployment
None. Deployment-ready: [DEPLOYMENT.md](DEPLOYMENT.md). Needs a founder-owned hosting account.
