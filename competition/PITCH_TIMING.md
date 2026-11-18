# Pitch timing

Measured with `python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md competition/PITCH_SCRIPT_6_MIN.md`.
Counts are narration words; the ⚠ fallback sentences and the 🔗 judge-access line are included.

| Part | Window | Words | At 130 wpm | At 140 wpm | At 150 wpm |
|---|---|---|---|---|---|
| Demo (DEMO_SCRIPT_2_MIN) | 0:00–2:00 (target about 1:50) | see DEMO_SCRIPT_2_MIN | | | |
| Presentation (PITCH_SCRIPT_6_MIN) | 2:00–5:55 | 512 | 3:56 | 3:39 | 3:24 |
| **Full pitch** (2:00 demo slot + presentation) | **≤ 6:00** | | **5:56** | **5:39** | **5:24** |

At a natural 140 wpm, the speech alone ends at about 5:39. Pauses on the evidence numbers and slide changes bring a
take to roughly 5:45–5:55. At a slow 130 wpm there is almost no pause budget, so:

- If a rehearsal goes over 5:55, first drop the 🔗 line (only valid with a deployment anyway), then the sentence
  "And we're model-agnostic.", then shorten "Today's tools".
- If a rehearsal is under 5:35, slow down; do not add claims.

## Segment budget (timestamps in the script are proportional to words)
| Segment | Slide | Words | Seconds |
|---|---|---|---|
| The incident | 2 | 45 | 21 |
| Who has it | 3 | 45 | 20 |
| Today's tools | 4 | 32 | 15 |
| Solution and workflow | 5–6 | 82 | 38 |
| Evidence | 9 | 61 | 28 |
| Safety | 10 | 51 | 23 |
| Defensibility | 11 | 30 | 14 |
| Business model | 12 | 32 | 15 |
| Market entry (Egypt, UK, UAE expansion) | 13 | 40 | 18 |
| Roadmap | 14 | 24 | 11 |
| Founder and ask | 15 | 45 | 21 |
| Judge access + close | 15 | 25 | 11 |

Slides 1 and 8 (title, architecture) are shown without narration; slide 8 is a Q&A backup.
Rehearsal rule: three timed run-throughs before recording, with a stopwatch, at your natural pace.
