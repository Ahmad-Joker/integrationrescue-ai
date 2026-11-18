# Product requirements (prototype)

**User:** integration / support engineer at a B2B SaaS company. **Job:** "A customer says X failed although every
system reports success — find out why, fix it safely, and prove it is fixed."

## Competition context
Official page https://dubaichamberdigital.com/en/create-ai-agents (read 2026-11-18; page "last updated on 15 October
2026"): launched 7 Oct 2026; four categories incl. Best Business AI Agent ("public- or private-sector use") and Best
Youth AI Agent (under 21); registration and submission of "Agent & Pitch Deck" in "January 2027" (no day given);
submission = prototype, pitch deck and demo video; English only; agent must not be copied from an existing repository;
finalists present a working agent on stage; Grand Final first week of May 2027. The 6-minute pitch video, Business
Model Canvas, Agent Card and judging weights come from the founder's brief. Founder-provided dates (2026-11-18):
submission portal opens 4 December 2026; deadline 4 January 2027. Internal readiness target: 2026-12-15.

## Requirements and status
| # | Requirement | Status |
|---|---|---|
| 1 | Incident creation (UI + API) | done (scenario-backed environments) |
| 2 | Log / JSON / screenshot evidence upload | done (stored, redacted); images not analysed yet |
| 3 | AI-driven investigation with tools and hypothesis revision | done (live Gemini, recorded evals; Claude fake-client only) |
| 4 | Local integration simulators with persistent state | done (billing, entitlements, webhooks; CRM missing) |
| 5 | Root-cause report | done |
| 6 | Failure reproduction in isolation | done |
| 7 | Bounded patch generation + policy check | done |
| 8 | Isolated patch testing | done |
| 9 | Independent business-state verification | done |
| 10 | Regression-test generation (fail-before/pass-after) | done |
| 11 | Human approval gate | done |
| 12 | Audit trail | done (timeline per incident) |
| 13 | Dashboard (7 screens) | done (dashboard, submit, investigation, repair, verification, report, eval lab) |
| 14 | Reproducible demo | done (`dev.ps1 demo`, UI) |
| 15 | 8 incident families | 5 of 8 |
| 16 | Multimodal (screenshots, browser, video) | not started |
| 17 | Live vs replay vs fault-injection modes, clearly labelled | done (live Gemini, baseline, fault injection) |
| 18 | Public judge demo (access control, limits, reset, container) | done locally; not deployed |

## Non-goals for the prototype
Real SaaS connectors, multi-tenant auth, production deployment, auto-promotion without human approval.
