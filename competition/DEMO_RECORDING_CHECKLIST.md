# Demo recording checklist (two minutes, live Gemini)

## One-command setup
```powershell
./scripts/dev.ps1 record
```
This builds the dashboard and starts a fresh judge demo at http://127.0.0.1:8080, with **live Gemini**
(`gemini-3.1-flash-lite`) as the default decision maker, then opens the browser on *New incident*. The console
prints a throwaway access code: type it into the purple banner, then move the console off screen. Also complete
[LIVE_DEMO_CHECKLIST.md](LIVE_DEMO_CHECKLIST.md).

## Recorder
OBS Studio is **not installed** on this machine (checked 2026-11-18). Either option works:
- **Windows Snipping Tool → Record** (Windows 11, built in): select the browser window, record, save MP4.
  Simplest choice; records the microphone if enabled.
- **OBS Studio** (free, obsproject.com; installing it is your decision). Suggested scenes:
  1. *Demo*: Window Capture (browser) at 1920×1080 + microphone. Hide the taskbar.
  2. *Demo + face*: same, plus Video Capture Device (webcam) at 20% size, bottom-right corner (optional for the demo).
  3. *Pitch*: Display Capture (slides in PowerPoint slideshow) + webcam at 25% bottom-right (face required 2:00–6:00).
  Settings: Output → Recording format mp4, 1080p, 30 fps; Audio → mic only, desktop audio off.

## Before
- [ ] Microphone tested: 10 seconds recorded and listened back; quiet room
- [ ] Browser: a single tab, bookmarks bar hidden, zoom 110%, no extension icons showing
- [ ] Nothing private visible: no `.env`, no console with codes, no email or other tabs. The access code never appears on screen
- [ ] Featured incident "Paid for Pro, still on Free" selected; Decision maker = **Live AI agent (Gemini)**
- [ ] Gemini quota for at least two attempts (about 15 requests each)

## Recording
- [ ] Record the full raw live run once, without narration. Keep the file: it is the proof that the run was live
- [ ] Narrate from DEMO_SCRIPT_2_MIN.md, live or as a voice-over; cut rather than speed up your speech
- [ ] The LIVE AI AGENT banner is visible before you say "AI"
- [ ] You click **Approve & promote** yourself, on camera
- [ ] Every one of the 12 proofs in DEMO_SCRIPT_2_MIN.md ("What the video must visibly prove") appears on screen

## Editing
- [ ] Final length 1:50–1:55, hard maximum 2:00
- [ ] Every speed-up or cut is captioned ("sped up 4×", "waiting cut")
- [ ] English captions (auto-generate, then correct: IntegrationRescue, Gemini, webhook, entitlement)
- [ ] Lower-third with the real recording date; end card with the repository URL
- [ ] No claim on screen that is not in TECHNICAL_EVIDENCE.md

## Publish
- [ ] Upload as **Unlisted** (YouTube) or as the portal requires; title "IntegrationRescue: 2-minute live agent demo"
- [ ] Test the link in a private window; put it in the deck (slide 7), PLACEHOLDER_REGISTER.md and SUBMISSION_READINESS.md
- [ ] Save the incident evidence: `/api/incidents/<id>` JSON and `/api/incidents/<id>/report.md` (fictional data, no secrets)
