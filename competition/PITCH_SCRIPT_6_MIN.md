# Six-minute pitch script

Structure: **0:00–2:00** the two-minute live Gemini demo ([DEMO_SCRIPT_2_MIN.md](DEMO_SCRIPT_2_MIN.md)), then
**2:00–6:00** Ahmad Essam Abdelaziz on camera with slides. The presentation narration is counted by
`python scripts/script_timing.py competition/PITCH_SCRIPT_6_MIN.md`; results are in [PITCH_TIMING.md](PITCH_TIMING.md).
Target: finish between 5:40 and 5:55. Speak plainly, look at the camera, and pause on the numbers.

Lines marked ⚠ depend on founder evidence. Say the bracketed fallback until that evidence exists. The 🔗 line is only
said once a public deployment has passed `verify_deployment.py`; otherwise skip it (the timing below includes it).

| Time | Slide | Narration |
|---|---|---|
| 0:00–2:00 | Demo video (slide 7) | (two-minute demo, its own narration) |
| 2:00–2:21 | 2 The incident | "What you just saw is a failure no dashboard catches. The customer paid, every system said success, and the customer still couldn't use what they paid for. Someone has to notice. Then an engineer spends hours tracing it across billing, webhooks, code and access data." |
| 2:21–2:41 | 3 Who has it | "This can hit any software company whose billing controls product access, especially small teams with no billing specialist. Support feels it first, then engineering, then finance through refunds. ⚠ [Fallback: We're now interviewing SaaS teams to measure how often this happens and what it costs.]" |
| 2:41–2:56 | 4 Today | "Today's tools stop early. Monitoring sees a 202 and is happy. Coding assistants can write a patch, but they judge success by tests passing, not by whether the customer actually got access." |
| 2:56–3:34 | 5–6 Solution and workflow | "IntegrationRescue is an AI agent that works like a careful engineer. It forms hypotheses, checks each system, reproduces the failure in a copy and proposes the smallest fix. It tests it, and asks a human to approve. Then a separate verifier, which the AI cannot influence, checks the business result: right plan, one charge, one grant. That's why it's an agent and not an automation: it decides what to investigate, whether a fix is needed at all, and when it can't know." |
| 3:34–4:02 | 9 Evidence | "We measure this. In live tests with Google Gemini, the agent diagnosed all 31 scored incidents correctly. After one fix to our tools, it reached the right outcome in 16 of 17, and all 11 configuration and trust repairs were verified. Zero false success claims, zero double charges. Code repairs are not reliable yet: zero of five. We publish that too." |
| 4:02–4:25 | 10 Safety | "Safety lives in code, not in the prompt. In one test, the AI trusted a security key it should have checked. We didn't just change the prompt. We made the system refuse that change, whatever the model says. Every repair needs human approval, and only the independent check can say verified." |
| 4:25–4:39 | 11 Defensibility | "Our advantage is verified outcomes. Every incident becomes a test case with hidden ground truth, so we can prove reliability, and that library grows with every pilot. And we're model-agnostic." |
| 4:39–4:54 | 12 Business model | "We plan to charge for outcomes: a platform fee, plus a fee per verified fix, and nothing for a guess. ⚠ [Fallback: That pricing is a hypothesis we'll test with design partners.]" |
| 4:54–5:12 | 13 Market entry | "I'm based in Egypt, so we start interviews and pilots there and in the UK, through my own network. This championship opens the UAE ecosystem as an expansion market. The product itself is global: connectors follow billing platforms, not borders." |
| 5:12–5:23 | 14 Roadmap | "Today it's a working prototype on simulated systems with fictional data. Next come real read-only connectors, design-partner pilots, and stronger isolation for customer code." |
| 5:23–5:44 | 15 Founder and ask | "I'm Ahmad Essam Abdelaziz, an artificial-intelligence student at AAST and an AI-agent developer. I built this because agents are only useful when their results can be trusted. We're looking for design partners: SaaS engineering teams willing to test the workflow on fictional or test-mode data." |
| 5:44–5:55 | 15 Close | "🔗 Judges can try the live demo at the link on screen. When software breaks between systems, IntegrationRescue fixes it, and proves it. Thank you." |

## Delivery notes
- The face must be visible from 2:00 to 6:00 (picture-in-picture over slides is fine).
- Never say "customers", "pilots", "traction" or any market size until real evidence has been added (see
  PROBLEM_VALIDATION_PLAN). The ask is for design partners; there are no existing customers. Once evidence exists,
  replace the ⚠ fallback with counts, for example "6 of 10 teams we interviewed had this in the last six months".
- Location: Ahmad is based in Egypt. Do not imply he lives in the UAE or has a UAE network.
- If asked "is it live?": "The demo is a recording of a real Gemini-powered run. The agent produced the investigation
  path; it was not replayed from the baseline." Keep the raw recording.
- No 🔗 line without a verified public URL.
