# Six-minute pitch script

Structure: **0:00–2:00** the two-minute live demo ([DEMO_SCRIPT_2_MIN.md](DEMO_SCRIPT_2_MIN.md)), then
**2:00–6:00** Ahmad on camera with slides. The presentation narration below is counted by
`python scripts/script_timing.py competition/PITCH_SCRIPT_6_MIN.md` (results in [PITCH_TIMING.md](PITCH_TIMING.md)).
Speak plainly, look at the camera, and pause on the numbers.

Lines marked ⚠ contain a claim that depends on founder evidence. Use the bracketed fallback until it exists.

| Time | Slide | Narration |
|---|---|---|
| 0:00–2:00 | Demo video (slide 7) | (two-minute demo, its own narration) |
| 2:00–2:24 | 2 The incident | "What you just saw is a failure that no dashboard catches. The customer paid. Every system said success. The customer still couldn't use what they paid for. Someone has to notice, then an engineer spends hours tracing it across billing, webhooks, code and access data." |
| 2:24–2:46 | 3 Who has it | "This hits every software company that sells subscriptions, especially small teams with no billing specialist. Support feels it first, then engineering, then finance through refunds. ⚠ [Fallback: We're now interviewing SaaS teams to measure how often this happens and what it costs.]" |
| 2:46–3:08 | 4 Today | "Today's tools stop early. Monitoring sees a 202 and is happy. Coding assistants can write a patch, but they judge success by tests passing, not by whether the customer actually got access. And a guess is dangerous when money is involved." |
| 3:08–3:52 | 5–6 Solution and workflow | "IntegrationRescue is an AI agent that works like a careful engineer. It forms hypotheses, checks each system, reproduces the failure in a copy, and proposes the smallest fix. It tests it, and asks a human to approve. Then a separate verifier, which the AI cannot influence, checks the business result: right plan, one charge, one grant. That's why it's an agent and not an automation: it decides what to investigate, whether a fix is needed at all, and when it can't know." |
| 3:52–4:21 | 9 Evidence | "We measure this. In our live tests with Google Gemini, the agent diagnosed all 31 scored incidents correctly. After one fix to our tools, it reached the right outcome in 16 of 17, including knowing when to change nothing. Zero false success claims, zero double charges. Code repairs aren't reliable yet. We publish that too." |
| 4:21–4:48 | 10 Safety | "Safety lives in code, not in the prompt. In one test, the AI trusted a security key it should have checked. We didn't just fix the prompt. We made the system refuse that change, whatever the model says. Every repair needs human approval, and only the independent check can say verified." |
| 4:48–5:07 | 11 Defensibility | "Our moat is verified outcomes. Every incident becomes a test case with hidden ground truth, so we can prove reliability, and that library grows with every customer. We're model-agnostic, so better models make us better." |
| 5:07–5:34 | 12–13 Business and market | "We plan to charge for outcomes: a platform fee, plus a fee per verified fix, with nothing for a guess. We'll start with SaaS teams on common billing platforms, here in the UAE first, then globally through billing-platform marketplaces. ⚠ [Fallback: Pricing is a hypothesis we are testing with design partners.]" |
| 5:34–5:48 | 14 Roadmap | "Today it's a working prototype on simulated systems with fictional data. Next: real read-only connectors, design-partner pilots on test-mode billing, and stronger isolation for customer code." |
| 5:48–6:00 | 15 Close | "Software will keep connecting to software. IntegrationRescue makes sure that when it breaks, the fix is proven, not guessed. I'm Ahmad. Thank you." |

## Delivery notes
- The face must be visible from 2:00 to 6:00 (picture-in-picture over slides is fine).
- Do not say "customers", "pilots", "traction" or any market size unless real evidence has been added
  (see PROBLEM_VALIDATION_PLAN). When it has, replace the ⚠ fallback with counts, for example "6 of 10 teams we
  interviewed had this in the last six months".
- If asked "is it live?": "The demo is a recording of a live Gemini run; the agent's path is not scripted." Keep the
  raw recording.
