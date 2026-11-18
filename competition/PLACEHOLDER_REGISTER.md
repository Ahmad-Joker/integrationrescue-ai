# Placeholder register (2026-11-18)

Every placeholder that is deliberately left in the submission materials. None can be filled from the repository:
each needs Ahmad or a completed founder action. Search for them with
`grep -rn "PLACEHOLDER\|\[your email\]\|\[recording date\]\|<service>\|<host>" README.md docs competition`.

| # | File(s) | Field | Why it is missing | Who supplies it | Blocks submission? |
|---|---|---|---|---|---|
| 1 | `competition/deck_data.json` (slides 1 and 15), the .pptx, `competition/AGENT_CARD.md`, `docs/JUDGE_ACCESS.md` | `[PLACEHOLDER: founder email]` | No verified public contact email has been provided; it must not be invented | Ahmad (choose a public address) | **Yes** (the Agent Card and deck need a contact) |
| 2 | `competition/INTERVIEW_OUTREACH_MESSAGES.md` | `[your email]` | same as 1 | Ahmad | No (needed only for the cold email) |
| 3 | `competition/deck_data.json` (slide 15), the .pptx | `[PLACEHOLDER: founder photo]` | needs a real photo of Ahmad | Ahmad | No, but strongly recommended (team slide) |
| 4 | `deck_data.json` (slide 15), the .pptx, `docs/JUDGE_ACCESS.md` | `[PLACEHOLDER: public demo URL]` | no deployment exists; a URL may only be added after `verify_deployment.py` passes against it | Ahmad (deploy: USER_ACTIONS A2–A3) | **Yes** (judge access is required) |
| 5 | `deck_data.json` (slide 15), the .pptx | `[PLACEHOLDER: QR code to demo]` | depends on 4 | Ahmad (generate from the verified URL) | No |
| 6 | `deck_data.json` (slide 7), the .pptx | `[PLACEHOLDER: 2-minute demo video link]` | the video has not been recorded | Ahmad (A5) | **Yes** |
| 7 | `deck_data.json` (slide 7), the .pptx, `DEMO_SHOT_LIST.md`, `DEMO_BACKUP_PLAN.md` | `[PLACEHOLDER: recording date]` / `[recording date]` | depends on 6 | Ahmad | No (but caption the video with it) |
| 8 | `docs/JUDGE_ACCESS.md` | `[PLACEHOLDER: host and plan]` | depends on 4 | Ahmad | No (fill with 4) |
| 9 | `docs/DEPLOYMENT.md`, `competition/USER_ACTIONS.md` | `<service>`, `<host>`, `<URL>`, `<the access code>` | command templates: they are filled in when typing the command, never committed | Ahmad at deploy time | No |
| 10 | Pitch script, deck slide 3 | ⚠ fallback sentences ("We're now interviewing…", "That pricing is a hypothesis…") | no interview or pricing evidence exists | Ahmad (A10, B1) | No: the fallbacks are honest as written |

When a placeholder is filled: edit `deck_data.json`, run `python scripts/build_deck.py` and
`powershell -File scripts/render_deck.ps1`, re-check the affected slides (see DECK_QA.md), and update this register.
