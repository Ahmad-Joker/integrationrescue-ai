# Pricing and unit economics

**All prices below are hypotheses to test, not validated prices.** Measured inputs are marked [measured], with
their source. Everything else is a placeholder.

## Pricing hypotheses (test in interviews and pilots)
| Model | Shape | Why it might work | Risk | Test |
|---|---|---|---|---|
| **A. Outcome-based (lead hypothesis)** | platform fee per connected integration per month + fee per *verified* resolution; nothing for DIAGNOSED/INDETERMINATE | aligns price with proof; the verifier makes "resolved" countable | lumpy revenue; disputes over what counts | ask "what would one verified fix be worth to you?" against the incident cost they report |
| B. Seat-based SaaS | per engineer per month | familiar, predictable | users are occasional; weak value link | ask what they pay for comparable tools |
| C. Enterprise | annual licence, VPC/on-prem verifier, SSO, audit export | regulated buyers, data residency | long cycles | only after 3+ pilots |
| D. Design-partner pilot | fixed pilot fee or free for 60 days in exchange for a case study | gets evidence fast | no revenue signal if free | prefer a small paid pilot as a commitment signal |

Price points to test (deliberately wide, not recommendations): per verified resolution `<P_low>` / `<P_mid>` /
`<P_high>`; platform fee `<F_low>` / `<F_high>` per integration per month. Use Van Westendorp-style questions or
three-option anchoring, after the interviewee has described their last incident's cost.

## Cost per investigation model
```
Model cost        = calls × (input_tokens × price_in + output_tokens × price_out)
Compute/sandbox   = run_minutes × sandbox_cost_per_minute
Verification      = negligible (read-only SQL against a snapshot/replica)
Human review      = customer's time (not our cost), typically one approval
Cost per investigation = model cost + compute + allocated connector/maintenance cost
```
Measured inputs (live Gemini `gemini-3.1-flash-lite`, free tier, from `evidence/eval`):
| Input | Value |
|---|---|
| Model calls per incident | 10.7–17.8 mean across live runs [measured] |
| Input tokens per incident | 34,583–69,138 mean [measured] |
| Output tokens per incident | 672–3,035 mean [measured] |
| Wall time per incident | 27.7–58.6 s median (runs 2–3) [measured] |
| Price per 1M input/output tokens | `<from the provider's current price page, with date>` [not yet looked up] |
| Sandbox cost per minute | `<from hosting price page>` [not measured] |

Example calculation to fill in: `cost ≈ 46,805 × price_in/1e6 + 883 × price_out/1e6` (run-2 means), plus compute.
Stronger models cost more per token and may need fewer calls. Measure before quoting.

## Unit economics to track once pilots exist
Cost per investigation and per *verified* resolution (failed attempts are cost without revenue) · gross margin per
verified resolution · share of incidents ending VERIFIED vs DIAGNOSED · connector build cost per platform · time to
first verified resolution in a pilot.

## What not to say
No revenue projections, LTV/CAC or margin percentages until pilot data exists. In the pitch: "pricing hypothesis:
pay per verified fix", plus the measured token usage.
