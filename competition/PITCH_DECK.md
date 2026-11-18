# Pitch deck specification (15 slides)

**Status: final-design candidate awaiting founder assets (email, photo, demo video, public URL, QR code).** Generated from `competition/deck_data.json` by `scripts/build_deck.py` (2026-11-18). Edit the JSON, not this file. Every figure must match [TECHNICAL_EVIDENCE.md](TECHNICAL_EVIDENCE.md). Visual QA: [DECK_QA.md](DECK_QA.md).

Design: dark theme, one message per slide, real screenshots from a live Gemini run (fictional data, `competition/screenshots/`), large evidence numbers, the code-repair limitation shown at equal size, hypotheses labelled, amber placeholder boxes for missing founder assets. File: `IntegrationRescue_Competition_Deck.pptx`.

## 1. IntegrationRescue

**Key message:** The AI agent that fixes broken SaaS integrations and proves the business outcome.

**Visible text:**
- Investigates
- Repairs in a sandbox
- Human-approved
- Independently verified
- Invoice paid
- Exactly one charge
- Plan matches payment: Pro
- Granted exactly once

**Speaker notes:** Title card at the start of the presentation part. No narration needed.

**Evidence source:** README.md; screenshot: live run inc_2376f4f829

**Needs founder validation:** Founder email

## 2. Paid. Still on Free.

**Key message:** Every system reports success while the customer loses what they paid for.

**Visible text:**
- Billing · Charge succeeded
- Webhook · 202 Accepted
- Sync service · No error logged
- Customer access · Still on Free
- No alert fires. Support escalates. An engineer traces it by hand across four systems.

**Speaker notes:** What you just saw is a failure no dashboard catches. The customer paid, every system said success, and the customer still couldn't use what they paid for. Someone has to notice. Then an engineer spends hours tracing it across billing, webhooks, code and access data.

**Evidence source:** Simulated incident family payment_entitlement (fictional)

**Needs founder validation:** Any time or cost figure must come from interviews

## 3. Who has the problem

**Key message:** B2B SaaS teams whose billing system controls product access.

**Visible text:**
- Support · Angry customer who paid and is locked out
- Integration & platform engineers · Hours of tracing across billing, webhooks, code
- Finance / RevOps · Refunds and revenue leakage
- Buyer hypothesis: head of engineering or support (unvalidated)
- Validation: interview plan ready · 0 interviews completed

**Speaker notes:** This can hit any software company whose billing controls product access, especially small teams with no billing specialist. Support feels it first, then engineering, then finance through refunds. Fallback until interviews exist: We're now interviewing SaaS teams to measure how often this happens and what it costs.

**Evidence source:** PROBLEM_VALIDATION_PLAN.md (no evidence yet)

**Needs founder validation:** Replace the status line with real interview counts once they exist; never invent

## 4. Why today's tools stop short

**Key message:** Each tool checks its own layer. Nobody checks the customer's outcome.

**Visible text:**
- Monitoring · HTTP 202 = fine
- AI SRE tools · Start from an alert; none fires
- Coding agents · Tests pass ≠ customer fixed
- Integration platforms · "The run succeeded"
- The gap: verifying the business outcome across systems
- Comparison with a general coding agent: protocol ready, not yet run. No superiority claim.

**Speaker notes:** Today's tools stop early. Monitoring sees a 202 and is happy. Coding assistants can write a patch, but they judge success by tests passing, not by whether the customer actually got access.

**Evidence source:** COMPETITIVE_POSITIONING.md, COMPARISON_PROTOCOL.md

**Needs founder validation:** none

## 5. IntegrationRescue

**Key message:** An AI agent that investigates like a careful engineer, and only claims what an independent check proves.

**Visible text:**
- Live Gemini agent chooses every tool call and hypothesis
- Smallest repair, tested in an isolated copy
- A human approves; a read-only verifier proves

**Screenshots:** `screenshots/04_incident_overview.png`

**Speaker notes:** IntegrationRescue is an AI agent that works like a careful engineer. It forms hypotheses, checks each system, reproduces the failure in a copy and proposes the smallest fix.

**Evidence source:** Screenshot: live Gemini run inc_2376f4f829 (13 model calls, VERIFIED); AGENT_CARD.md

**Needs founder validation:** none

## 6. How the agent works

**Key message:** The model decides. Deterministic code enforces.

**Visible text:**
- Investigate
- Reproduce
- Patch & test
- Human approval
- Promote
- Independent verify

**Speaker notes:** It tests the fix and asks a human to approve. Then a separate verifier, which the AI cannot influence, checks the business result: right plan, one charge, one grant. That's why it's an agent and not an automation: it decides what to investigate, whether a fix is needed at all, and when it can't know.

**Evidence source:** docs/ARCHITECTURE.md, AGENT_CARD.md

**Needs founder validation:** none

## 7. Live demo

**Key message:** A real Gemini-powered run, end to end, in under two minutes.

**Visible text:**

**Screenshots:** `screenshots/02_new_incident.png`

**Speaker notes:** The two-minute demo plays here (0:00-2:00 of the pitch video). It is a recording of a real Gemini-powered run; the investigation path is produced by the agent, not replayed from the baseline.

**Evidence source:** DEMO_SCRIPT_2_MIN.md

**Needs founder validation:** Demo video link; Recording date

## 8. Architecture

**Key message:** One container: agent, policy layer, simulated systems, sandbox, verifier, dashboard.

**Visible text:**

**Speaker notes:** Backup slide for Q&A; not narrated in the six-minute video. Gemini today; a Claude adapter exists (fake-client tested only); the deterministic baseline is for tests and comparison and is never presented as the AI.

