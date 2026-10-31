# Product requirements (prototype)

**User:** integration / support engineer at a B2B SaaS company. **Job:** "A customer says X failed although every
system reports success — find out why, fix it safely, and prove it is fixed."

## Competition context (from press coverage, not the official rulebook)
Create AI Agents Championship, launched 7 Oct 2026 by the Dubai Chamber of Digital Economy; categories include Best
Business AI Agent and Best Youth AI Agent (reported as under-21). Reported submission items: prototype, pitch deck,
demo video. Registration close is reported inconsistently (Dec 2026 vs Jan 2027) — **confirm on
dubaichamberdigital.com/en/create-ai-agents**. Internal readiness target: 2026-12-15.

## Requirements and status
| # | Requirement | Status |
|---|---|---|
| 1 | Incident creation (UI + API) | done (scenario-backed environments) |
| 2 | Log / JSON / screenshot evidence upload | done (stored, redacted); images not analysed yet |
| 3 | AI-driven investigation with tools and hypothesis revision | done (Claude provider; live run blocked on credentials) |
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
| 15 | 8 incident families | 3 of 8 |
| 16 | Multimodal (screenshots, browser, video) | not started |
| 17 | Live vs replay vs fault-injection modes, clearly labelled | done for deterministic + fault injection; live untested |

## Non-goals for the prototype
Real SaaS connectors, multi-tenant auth, production deployment, auto-promotion without human approval.
