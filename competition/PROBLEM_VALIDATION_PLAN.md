# Problem validation plan

**Status: not started. There is no customer evidence yet.** This plan says how to get it honestly before the
submission. Evidence goes into [VALIDATION_EVIDENCE_TEMPLATE.md](VALIDATION_EVIDENCE_TEMPLATE.md) copies.

## Facts vs hypotheses
| Statement | Type |
|---|---|
| Billing → entitlement integrations can fail silently while every system reports success | Fact for the mechanism (we reproduce it); frequency in the wild unknown |
| SaaS teams experience "paid but locked out" incidents often enough to care | **Hypothesis H1** |
| Each incident costs meaningful engineering time (hours, not minutes) and customer goodwill | **Hypothesis H2** |
| Teams would trust an AI-proposed fix if a human approves it and an independent check proves the outcome | **Hypothesis H3** |
| Someone with budget (eng lead, support lead, RevOps) would pay per verified resolution | **Hypothesis H4** |
| Read-only access to billing plus repo access is acceptable for a pilot | **Hypothesis H5** |

## Who has the problem, who pays
- **Experiences it:** support agents (angry customer), integration and platform engineers (hours of tracing), finance
  (refunds).
- **Pays (hypothesis):** head of engineering or support at a 20–300-person B2B SaaS company; RevOps where leakage
  is measured.
- **Early adopters:** had at least one "paid but no access" or "webhook said OK but nothing happened" incident in the
  last 90 days; use Stripe, Chargebee or Paddle with their own entitlement logic; 1–5 platform engineers; already use
  AI coding tools (lower trust barrier).

## Interviews (target: 10 in 3 weeks)
- Sources: founder's network, UAE startup communities (incubators, coworking spaces, meetups), SaaS founders on
  LinkedIn, billing-platform community forums, integration agencies. **Do not pay for leads** (no budget).
- Script: [CUSTOMER_INTERVIEW_SCRIPT.md](CUSTOMER_INTERVIEW_SCRIPT.md). Ask about past behaviour, not opinions of the
  product. Show the demo only in the last 10 minutes.
- Record: role, company size (band), stack, last incident (what, how found, time to fix, who), current tools,
  spend on related tools, reaction to the demo, any commitment.

## Success criteria (decide before interviewing)
| Hypothesis | Supported if | Refuted if |
|---|---|---|
| H1 frequency | ≥5 of 10 describe a concrete incident in the last 6 months | ≤2 of 10 |
| H2 cost | median reported time to resolve ≥2 hours, or a refund/churn story | most fixed in minutes |
| H3 trust | ≥5 of 10 would let it propose fixes behind approval | most refuse repo or billing read access |
| H4 willingness to pay | ≥3 agree to a pilot, an intro to the budget holder, or a price conversation | none |
| H5 access | ≥3 would grant read-only billing + repo access for a pilot | none |

## Pilot plan (if H1–H3 hold)
1. Two to three design partners; their **sandbox/test-mode** billing first, never production at the start.
2. Build the connector for their billing platform (read-only) and import a past incident as a replay.
3. Measure time to verified resolution against their own record of the original incident.
4. Written permission for every data access, a data-processing note, and deletion at the end.

## Commitment signals to record (strongest first)
Signed pilot or LOI · intro to budget holder · shares a real (anonymised) incident log · agrees to a second call ·
"interesting". Only the first three count as validation in the pitch.

## What may be said in the pitch before evidence exists
"We are validating with interviews; here is the plan and the criteria." Never imply interviews or pilots that did not
happen. Once evidence exists, quote counts ("6 of 10 had an incident in the last 6 months") and anonymised paraphrases
with permission. Never invent quotations.
