# Two-minute demo script (live Gemini agent)

Target: **1:50**. The narration is 218 words (`python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md`):
1:33 at 140 words per minute, 1:40 at 130, which leaves about 10–15 s for on-screen pauses. Recorded from a real live run (see `DEMO_RECORDING_CHECKLIST.md`). Agent waits are cut, and the cut
is captioned. Nothing is staged: if the run differs, narrate what it actually did.

Setup off camera: local demo server or deployed URL, state reset, incident "Paid for Pro, still on Free" selected,
decision maker **Live AI agent (Gemini)**.

| Time | Screen | Narration |
|---|---|---|
| 0:00–0:12 | New incident page; the ticket text | "A customer paid for Pro. Billing says succeeded. The webhook says 202 Accepted. And the customer is still on Free. Nothing alerted, because every system thinks it worked." |
| 0:12–0:20 | Click **Create and investigate**; the **LIVE AI AGENT (gemini)** banner | "Here IntegrationRescue gets the ticket. This is the live Gemini agent, not a script. Everything you see is simulated, with fictional data." |
| 0:20–0:45 | Investigation tab: tool calls stream in; hypotheses H1–H3 (caption: "sped up 4×") | "It decides what to check. Billing: paid for Pro. Entitlements: Free. Was the webhook lost? No, delivered and acknowledged. Did the handler crash? No. So it reads the integration code and the tenant config, and finds that the Pro price is missing from this tenant's plan mapping." |
| 0:45–0:55 | Reproduction "FAIL (failure reproduced in isolation)" | "Before touching anything, it replays the real event in an isolated copy. Still Free. Failure reproduced." |
| 0:55–1:15 | Repair tab: one-line diff, risk *low*, suite PASS, regression test FAIL-before, sandbox replay PASS | "It proposes one line. Our policy checks the scope. The tests pass, and a new regression test fails on the old code, which proves it tests this bug. A replay in the sandbox now grants Pro." |
| 1:15–1:25 | Type name, click **Approve & promote** | "Nothing ships without a human. I review the evidence and approve." |
| 1:25–1:42 | Verification tab: each check ✓; reproduction table shows the same checks ✗ before | "Now an independent verifier, which the AI cannot touch, reads billing directly. Paid plan: Pro. Exactly one charge. Granted once, even though the webhook was delivered twice. Only this check can say VERIFIED." |
| 1:42–1:50 | Dashboard / Evaluation lab, live runs highlighted | "It's a prototype on simulated systems. Config repairs are strong, code repairs aren't reliable yet, and we show both. Every fix it claims, it proves." |

**Timing check:** rehearse with a stopwatch. If a take runs past 1:55, drop the sentence "Nothing alerted, because
every system thinks it worked." and shorten the investigation segment to two checks.

**Must be visible:** broken integration (0:00) · business impact (0:00–0:12) · live agent start (0:12) · tool use
(0:20) · bounded repair (0:55) · approval gate (1:15) · sandbox/regression evidence (0:55–1:15) · promotion (1:15) ·
independent verification (1:25) · final business result (1:25–1:42) · limitation (1:42).
