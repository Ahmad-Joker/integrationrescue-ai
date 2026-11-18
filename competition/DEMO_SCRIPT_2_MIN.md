# Two-minute demo script (live Gemini agent)

Target: **1:50–1:55**, hard maximum 2:00. The narration is 236 words (`python scripts/script_timing.py
competition/DEMO_SCRIPT_2_MIN.md`): 1:41 at 140 words per minute, 1:48 at 130. Timestamps are proportional to the words
and leave a short pause after the approval click and on the verifier. It is recorded from a real live Gemini run (see
`DEMO_RECORDING_CHECKLIST.md`). Agent waiting time is cut, and every cut is captioned. Nothing is staged: if the run
differs, narrate what it actually did.

Setup off camera: local demo server or deployed URL, state reset, incident "Paid for Pro, still on Free" selected,
decision maker **Live AI agent (Gemini)**.

| Time | Screen | Narration |
|---|---|---|
| 0:00–0:11 | New incident page; the ticket text | "A customer paid for Pro. Billing says succeeded. The webhook says 202 Accepted. And the customer is still on Free. No alert fired." |
| 0:11–0:26 | Click **Create and investigate**; the **LIVE AI AGENT (gemini)** banner | "IntegrationRescue gets the ticket. This is a real Gemini-powered run: the agent produces the investigation path; it is not replayed from our rule-based baseline. The systems are simulated, with fictional data." |
| 0:26–0:49 | Investigation tab: tool calls stream in; hypotheses H1–H3 (caption: "sped up 4×") | "It decides what to check. Billing: paid for Pro. Entitlements: Free. Was the webhook lost? No, delivered and acknowledged. Did the handler crash? No. So it reads the integration code and the tenant config, and finds that the Pro price is missing from this tenant's plan mapping." |
| 0:49–0:56 | Reproduction "FAIL (failure reproduced in isolation)" | "Before touching anything, it replays the real event in an isolated copy. Still Free. Failure reproduced." |
| 0:56–1:15 | Repair tab: one-entry diff, risk *low*, suite PASS, regression test FAIL-before, sandbox replay PASS | "It proposes a one-entry config change. Our policy checks the scope. A new regression test fails on the old code and passes on the fix, so it really tests this bug. The full suite passes, and a sandbox replay now grants Pro." |
| 1:15–1:24 | Type name, click **Approve & promote** | "Nothing ships without a human. I review the evidence and approve, and only then is the fix promoted." |
| 1:24–1:40 | Verification tab: each check ✓; reproduction table shows the same checks ✗ before | "Now an independent verifier, which the AI cannot touch, reads billing directly. Correct plan: Pro. Exactly one charge. One entitlement grant, even though the webhook was delivered twice. Only this check can say VERIFIED." |
| 1:40–1:52 | Dashboard / Evaluation lab, live runs highlighted | "It's a prototype on simulated systems. Config repairs are strong, code repairs aren't reliable yet, and we show both. Every fix it claims, it proves." |

**Timing check:** rehearse with a stopwatch. If a take runs past 1:55, shorten the investigation segment to two checks
("Billing: paid. Entitlements: Free.") rather than speaking faster.

## What the video must visibly prove
| # | Proof | Where | Shot (DEMO_SHOT_LIST) |
|---|---|---|---|
| 1 | Broken business outcome: paid, still Free | 0:00 | 1 |
| 2 | Live Gemini selected (banner LIVE AI AGENT, provider gemini) | 0:11 | 2 |
| 3 | Agent-created investigation path, tool use | 0:26 | 3 |
| 4 | Hypotheses refuted / supported | 0:26–0:49 | 3 |
| 5 | Reproduction before repair | 0:49 | 4 |
| 6 | Bounded repair (one mapping entry in an allow-listed tenant file, risk low) | 0:56 | 5 |
| 7 | Regression test fails before, passes after; full suite passes | 1:00–1:10 | 6 |
| 8 | Sandbox replay passes | 1:10 | 6 |
| 9 | Human approval click | 1:15 | 7 |
| 10 | Promotion (phase moves to promote, then verify) | 1:20 | 7 |
| 11 | Independent verifier: correct plan, one charge, one entitlement grant | 1:24–1:40 | 8 |
| 12 | Honest limitation | 1:40 | 9 |
