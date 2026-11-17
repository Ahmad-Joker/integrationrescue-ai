# Demo backup plan

The rule throughout: **never present a deterministic-baseline run as the AI agent**, and never present a recording
as happening now.

| Situation | Action | What to say |
|---|---|---|
| Live run fails with MODEL UNAVAILABLE (429/503) | wait 60 s, start a new incident; switch `IR_GEMINI_MODEL` to another model with quota | "Google's free tier is rate-limited; the system refuses to claim anything while the model is down. Retrying." |
| Daily quota gone | play the **backup live recording** (below) | "This is a recording of a live run from <date>." |
| Agent ends DIAGNOSED (patch rejected three times) | show the rejected attempts and the policy reasons, then the backup recording | "It refused to ship an unproven fix, which is the point. Here is a run where the repair succeeded, recorded on <date>." |
| Deployed site down or asleep | use the local demo server (`dev.ps1 judge-demo`) or the recording | "Running it locally / recorded on <date>." |
| Everything fails on stage | baseline run, **announced as the baseline**, to show the pipeline | "This is the rule-based baseline, not the AI. It shows the same pipeline and verifier." |

## Backup live recording (prepare in advance)
1. Record one full raw live Gemini run following DEMO_RECORDING_CHECKLIST.md. Keep the unedited file.
2. Save the incident evidence: `GET /api/incidents/<id>` JSON and `/api/incidents/<id>/report.md`. Store them privately
   or in `evidence/live/` (fictional data, no secrets). The model usage in the JSON shows it was live.
3. Caption the video "Recorded live on <date> · gemini-3.1-flash-lite".
4. Make an edited 2-minute version (the submission demo) plus the raw file (proof if judges ask).

If the competition rules require the demo to be live or unedited, follow the rules: the raw recording plus the
public URL are the fallback.
