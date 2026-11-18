# Go-to-market (plan, not traction)

**Today:** no customers, no pilots, no interviews completed, no revenue. Everything below is a plan.
Legend: **[F]** fact · **[H]** hypothesis · **[P]** plan.

## Where we start, and why
| Layer | Market | Basis |
|---|---|---|
| Founder base | **Egypt** | Ahmad Essam Abdelaziz lives in Egypt and studies Artificial Intelligence at AAST **[F]**. Direct access to Egyptian software teams, university and startup communities, and the Cairo/Alexandria tech scene, through in-person meetups **[P]** |
| Direct network and eligibility | **Egypt and the UK** | Ahmad holds Egyptian and British citizenship **[F]**, so UK pilots and company formation are practical options **[H]**. The UK has a large English-speaking B2B SaaS sector; reach it through remote outreach **[P]** |
| Competition-led expansion | **UAE** | The Create AI Agents Championship (Dubai Chamber of Digital Economy) offers judges, investors and an ecosystem **[F]**. Ahmad does **not** have an existing UAE customer or professional network. The UAE is a proposed expansion opportunity, subject to customer validation **[H]** |
| Product opportunity | **Global English-speaking B2B SaaS** | Connectors are per billing platform, not per country, so the product is not regional **[H]** |

Narrow focus throughout: **B2B SaaS companies whose billing system controls product access** (Stripe, Chargebee, Paddle
or similar, with their own entitlement logic). The buyer hypothesis is the head of engineering or support; RevOps
where revenue leakage is measured **[H]**.

## Phase 0: validation (now → 4 January 2027 deadline)
- 10 interviews ([PROBLEM_VALIDATION_PLAN.md](PROBLEM_VALIDATION_PLAN.md), targets in
  [INTERVIEW_TARGET_PROFILE.md](INTERVIEW_TARGET_PROFILE.md)): Egyptian SaaS teams and AAST/startup-community
  connections first, then UK teams remotely, plus UAE contacts *if* the championship provides introductions.
- Public judge demo, and a short written teardown of one incident class (content that shows the problem).
- Goal: 2–3 design partners willing to try the workflow on **fictional or test-mode** data.

## Phase 1: design partners (0–6 months after the championship) [P]
- Build one real **read-only** connector, chosen by what partners use (likely Stripe first; to confirm), plus GitHub
  repo access. **No real connector exists today [F].**
- Replay past incidents from the partner's own history, then handle new ones live with human approval.
- Success metric: verified resolutions, and time saved against the partner's own baseline. Publish as a case study
  only with permission.

## Phase 2: repeatable self-serve (6–18 months) [P]
- Listings in billing-platform app marketplaces. A self-serve trial runs on the partner's sandbox data.
- Content: anonymised incident patterns ("the 202 that lied") aimed at engineers who search for these symptoms.
- Integration agencies as a channel: they bring many client integrations.
- UAE expansion through championship contacts if validation there is positive.

## From simulated integrations to real connectors
| Step | What changes | What stays |
|---|---|---|
| 1. Read-only connector | the simulator client is replaced by a platform API client with least-privilege, read-only keys | typed tools, phase gating, redaction |
| 2. Event replay | replay uses the platform's own test-mode or event-resend API, never new charges | idempotency rules, verifier contract |
| 3. Verifier on real data | verifier queries a read replica or API snapshot | independence from model output |
| 4. Repo integration | patch proposed as a pull request in the customer's repo; customer CI is the test gate | allow-lists, human approval, regression test |
| 5. Isolation | customer code runs in per-run VM-grade sandboxes | resource limits, stripped environment |

## Scalability
The product scales with incident families and connectors, not with headcount per customer. Model cost per
investigation is measured (see PRICING). Verification is cheap and deterministic. The main scaling costs are
connector maintenance and sandbox compute.
