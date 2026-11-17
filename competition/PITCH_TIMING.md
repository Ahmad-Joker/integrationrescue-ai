# Pitch timing

Measured with `python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md competition/PITCH_SCRIPT_6_MIN.md`
(narration words; the ⚠ fallback sentences are included in the count).

| Part | Window | Words | At 130 wpm | At 140 wpm | At 150 wpm | Headroom at 140 wpm |
|---|---|---|---|---|---|---|
| Demo (DEMO_SCRIPT_2_MIN) | 0:00–2:00 (target 1:50) | 218 | 1:40 | 1:33 | 1:27 | ~17 s for on-screen pauses |
| Presentation (PITCH_SCRIPT_6_MIN) | 2:00–6:00 | 451 | 3:28 | 3:13 | 3:00 | ~47 s |
| **Total** | **6:00** | 669 | 5:08 + demo pauses | 4:46 + pauses | | fits |

Segment budget for the presentation (seconds proportional to words, about 113 wpm effective including pauses):

| Segment | Slides | Words | Seconds |
|---|---|---|---|
| The incident | 2 | 45 | 24 |
| Who has it | 3 | 42 | 22 |
| Today's tools | 4 | 41 | 22 |
| Solution and workflow | 5–6 | 82 | 44 |
| Evidence | 9 | 55 | 29 |
| Safety | 10 | 51 | 27 |
| Defensibility | 11 | 35 | 19 |
| Business and market | 12–13 | 51 | 27 |
| Roadmap | 14 | 26 | 14 |
| Close | 15 | 23 | 12 |

Rehearsal rule: do three timed run-throughs. If any is over 5:55, cut from "Defensibility" first, then "Today's tools".
Slides 1 and 8 (title, architecture) are shown without narration or skipped in the video. Slide 8 is for Q&A.
