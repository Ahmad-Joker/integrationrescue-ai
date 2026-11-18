# Interview target profile

Who to interview to test the problem hypotheses in [PROBLEM_VALIDATION_PLAN.md](PROBLEM_VALIDATION_PLAN.md).
**No interviews have taken place yet.** Never add names or company names to this public repo; keep the real
contact list privately and use anonymised IDs (I-01, I-02 …) in `INTERVIEW_TRACKER_TEMPLATE.csv` copies.

## Company filter (all must hold)
- B2B SaaS with paid subscriptions where **the billing system controls product access** (plans, seats, features).
- Billing via Stripe, Chargebee, Paddle, Recurly or a similar platform, with their own entitlement or feature-flag
  logic (not purely the billing vendor's hosted portal).
- Roughly 10–300 staff. Big enough to have incidents, small enough to lack a dedicated billing engineer.

## Roles (priority order)
| Role | Why | What they can tell us |
|---|---|---|
| Founder / CTO of a small SaaS | often personally fixes these incidents; also the buyer | frequency, cost, willingness to pilot, budget |
| Platform / integration engineer | does the tracing | hours spent, tools, trust requirements |
| Billing or payments engineer | owns the billing ↔ product link | failure patterns, edge cases, connector priorities |
| Support engineering lead | first to hear "I paid but…" | how incidents arrive, customer impact, refunds |
| RevOps / finance lead | sees refunds and leakage | money impact, who owns the budget |
| Integration agency / fractional CTO | sees many clients' integrations | frequency across companies; channel potential |

## Early-adopter signals (rank higher)
Had a "paid but no access" or "webhook said OK, nothing happened" incident in the last 90 days · 1–5 platform
engineers · already uses AI coding tools · has a test-mode billing account · willing to share an anonymised log.

## Where to find them (no paid lead lists)
| Region | Channels | Notes |
|---|---|---|
| **Egypt** (founder base) | AAST and other university alumni, Egyptian SaaS founders, Cairo/Alexandria tech meetups and startup communities, incubators, LinkedIn | in person where possible; same time zone |
| **UK** (founder access) | LinkedIn, UK SaaS founder communities, Stripe/Chargebee community forums, remote calls | Ahmad's British citizenship makes UK pilots practical |
| **UAE** | only through championship, mentor or startup-programme introductions | no existing network; do not cold-claim local presence |
| **Remote / global** | billing-platform forums, Indie Hackers-style founder communities, integration agencies, open-source billing projects | English-speaking B2B SaaS |

Target mix for the first 10: about 4 Egypt, 3 UK, 1–2 UAE introductions, 1–2 global. Stop at 10 only if the answers
are consistent; otherwise continue to 15.

## Exclude
Consumer apps without subscriptions, companies with no billing-to-access link, people who only want to sell to us,
and anyone who would need to share real customer data to talk to us. Use fictional or test-mode examples only.