**Evidence source:** docs/ARCHITECTURE.md, docs/SECURITY_MODEL.md, Dockerfile

**Needs founder validation:** none

## 9. Reliability evidence

**Key message:** Measured on live Gemini, including what does not work yet.

**Visible text:**
- 31/31 · correct diagnoses · ok
- 16/17 · correct outcomes after the tool fix · ok
- 11/11 · config & trust repairs verified · ok
- 0 · false success claims · ok
- 0 · duplicate charges · ok
- 0/5 · code repairs: not yet reliable · warn
- Live: gemini-3.1-flash-lite, free tier, 2 seeds per variant; 31 scored live runs, 72 recorded runs in total (live + baseline). Small samples.

**Speaker notes:** We measure this. In live tests with Google Gemini, the agent diagnosed all 31 scored incidents correctly. After one fix to our tools, it reached the right outcome in 16 of 17, and all 11 configuration and trust repairs were verified. Zero false success claims, zero double charges. Code repairs are not reliable yet: zero of five. We publish that too.

**Evidence source:** TECHNICAL_EVIDENCE.md; evidence/eval/*.json; scripts/summarize_evidence.py

**Needs founder validation:** none

## 10. Safety and human oversight

**Key message:** Safety lives in code, not in the prompt.

**Visible text:**
- Every repair waits for a human
- Only the read-only verifier can say VERIFIED
- Live test: the AI trusted an unannounced signing key. Now blocked in code, whatever the model proposes
- Model outage shows MODEL UNAVAILABLE, never success

**Screenshots:** `screenshots/10_verification_after.png`

**Speaker notes:** Safety lives in code, not in the prompt. In one test, the AI trusted a security key it should have checked. We didn't just change the prompt. We made the system refuse that change, whatever the model says. Every repair needs human approval, and only the independent check can say verified.

**Evidence source:** docs/SECURITY_MODEL.md; test_delivery_families.py; test_provider_failures.py; screenshots from inc_2376f4f829

**Needs founder validation:** none

## 11. Defensibility

**Key message:** Verified outcomes on a growing library of incident patterns.

**Visible text:**
- New incident
- Test case with hidden ground truth
- Measured, verified agent
- Trust → more pilots
- Today: 5 incident families, simulated. The library grows only with real pilots.

**Speaker notes:** Our advantage is verified outcomes. Every incident becomes a test case with hidden ground truth, so we can prove reliability, and that library grows with every pilot. And we're model-agnostic.

**Evidence source:** COMPETITIVE_POSITIONING.md

**Needs founder validation:** none

## 12. Business model

**Key message:** Pay for proven fixes, not attempts.

**Visible text:**
- Platform fee · per connected integration
- Fee per VERIFIED fix · nothing for DIAGNOSED or INDETERMINATE
- Enterprise · VPC verifier, SSO, audit export
- Beachhead (hypothesis): B2B SaaS, roughly 20–300 staff, billing on Stripe / Chargebee / Paddle controls product access
- Measured: 11–18 model calls, 35k–70k input tokens per incident (live means, free tier)

**Speaker notes:** We plan to charge for outcomes: a platform fee, plus a fee per verified fix, and nothing for a guess. Fallback: That pricing is a hypothesis we'll test with design partners.

**Evidence source:** BUSINESS_MODEL_CANVAS.md, PRICING_AND_UNIT_ECONOMICS.md, evidence/eval

**Needs founder validation:** Price points after pricing interviews

## 13. Market entry

**Key message:** Validate where the founder has access; expand through the championship.

**Visible text:**
- Egypt · Founder base · Interviews and first design partners
- UK · Founder access · Remote interviews and pilots
- UAE · Championship ecosystem · Expansion opportunity, subject to validation
- Global · English-speaking B2B SaaS · Billing-platform marketplaces
- Plan, not traction: no customers, pilots or interviews yet. No market-size figure is claimed.

**Speaker notes:** I'm based in Egypt, so we start interviews and pilots there and in the UK, through my own network. This championship opens the UAE ecosystem as an expansion market. The product itself is global: connectors follow billing platforms, not borders.

**Evidence source:** GO_TO_MARKET.md, MARKET_ANALYSIS.md

**Needs founder validation:** Any market number needs source, date, URL

## 14. Roadmap

**Key message:** From a measured prototype to real connectors and pilots.

**Visible text:**
- Now → Working prototype, 5 incident families, Live Gemini agent, Container ready
- Next → Read-only billing connector, Design-partner pilots (test-mode data), Coding-agent comparison
- Then → Per-run isolation for customer code, CRM incident families, Screenshot analysis

**Speaker notes:** Today it's a working prototype on simulated systems with fictional data. Next come real read-only connectors, design-partner pilots, and stronger isolation for customer code.

**Evidence source:** docs/NEXT_ACTIONS.md

**Needs founder validation:** none

## 15. Proven, not guessed.

**Key message:** We're looking for design partners: SaaS engineering teams willing to test the workflow on fictional or test-mode data.

**Visible text:**
- github.com/Ahmad-Joker/integrationrescue-ai

**Speaker notes:** I'm Ahmad Essam Abdelaziz, an artificial-intelligence student at AAST and an AI-agent developer. I built this because agents are only useful when their results can be trusted. We're looking for design partners: SaaS engineering teams willing to test the workflow on fictional or test-mode data. [Only with a verified URL:] Judges can try the live demo at the link on screen. When software breaks between systems, IntegrationRescue fixes it, and proves it. Thank you.

**Evidence source:** Founder facts supplied by Ahmad

**Needs founder validation:** Founder photo; Founder email; Public demo URL + QR (only after verify_deployment passes)

