# Founder actions (only Ahmad can do these)

Everything that can be done from the repository is done. The steps below need Ahmad's accounts, face, voice,
decisions or real people. Do them **in this order**. Submission window: the portal opens **4 December 2026**; the
deadline is **4 January 2027**. Keep judge access up until the championship ends.

Never paste an API key, access code or admin code into a chat, an issue, a commit or a screenshot.

## A. Required before submission
| # | Action | Why | Exact steps | Evidence when done | Time | Depends on |
|---|---|---|---|---|---|---|
| A1 | ~~Push the November commits~~ | | done 2026-11-18: `a3ffbcd`, CI run 44201542793 green (backend, frontend, container) | | | |
| A2 | **Approve and push this session's commit plan** | CI must run on the current code | review the plan in this session and say "push"; then check that all 3 jobs on the Actions tab are green | green run link | 10 min | — |
| A3 | **Choose a public contact email** | the Agent Card, deck and judge page need one; it must not be invented | pick the address → replace `[PLACEHOLDER: founder email]` (see PLACEHOLDER_REGISTER #1) | updated files, deck rebuilt | 10 min | — |
| A4 | **Deploy on Render (free plan)** | judges need a URL | see "Deployment, step by step" below | service URL | 30–45 min | A2 |
| A5 | **Verify the public URL** | never claim a deployment that wasn't tested | post-deployment commands below; both must print `15/15 checks passed` | outputs pasted into `docs/JUDGE_ACCESS.md` with the date | 15 min | A4 |
| A6 | **Record the 2-minute live demo** | required item | `./scripts/dev.ps1 record`, then follow `DEMO_RECORDING_CHECKLIST.md` and `LIVE_DEMO_CHECKLIST.md`; keep the raw file | unlisted video link | 2–3 h | A2 (A5 if recording on the deployed URL) |
| A7 | **Finish the deck assets** | required item; the deck is a final-design candidate awaiting founder assets | add photo, email, video link and date (and, after A5, URL and QR) in `deck_data.json` → `python scripts/build_deck.py` → `powershell -File scripts/render_deck.ps1` → check slides 1, 7, 15 | final .pptx (+ PDF export if needed) | 1 h | A3, A6 |
| A8 | **Record the 6-minute pitch, face visible** | required item | `PITCH_SCRIPT_6_MIN.md`, `PITCH_TIMING.md`, `PITCH_RECORDING_CHECKLIST.md`; demo at 0:00–2:00; target 5:40–5:55 | unlisted video link | 3–4 h | A6, A7 |
| A9 | **Confirm requirements in the portal** (from 4 Dec) | check video limits, file formats and judge-access fields against our materials | log in → note every requirement → correct SUBMISSION_READINESS if anything differs | notes in SUBMISSION_READINESS | 30 min | portal open |
| A10 | **Keep judge access alive** until the championship ends | required | check the URL weekly and after every push (`verify_deployment.py`); keep the Gemini key valid; the free plan sleeps (first load about a minute). A paid always-on plan is **your spending decision** | weekly check log in JUDGE_ACCESS | 5 min/week | A5 |
| A11 | **Submit through the portal** (before 4 Jan 2027) | final step | upload deck, both video links, repository link, Business Model Canvas (`BUSINESS_MODEL_CANVAS.md`, export to PDF), Agent Card (`AGENT_CARD.md`), judge URL; the access code goes only in a private field | confirmation email or screenshot | 1 h | all above |

## B. Strongly recommended
| # | Action | Why | Exact steps | Evidence | Time | Depends on |
|---|---|---|---|---|---|---|
| B1 | **Customer interviews (target 10)** | the largest scoring gap: "Real value and problem validation" has no evidence | `INTERVIEW_TARGET_PROFILE.md` → messages in `INTERVIEW_OUTREACH_MESSAGES.md` → `CUSTOMER_INTERVIEW_SCRIPT.md` → private tracker from `INTERVIEW_TRACKER_TEMPLATE.csv` → `VALIDATION_SUMMARY_TEMPLATE.md`; then replace the ⚠ fallbacks in the pitch and slide 3 | filled summary | 2–3 weeks | — |
| B2 | **Decide the licence** | a public repo without a licence is "all rights reserved"; judges may ask | **MIT**: permissive open source, the simplest choice. **Apache-2.0**: permissive, plus an explicit patent grant and patent-retaliation clause. **No licence (all rights reserved)**: only if you intend that and the competition allows it. Add a `LICENSE` file for the one you choose | `LICENSE` in the repo | 10 min | — |
| B3 | **Rotate the Gemini key used in development** | it was used on this machine and in local logs | Google AI Studio → new key for the deployment; delete old ones; update `.env` locally | — | 10 min | before A4 |
| B4 | **Decide on `.claude/launch.json`** | it is tracked and contains absolute paths from your machine (your Windows user folder); it is only used by the Claude desktop app's preview, not by the project | recommended: `git rm --cached .claude/launch.json`, add `.claude/launch.json` to `.gitignore` (the local file keeps working), commit. Or keep it tracked | — | 2 min | — |
| B5 | **Approve pricing points to test** | the deck shows "pay per verified fix" as a hypothesis | read `PRICING_AND_UNIT_ECONOMICS.md`; choose 3 price points to test in interviews; never present them as validated | chosen points in the file | 30 min | — |
| B6 | **Run the coding-agent comparison** | backs up, or refutes, the differentiation claim | `COMPARISON_PROTOCOL.md`; ideally a friend operates arm C; results in `evidence/comparison/` | RESULTS.md | 1 day | A2 |
| B7 | **Captions and audio check** for both videos | accessibility and clarity | YouTube auto-captions → correct the names | — | 30 min | A6, A8 |

## C. Optional
| # | Action | Why | Time |
|---|---|---|---|
| C1 | Enable Google billing for a stronger model and more live runs (**spending decision**) | better code-repair numbers; fewer 429 errors | 15 min + cost |
| C2 | More live schema-drift runs on another free model | measure code repair on at least 6 runs | 1 h per day of quota |
| C3 | Ask a mentor to watch the 6-minute video cold | an outside view before submitting | 1 h |
| C4 | Install OBS Studio (free) if Snipping Tool's recorder is not enough | picture-in-picture face for the pitch | 20 min |

## Deployment, step by step (A4–A5)
**Before:** Docker Desktop running, then from the repo root:
```powershell
./scripts/dev.ps1 preflight
```
It must end with `PREFLIGHT PASSED`. It runs lint, the tests and the frontend build, builds the image, checks that
it refuses to start without an access code, and runs the 15 judge-flow checks in the container.

**Generate two codes** in your own terminal (they appear only there; save them in a password manager):
```powershell
.venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(18))"
```
Run it twice: the first output is `IR_ACCESS_TOKEN` (for judges), the second is `IR_ADMIN_TOKEN` (for you only).

**On render.com** (sign in with your own account; the free plan needs no card):
1. *New* → *Blueprint* → connect GitHub → select `Ahmad-Joker/integrationrescue-ai` → Render reads `render.yaml`.
2. Render asks for three secret values. Type them **only into Render's form**:
   - `IR_ACCESS_TOKEN` = first code
   - `IR_ADMIN_TOKEN` = second code
   - `GEMINI_API_KEY` = your (rotated, see B3) Google AI Studio key
3. Confirm the plan shows **Free**, then *Apply*. Wait for the deploy to finish and copy the URL
   (`https://<service>.onrender.com`).

**After** (post-deployment check, from the repo root):
```powershell
$env:IR_ACCESS_TOKEN = Read-Host "Access code" -AsSecureString | ForEach-Object { [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($_)) }
.venv\Scripts\python scripts\verify_deployment.py --url https://<service>.onrender.com
.venv\Scripts\python scripts\verify_deployment.py --url https://<service>.onrender.com --provider gemini
```
Both must print `15/15 checks passed` (the second spends about 15 free-tier requests). Then:
- reset the demo state: `curl.exe -X POST -H "x-admin-token: <admin code>" https://<service>.onrender.com/api/admin/reset`;
- cold-start check: wait 20 minutes, open the URL, and note how long the first load takes (put it in JUDGE_ACCESS);
- record the URL, the date and both results in `docs/JUDGE_ACCESS.md` and `SUBMISSION_READINESS.md`, and replace the
  URL placeholders (PLACEHOLDER_REGISTER #4, #5, #8). Never write the access code into the repository.
