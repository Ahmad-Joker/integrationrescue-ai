# Deck QA: 2026-11-18

**Status: final-design candidate awaiting founder assets.** It is not final: the founder email, founder photo,
demo-video link, recording date, public demo URL and QR code are still placeholders (see PLACEHOLDER_REGISTER.md).

## How the deck is produced and checked
1. Screenshots: `node frontend/scripts/capture-screenshots.mjs --url <judge-demo URL> --out competition/screenshots`
   ran against a local judge-demo server (`scripts/serve_demo.py`, demo mode, fictional data). It produced one real
   **live Gemini** run, `inc_2376f4f829` (gemini-3.1-flash-lite, 13 model calls, 43,921 input / 765 output tokens),
   approved through the human-approval step by the script as "Demo reviewer" (auto-approval off), outcome VERIFIED. Metadata: `competition/screenshots/capture.json`. The access code is
   injected into session storage and never appears on screen; there is no browser chrome.
2. Deck: `python scripts/build_deck.py` builds `IntegrationRescue_Competition_Deck.pptx` and `PITCH_DECK.md` from
   `deck_data.json`.
3. Render: `powershell -File scripts/render_deck.ps1` exports every slide through PowerPoint to
   `competition/deck_preview/slideNN.png` (1600×900). All 15 renders were opened and inspected.

## Iterations
| Round | Problems found | Fix |
|---|---|---|
| 1 | Slide 1: chip text wrapped; hero screenshot unreadable at that size | wider chips; replaced the screenshot with a drawn verified-checks panel |
| 1 | Slide 3: currency icon implied a country | removed icons (accent bars instead) |
| 1 | Slide 6: empty space under the bullets | larger type, tighter boxes |
| 1 | Slide 7: placeholders overlapped the screenshot | smaller screenshot, placeholders below it |
| 1 | Slide 10: approval-gate screenshot unreadable (too wide and thin) | 2×2 statement cards and a full-width verifier screenshot |
| 1 | Slide 12: cost line wrapped onto two lines | shortened |
| 1 | Slide 13: unnecessary citizenship detail on the slide | "Founder access" on the slide; reasoning kept in GO_TO_MARKET |
| 2 | Slide 14: empty space | larger type, shorter boxes |
| 2 | Evaluation lab (app) showed a diagnosis ✓ on runs excluded as infrastructure errors | UI now shows "—" for those rows (`frontend/src/pages.tsx`) |

## Final checklist (round 3 renders)
| Check | Result |
|---|---|
| Text overflow / clipping | none found on 15 slides |
| Screenshots readable where used (slides 5, 7, 10) | yes: slide 5 is a full product view; slide 7 sits behind the video placeholder; slide 10 verifier table is legible |
| Alignment and contrast | consistent grid; light text on a dark background; amber only for warnings and placeholders |
| Evidence numbers prominent | slide 9: six equal tiles; **0/5 code repair is the same size**, in amber |
| Hypotheses labelled | slide 3 (buyer), slide 12 (three HYPOTHESIS tags + beachhead), slide 13 ("plan, not traction") |
| Founder location | slide 13 and notes: based in Egypt; UAE as a championship-enabled expansion market. The phrase "based in the UAE" does not occur |
| Unsupported claims | none: no customers, pilots, interviews, market size or prices; comparison marked "not yet run" |
| Speaker notes with evidence source | all 15 slides (checked programmatically: every notes page contains "Evidence:") |
| Placeholders visible | slides 1, 7 and 15 show amber dashed `[PLACEHOLDER: …]` boxes |
| Private data | none: fictional customer email (`.example` domain), fictional tenant; no keys, codes or local paths. File metadata: author = founder name |

## What remains (founder)
Add a photo, email, demo-video link and date, then (only after a verified deployment) the URL and QR code. Re-render,
and re-check slides 1, 7 and 15. Optional polish in PowerPoint: brand fonts and a logo mark.
