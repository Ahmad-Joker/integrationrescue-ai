# IntegrationRescue — executive summary (draft)

**Problem.** In integrated SaaS stacks a transaction can "succeed" everywhere while the business action silently fails:
the card is charged, the webhook returns 202, and the customer still sees "Upgrade to Pro". Monitoring sees no error;
support escalates; engineers trace it by hand across billing, webhooks, sync code and entitlement data.

**Product.** An agent that takes the incident, investigates across those systems with real, permission-controlled
tools, reproduces the failure in an isolated copy, proposes the smallest repair, tests it (including a regression test
that must fail before and pass after), and — after human approval — proves the outcome with an independent verifier:
correct entitlement, exactly one charge, exactly one grant. If authoritative state is unavailable it says
INDETERMINATE instead of guessing.

**What the agent decides vs what code enforces.** The model chooses evidence, hypotheses, tools and the repair.
Deterministic code enforces permissions, budgets, sandboxing, approval and verification. A model cannot mark anything fixed.

**Evidence today (recorded 2026-10-31, deterministic baseline, not the LLM):** 14 end-to-end incidents across 3 families
incl. held-out variants; 14/14 correct diagnoses; 8/8 repairable config defects verified; 2/2 ledger outages correctly
INDETERMINATE; 0 false VERIFIED; 0 duplicate charges. Live-model results: not yet measured.

**Differentiation hypothesis.** AI SRE tools (Datadog Bits AI, Cleric, Resolve.ai) and code fixers (Sentry Seer, coding
agents) diagnose or patch; IntegrationRescue's narrow claim is closing the loop on the *business outcome* across systems
with verification independent of the AI. To be tested against a general coding-agent baseline.

**Business model (hypotheses, unvalidated).** Per-integration subscription for SaaS teams, or per-resolved-incident
pricing; first wedge: billing → entitlement integrations where revenue leakage and refunds are measurable.

**Stage.** Working local prototype with simulated services and fictional data. No customers, no deployment.
