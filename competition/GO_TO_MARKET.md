# Go-to-market (plan, not traction)

**Today:** no customers, no pilots, no revenue. Everything below is a plan.

## Phase 0: validation (now → submission)
- 10 interviews ([PROBLEM_VALIDATION_PLAN.md](PROBLEM_VALIDATION_PLAN.md)), UAE-first through the founder's network
  and local startup communities, plus remote calls globally.
- Public judge demo and a short written teardown of one incident class (content that shows the problem).
- Goal: 2–3 design partners willing to run a pilot on **test-mode** billing.

## Phase 1: design partners (0–6 months after the championship)
- Build one real read-only connector, chosen by what partners use (likely Stripe first; to confirm), plus GitHub repo
  access.
- Replay past incidents from partners' own history, then handle new ones live with human approval.
- Success metric: verified resolutions and the time saved against the partner's own baseline, published as a case
  study with permission.

## Phase 2: repeatable self-serve (6–18 months)
- Listings in billing-platform app marketplaces. A self-serve trial runs on the partner's sandbox data.
- Content: anonymised incident patterns ("the 202 that lied") aimed at engineers who search for these symptoms.
- Integration agencies as a channel: they bring many client integrations.

## From simulated integrations to real connectors
| Step | What changes | What stays |
|---|---|---|
| 1. Read-only connector | the simulator client is replaced by a platform API client with least-privilege, read-only keys | typed tools, phase gating, redaction |
| 2. Event replay | replay uses the platform's own test-mode or event-resend API, never new charges | idempotency rules, verifier contract |
| 3. Verifier on real data | verifier queries a read replica or API snapshot | independence from model output |
| 4. Repo integration | patch proposed as a pull request in the customer's repo; customer CI is the test gate | allow-lists, human approval, regression test |
| 5. Isolation | customer code runs in per-run VM-grade sandboxes | resource limits, stripped environment |

## Scalability
The product scales with incident families and connectors, not with headcount per customer. The model cost per
investigation is measured (see PRICING). Verification is cheap and deterministic. The main scaling costs are
connector maintenance and sandbox compute.
