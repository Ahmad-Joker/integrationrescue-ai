# Release readiness (Definition of Done, competition prototype)

| # | Criterion | Status |
|---|---|---|
| 1 | Starts with documented commands | ✅ |
| 2 | Backend services run | ✅ |
| 3 | Frontend runs | ✅ |
| 4 | Simulator APIs work | ✅ |
| 5 | Incident fixtures execute | ✅ (3 families) |
| 6 | Genuine tool-driven decisions with a real model | ✅ Gemini (free tier); repair rate low, see EVALUATION_PLAN |
| 7 | Failure reproduction | ✅ |
| 8 | Bounded repair proposal | ✅ |
| 9 | Isolated repair testing | ✅ |
| 10 | Independent verification | ✅ |
| 11 | Duplicate financial effects prevented | ✅ (tested) |
| 12 | Indeterminate handled | ✅ |
| 13 | Security boundaries enforced | ✅ (see gaps in SECURITY_MODEL) |
| 14–17 | Unit / integration / browser / adversarial tests pass | ✅ |
| 18 | Complete demo succeeds | ✅ deterministic mode |
| 19 | Metrics from actual runs | ✅ baseline + live Gemini |
| 20 | Documentation accurate | ✅ as of 2026-10-31 |
| 21 | Repo clean and reproducible | ✅ local |
| 22 | CI verified | ✅ GitHub Actions green (run 41154637560) |
| 23 | Multimodal | ❌ not started |
| 24 | Live vs replay clearly labelled | ✅ |
| 25 | Competition materials | 🟡 partial |
| 26 | Limitations documented | ✅ |

Not production-ready: needs auth, OS isolation, real connectors, monitoring and a live-model reliability evaluation.
