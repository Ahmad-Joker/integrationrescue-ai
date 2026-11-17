# IntegrationRescue: executive summary

**Problem.** In integrated SaaS stacks a transaction can "succeed" everywhere while the business action silently
fails: the card is charged, the webhook returns 202, and the customer still sees "Upgrade to Pro". Monitoring sees no
error. Support escalates, and engineers trace the failure by hand across billing, webhooks, sync code and entitlement
data. (How often this happens and what it costs is a hypothesis we are now testing with interviews; see
`PROBLEM_VALIDATION_PLAN.md`.)

**Product.** An AI agent takes the incident and investigates across those systems with permission-controlled tools.
It reproduces the failure in an isolated copy and proposes the smallest repair. It tests that repair, including a
regression test that must fail before and pass after. After a human approves, an independent verifier proves the
outcome: correct entitlement, exactly one charge, exactly one grant. If the source of truth is unavailable, it
answers INDETERMINATE instead of guessing. If nothing is broken, it proves that and changes nothing.

**What the agent decides vs what code enforces.** The model (live Gemini) chooses evidence, hypotheses, tools and the
repair. Deterministic code enforces permissions, budgets, sandboxing, approval and verification. No model output can
mark anything fixed.

**Evidence (recorded, files in `evidence/`).** Live Gemini (free-tier `gemini-3.1-flash-lite`): 31/31 correct
diagnoses. After an edit-schema fix, 16/17 correct outcomes: 11/11 configuration and trust-change repairs verified,
3/3 "no action needed", 2/2 outages indeterminate. Code repair is not yet reliable (0/5). 0 false success claims and
0 duplicate charges in 72 recorded runs. The live run found a real safety gap: the model trusted a signing key it
should have checked. That check is now enforced in code.

**Differentiation hypothesis.** AI SRE tools diagnose telemetry; code fixers and coding agents patch code. Our narrow
claim is closing the loop on the *business outcome* across systems, with verification independent of the AI. A
head-to-head with a general coding agent is designed (`COMPARISON_PROTOCOL.md`) but not yet run.

**Business model (hypotheses, unvalidated).** Usage-based price per verified resolution plus a platform fee, for B2B
SaaS teams whose billing drives product access. First wedge: billing → entitlement integrations, where revenue leakage
and refunds are measurable. See `BUSINESS_MODEL_CANVAS.md` and `PRICING_AND_UNIT_ECONOMICS.md`.

**Stage.** Working prototype on simulated services with fictional data. Deployment-ready container, not yet
deployed. No customers, no pilots, no revenue.
