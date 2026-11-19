# Release readiness (Definition of Done, competition prototype, updated 2026-11-18)

| # | Criterion | Status |
|---|---|---|
| 1 | Starts with documented commands | ✅ `dev.ps1`, `serve_demo.py`, Dockerfile |
| 2–4 | Backend, frontend, simulator APIs run | ✅ |
| 5 | Incident fixtures execute | ✅ 5 families |
| 6 | Genuine tool-driven decisions with a real model | ✅ Gemini (free tier); code repair unreliable |
| 7–10 | Reproduction, bounded repair, isolated testing, independent verification | ✅ |
| 11 | Duplicate financial effects prevented | ✅ tested |
| 12 | Indeterminate handled | ✅ |
| 13 | Security boundaries enforced | ✅ incl. public-demo controls; gaps in SECURITY_MODEL |
| 14–17 | Unit / integration / browser / adversarial tests pass | ✅ 2026-11-18 (VERIFICATION_REPORT) |
| 18 | Complete demo succeeds | ✅ live Gemini and baseline, local; ❌ no public URL |
| 19 | Metrics from actual runs | ✅ committed in `evidence/` |
| 20 | Documentation accurate | ✅ as of 2026-11-18 |
| 21 | Repo clean and reproducible | ✅ `f275ca1` pushed |
| 22 | CI verified | ✅ `f275ca1`: run 44259070565, backend + frontend + container jobs green |
| 23 | Multimodal | ❌ not started |
| 24 | Live vs baseline clearly labelled | ✅ UI, reports, evals, docs |
| 25 | Competition materials | 🟡 written and timed; deck is a final-design candidate (founder assets missing); recordings and validation evidence are founder actions |
| 26 | Limitations documented | ✅ `docs/LIMITATIONS.md` |
| 27 | Deployable container | ✅ built and verified locally; ❌ not deployed |

Not production-ready: needs per-run OS isolation, real connectors, user identity, monitoring, and a larger live
reliability evaluation.
