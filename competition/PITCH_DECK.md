# Pitch deck specification (15 slides)

Generated from `competition/deck_data.json` by `scripts/build_deck.py` (2026-11-18). Edit the JSON, not this file. Every figure must match [TECHNICAL_EVIDENCE.md](TECHNICAL_EVIDENCE.md).

Design: dark background, one message per slide, at most 4 short bullets, large numbers for evidence. The demo video is embedded on slide 7 (or linked, if the portal needs a separate upload). Draft file: `IntegrationRescue_Competition_Deck.pptx`.

## 1. IntegrationRescue

**Key message:** The AI agent that fixes broken SaaS integrations and proves the business outcome.

**Visible text (maximum):**
- Investigates · repairs in a sandbox · human-approved · independently verified
- Create AI Agents Championship · Best Business AI Agent
- Ahmad · <email>

**Visual:** Logo mark + one-line value proposition on a dark background

**Speaker notes:** Shown during the first seconds or as a title card; no narration needed.

**Evidence source:** README.md

**Needs founder validation:** Founder name/contact

## 2. Paid. Still on Free.

**Key message:** Every system says success while the customer loses what they paid for.

**Visible text (maximum):**
- Card charged ✓  Webhook 202 ✓  Access: Free ✗
- No alert fires
- Support → engineering → hours of manual tracing

**Visual:** Three green ticks (Billing, Webhook, Sync) and one red cross (Customer access)

**Speaker notes:** What you just saw is a failure no dashboard catches...

**Evidence source:** Simulated incident family payment_entitlement

**Needs founder validation:** Any time/cost figure must come from interviews

## 3. Who has the problem

**Key message:** SaaS teams whose billing drives product access, especially small teams without a billing specialist.

**Visible text (maximum):**
- Feels it: support, integration engineers, finance
- Pays (hypothesis): head of engineering or support
- Validation: 10 interviews in progress / planned

**Visual:** Persona strip: support agent, platform engineer, finance lead

**Speaker notes:** Who has it segment of the pitch script.

**Evidence source:** PROBLEM_VALIDATION_PLAN.md

**Needs founder validation:** Replace 'planned' with real interview counts once done; never invent

## 4. Why today's tools stop short

**Key message:** Monitoring trusts the 202; coding agents trust green tests; nobody checks the customer's outcome.

**Visible text (maximum):**
- Monitoring: HTTP OK = fine
- AI SRE: needs an alert
- Coding agents: tests pass ≠ customer fixed

**Visual:** Three columns with where each tool stops, and a gap labelled 'business outcome'

**Speaker notes:** Today's tools segment. No superiority claim: comparison not yet run.

**Evidence source:** COMPETITIVE_POSITIONING.md

**Needs founder validation:** none

## 5. IntegrationRescue

**Key message:** An AI agent that investigates like a careful engineer and only claims what an independent check proves.

**Visible text (maximum):**
- Live Gemini agent decides what to investigate
- Smallest repair, tested in isolation
- Human approves · independent verifier proves

**Visual:** Product screenshot: incident page with LIVE AI AGENT banner

**Speaker notes:** Solution segment, first half.

**Evidence source:** AGENT_CARD.md

**Needs founder validation:** none

## 6. How the agent works

**Key message:** The model decides; deterministic code enforces.

**Visible text (maximum):**
- Investigate → Reproduce → Patch & test → Human approval → Promote → Verify
- Says NO ACTION NEEDED or INDETERMINATE when true
- Budgets, allow-lists, sandbox in code

**Visual:** Pipeline diagram with the approval gate and verifier highlighted

**Speaker notes:** Why it is an agent, not an automation: decides what to check, whether to fix, when it cannot know.

**Evidence source:** docs/ARCHITECTURE.md

**Needs founder validation:** none

## 7. Live demo

**Key message:** A real live Gemini run, end to end, in two minutes.

**Visible text (maximum):**
- <embedded or linked 2-minute video>
- Recorded live on <date>

**Visual:** Embedded video (or thumbnail + unlisted link)

**Speaker notes:** The demo plays here (0:00–2:00 of the pitch video).

**Evidence source:** DEMO_SCRIPT_2_MIN.md

**Needs founder validation:** Video link; Recording date

## 8. Architecture

**Key message:** One container: agent, policy layer, simulated systems, verifier, dashboard.

