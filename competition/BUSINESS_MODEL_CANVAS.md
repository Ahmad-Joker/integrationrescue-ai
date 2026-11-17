# Business Model Canvas: IntegrationRescue

Legend: **[F]** fact we can show today · **[H]** hypothesis, unvalidated · **[P]** plan. Nothing here is validated
by customers yet. Validation plan: [PROBLEM_VALIDATION_PLAN.md](PROBLEM_VALIDATION_PLAN.md).

| Key partners | Key activities | Value propositions | Customer relationships | Customer segments |
|---|---|---|---|---|
| **[P]** Billing platforms' partner programmes (Stripe, Chargebee, Paddle) for connector access and listings · **[P]** model providers (Google Gemini today) · **[P]** cloud hosting · **[H]** integration agencies and fractional CTOs who see these incidents across clients · **[P]** Dubai/UAE startup programmes for first pilots | Building connectors (billing, CRM, entitlement stores) · maintaining the incident-family library and evaluation suite · keeping the verifier and policy layer independent of the model · running pilots | **For the engineer:** a broken "paid but still Free" style incident goes from hours of manual tracing to a tested, reviewable repair, with proof the customer's outcome is right **[H on time saved]** · **For the business:** fewer customers charged without access, fewer refunds and escalations **[H]** · **For risk/compliance:** nothing ships without human approval, and "fixed" is decided by an independent check, not the AI **[F in prototype]** · Says "cannot tell" or "nothing to fix" instead of guessing **[F]** | Self-serve trial on sandbox data, then a guided pilot · shared incident reports and audit trail · design-partner Slack channel during pilots **[P]** | **Beachhead [H]:** B2B SaaS companies (roughly 20–300 staff) with self-serve subscription billing (Stripe/Chargebee/Paddle) and their own entitlement/feature-flag logic, small platform teams, no dedicated billing engineer · **Users:** integration, support and platform engineers · **Buyers:** head of engineering or support; RevOps when revenue leakage is visible · **Later [H]:** integration agencies, iPaaS vendors (embedded), enterprises with many internal integrations |
| | **Key resources** | | **Channels** | |
| | Policy and verification engine, incident families with hidden ground truth, evaluation harness **[F]** · connectors **[P]** · founder's engineering time **[F]** | | Founder-led outreach to SaaS founders and engineering leads in the UAE and globally · content from real (anonymised) incident patterns · billing-platform app marketplaces · championship visibility **[P]** | |

| Cost structure | Revenue streams |
|---|---|
| Model inference per investigation (measured: 10–18 calls, about 35k–70k input tokens per incident on a lite model; dollar cost not measured on a paid tier) **[F/H]** · hosting and sandboxes (per-run isolation adds cost) **[H]** · connector development and maintenance · founder time; no salaries today **[F]** | **[H, untested]** Platform fee per connected integration plus a usage fee per *verified* resolution (pay for outcomes, not attempts) · enterprise plan with on-prem/VPC verifier, SSO and audit export · pilot fee for design partners. Price points are hypotheses to test: [PRICING_AND_UNIT_ECONOMICS.md](PRICING_AND_UNIT_ECONOMICS.md) |

**Unfair advantage (claim to test, not proven):** the incident library with hidden ground truth and an independent
verifier gives a measurable "verified outcome" metric that generic coding agents and AI SRE tools do not report. It
compounds as more incident families and connectors are added.
