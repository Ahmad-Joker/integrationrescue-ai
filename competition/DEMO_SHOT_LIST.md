# Demo shot list (matches DEMO_SCRIPT_2_MIN.md)

Capture at 1920×1080, 30 fps, browser zoom 110%, cursor highlighting on. Record the whole live run in one take, then
cut. Keep the raw recording: it proves the run was live. Reference stills of every shot from a real live run:
`competition/screenshots/` (`02` … `13`).

| # | Time | Shot | Zoom / emphasis | Caption on screen | Reference still |
|---|---|---|---|---|---|
| 1 | 0:00–0:11 | New incident page: featured card "Paid for Pro, still on Free" and its impact line; Decision maker shows **Live AI agent (Gemini)** | zoom to the card, then the Decision maker field | "Fictional customer · simulated billing" | 02 |
| 2 | 0:11–0:26 | Click Create; the incident page opens with the **LIVE AI AGENT … (gemini)** banner | hold 2 s on the banner | "Real Gemini-powered run" | 03, 04 |
| 3 | 0:26–0:49 | Investigation tab: tool calls appear with rationale; the Hypotheses panel updates (refuted / supported) | speed ramp 4× on waiting; normal speed when a hypothesis turns "supported" | "Sped up 4× · tool calls chosen by the agent" | 05, 06 |
| 4 | 0:49–0:56 | Root cause panel: "Reproduced FAIL (failure reproduced in isolation)" | zoom | "Reproduced before any change" | 07 |
| 5 | 0:56–1:05 | Repair tab: the diff in `tenants/<tenant>.json`; policy risk **low** | zoom on the added mapping entry | "Bounded repair · allow-listed file" | 08 |
| 6 | 1:05–1:15 | Same panel: Test suite PASS · Regression (unpatched) **FAIL** · Sandbox replay PASS | slow pan across the three badges | "Fails before · passes after · replayed in a sandbox" | 08 |
| 7 | 1:15–1:24 | Type your name, click **Approve & promote**; the pipeline moves to Promote → Verify | real speed | "Human approval required" | 09 |
| 8 | 1:24–1:40 | Verification tab: "Environment after promotion" all ✓; then "Reproduction (unpatched)" ✗ | zoom on `entitlement_matches_paid_plan`, `exactly_one_successful_charge`, `entitlement_granted_once_for_event` | "Independent verifier · read-only" | 10, 11 |
| 9 | 1:40–1:52 | Evaluation lab with a live Gemini run selected | hold | "Prototype · simulated systems · code repair not yet reliable" | 13 |

Your face is optional in the demo (picture-in-picture in a corner) and required in the pitch. Lower-third at the
start: "IntegrationRescue · live Gemini run recorded [PLACEHOLDER: recording date]".

The agent may record a different number of hypotheses or call tools in another order. Film what it actually does;
never re-take until it "looks scripted".
