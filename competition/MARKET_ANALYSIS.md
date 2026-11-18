# Market analysis

**No external market figures are used here.** We have not verified any market-size number, so this document gives
a sizing *method* with placeholders. Fill a placeholder only with a figure whose source, publication date and URL
are written next to it, and mark it "external, not our data".

## The problem space
Every SaaS company that sells subscriptions connects a billing system to its product: who paid determines who gets
access. The same pattern repeats for CRM sync, provisioning, usage metering and partner integrations. These
connections fail in ways that monitoring misses, because each system reports success on its own terms. Our prototype
reproduces five such failure classes. **How often they happen in real companies, and what they cost, is unvalidated**
(see PROBLEM_VALIDATION_PLAN H1/H2).

## Segments
| Segment | Why they might care | Why they might not | Priority |
|---|---|---|---|
| B2B SaaS, 20–300 staff, self-serve billing + own entitlement logic | revenue-visible incidents, small teams, no billing specialist | may see incidents rarely | **Beachhead (hypothesis)** |
| Integration agencies / fractional CTOs | see many clients' integrations; sell fixes | low budgets per client | channel partner |
| iPaaS / billing platforms | could embed verified-resolution into their product | build vs buy | later partnership |
| Enterprises with many internal integrations | high cost per incident, compliance needs | long sales cycles, security reviews | later |

## Bottom-up sizing method (fill with validated inputs only)
```
Serviceable companies (beachhead)          N   = <count of target SaaS companies in region>     [source needed]
Share with ≥1 relevant incident per quarter p   = <from interviews: H1>                            [our data]
Incidents per affected company per year    f   = <from interviews>                                [our data]
Price per verified resolution              P   = <pricing test result>                            [our data]
Platform fee per company per year          F   = <pricing test result>                            [our data]

Annual revenue potential (beachhead) ≈ N × p × (f × P + F)
```
Do the calculation separately for Egypt (founder base), the UK (founder-access market), the UAE (competition-led
expansion) and global English-speaking SaaS. Present it only with the inputs visible.

## Regional angle (qualitative, to verify)
- **Founder base:** Ahmad is based in Egypt. Egyptian SaaS and software teams are the most reachable first interviewees
  (in person, same time zone, university and startup communities).
- **UK:** Ahmad also holds British citizenship, so UK teams are reachable remotely and UK pilots are practical.
- **UAE:** a proposed early market through the Create AI Agents Championship network (Dubai Chamber of Digital
  Economy), subject to customer validation. There is no existing UAE network or customer.
- Which billing platforms these companies use (global platforms such as Stripe, or local payment providers) is an
  interview question, not an assumption. Connector priorities follow the answers.
- Data residency and approval requirements in regulated sectors favour our design: read-only access, human approval
  and an auditable, independent verifier. This also points to an on-prem/VPC verifier option.
- **To do:** cite official Egyptian, UK or UAE digital-economy or SaaS statistics only with source, date and URL.

## Global opportunity (qualitative)
The workflow does not depend on the region: connectors are per platform, not per country. A global path runs through
billing-platform app marketplaces and English-language content. Competition is global (see COMPETITIVE_POSITIONING).

## Open questions this document cannot answer yet
How frequent and costly are these incidents? Which billing platforms dominate the beachhead? Who holds the budget?
Interviews answer these. Desk research does not.