**Visible text (maximum):**
- Typed, phase-gated tools · patch policy · sandbox + replay
- Read-only verifier derives truth from billing
- Gemini today; model-agnostic (Claude adapter, baseline)

**Visual:** Box diagram: Ticket → Agent (Gemini) ↔ Tools → Simulators; Policy; Sandbox; Approval; Verifier (read-only)

**Speaker notes:** Backup slide for Q&A; not narrated in the 6-minute video.

**Evidence source:** docs/ARCHITECTURE.md, docs/SECURITY_MODEL.md

**Needs founder validation:** none

## 9. Reliability evidence

**Key message:** Measured on live Gemini, including what does not work yet.

**Visible text (maximum):**
- 31/31 correct diagnoses (live, scored)
- 16/17 correct outcomes after tool fix · 11/11 config & trust repairs verified
- 0 false success claims · 0 duplicate charges (72 runs)
- Code repair: 0/5, not yet reliable

**Visual:** Four big numbers; the code-repair number shown just as prominently

**Speaker notes:** Evidence segment. Free-tier gemini-3.1-flash-lite, 2 seeds per variant: small samples.

**Evidence source:** TECHNICAL_EVIDENCE.md, evidence/eval/

**Needs founder validation:** none

## 10. Safety and human oversight

**Key message:** Safety lives in code, not in the prompt.

**Visible text (maximum):**
- Every repair needs human approval
- Only the independent verifier can say VERIFIED
- Live test found the AI trusting an unverified key → now blocked in code
- Model outage = MODEL UNAVAILABLE, never success

**Visual:** Approval gate screenshot + 'blocked' policy message

**Speaker notes:** Safety segment.

**Evidence source:** docs/SECURITY_MODEL.md, TECHNICAL_EVIDENCE.md

**Needs founder validation:** none

## 11. Defensibility

**Key message:** Verified outcomes, measured on a growing library of real incident patterns.

**Visible text (maximum):**
- Incident library with hidden ground truth
- Independent verifier + audit trail
- Connectors (planned) · model-agnostic

**Visual:** Flywheel: incident → test case → better agent → more trust → more incidents

**Speaker notes:** Defensibility segment. Honest: library is 5 families today.

**Evidence source:** COMPETITIVE_POSITIONING.md

**Needs founder validation:** none

## 12. Business model

**Key message:** Pay for proven fixes, not attempts (hypothesis).

**Visible text (maximum):**
- Platform fee per connected integration
- Fee per VERIFIED resolution; nothing for a guess
- Enterprise: VPC verifier, SSO, audit export

**Visual:** Business Model Canvas thumbnail + pricing boxes marked 'hypothesis'

**Speaker notes:** Business segment, part 1.

**Evidence source:** BUSINESS_MODEL_CANVAS.md, PRICING_AND_UNIT_ECONOMICS.md

**Needs founder validation:** Price points after pricing interviews

## 13. Market and go-to-market

**Key message:** Start with SaaS teams on common billing platforms, UAE first, then global via marketplaces.

**Visible text (maximum):**
- Design partners on test-mode billing
- Billing-platform app marketplaces
- Integration agencies as a channel

**Visual:** Map: UAE pilots → global marketplaces

**Speaker notes:** Business segment, part 2. No market-size figure unless sourced.

**Evidence source:** MARKET_ANALYSIS.md, GO_TO_MARKET.md

**Needs founder validation:** Any market number needs source, date, URL

## 14. Roadmap

**Key message:** From a proven prototype to real connectors and pilots.

**Visible text (maximum):**
- Now: prototype, 5 incident families, live Gemini
- Next: read-only connectors, design-partner pilots
- Then: per-run isolation, CRM family, vision

**Visual:** Three-step timeline

**Speaker notes:** Roadmap segment. Dates only if committed.

**Evidence source:** docs/NEXT_ACTIONS.md

**Needs founder validation:** none

## 15. Proven, not guessed.

**Key message:** When software breaks between systems, IntegrationRescue fixes it and proves it.

**Visible text (maximum):**
- Ahmad · founder
- github.com/Ahmad-Joker/integrationrescue-ai
- <demo URL> · <email>

**Visual:** Founder photo, contact, QR code to the demo

**Speaker notes:** Close.

**Evidence source:** —

**Needs founder validation:** Team: add co-founders/advisors only if real; Demo URL once deployed

