# Customer interview script (30 minutes)

Rules: ask about **past events**, not hypotheticals. Don't pitch until the end. Take notes in a copy of
[VALIDATION_EVIDENCE_TEMPLATE.md](VALIDATION_EVIDENCE_TEMPLATE.md). Ask permission before recording or quoting.
Never put real customer names or personal data into this public repository: anonymise (role, size band, stack).

## Opening (2 min)
"I'm building a tool around integration failures between billing and product access. I'm not selling today. I want
to learn how this works at your company. May I take notes? Nothing will be shared with your name attached."

## Context (5 min)
1. What's your role, and roughly how big is the team or company?
2. How does a customer payment turn into access in your product? Which billing platform? Who owns that code?
3. What other integrations matter to revenue (CRM, provisioning, usage metering)?

## The last incident (12 min)
4. Tell me about the last time a customer paid (or upgraded) and didn't get what they paid for, or an integration
   "succeeded" but nothing happened. When was it?
5. How did you find out? Who noticed first?
6. Walk me through what you did to find the cause, step by step. Which systems did you open?
7. How long did it take from report to fix? To being *sure* it was fixed? How did you know?
8. What did it cost: refunds, churn, engineering hours, escalations?
9. How often does something like this happen? Last quarter, roughly?
10. What do you use today: monitoring, logs, runbooks, AI tools? What's missing?

## Trust and buying (6 min)
11. If a tool proposed the fix, what would you need to see before approving it?
12. Would you give a tool read-only access to billing and your integration repo? In test mode? Under what conditions?
13. Who would decide to buy something like this? Is there a budget line it would come from?
14. What do you pay today for related tools (incident management, observability, AI coding)?

## Demo and close (5 min)
15. Show the two-minute demo. "What's the first thing you'd worry about? What would make this useless for you?"
16. "If we ran a pilot on your test-mode billing with one past incident, would you be open to that?"
17. "Who else should I talk to?"

## After the call (same day)
Fill in the evidence template: facts only, separate from your interpretation. Mark any commitment signal exactly as
given. Do not round "maybe" up to "yes".
