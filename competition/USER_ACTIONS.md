# Founder actions (only Ahmad can do these)

Everything that could be done in the repository is done. These steps need your accounts, your face, your
decisions or real people. The order is the suggested order.

## A. Required before submission
| # | Action | Why | Exact steps | Evidence when done | Time | Depends on |
|---|---|---|---|---|---|---|
| A1 | **Approve and push the commits** | CI must run on the current code; judges read GitHub | Review the commit plan in this session, say "push", then check the Actions tab for green on all three jobs (backend, frontend, container) | green run link in SUBMISSION_READINESS | 10 min | — |
| A2 | **Create a hosting account and deploy** | judges need a URL | Render: sign up (free) → New → Blueprint → select `integrationrescue-ai` → enter `IR_ACCESS_TOKEN`, `IR_ADMIN_TOKEN` (generate: `python -c "import secrets; print(secrets.token_urlsafe(18))"`) and `GEMINI_API_KEY` → Deploy. Details: `docs/DEPLOYMENT.md` | service URL | 30 min | A1 |
| A3 | **Verify the public URL** | never claim a deployment that wasn't tested | `$env:IR_ACCESS_TOKEN="<code>"` then `.venv\Scripts\python scripts\verify_deployment.py --url <URL>` and again with `--provider gemini` | two outputs "15/15 checks passed"; paste the URL and date into `docs/JUDGE_ACCESS.md` and SUBMISSION_READINESS | 15 min | A2 |
| A4 | **Keep judge access alive** until the final (first week of May 2027) | the requirement is access throughout | free Render instances sleep, so either accept the ~1 min first load (say so in JUDGE_ACCESS) or decide to pay for a non-sleeping plan (**your spending decision**); check the URL weekly and after every push; keep the Gemini key valid | weekly check log in JUDGE_ACCESS | 5 min/week | A3 |
| A5 | **Record the 2-minute live demo** | required item | follow `DEMO_RECORDING_CHECKLIST.md` + `LIVE_DEMO_CHECKLIST.md`; keep the raw recording | unlisted video link | 2–3 h | A1 (local) or A3 |
| A6 | **Record the 6-minute pitch, face visible** | required item | `PITCH_SCRIPT_6_MIN.md`, `PITCH_RECORDING_CHECKLIST.md`; demo at 0:00–2:00 | unlisted video link | 3–4 h | A5, A8 |
| A7 | **Finish the deck design** | required item; the .pptx is a text-first draft | open `IntegrationRescue_Competition_Deck.pptx`, add the visuals listed on each slide (screenshots from the dashboard), embed or link the demo on slide 7, add contact details on slides 1 and 15; export PDF if the portal wants it | final deck file | 2–3 h | A5 |
| A8 | **Decide what the pitch may claim about validation** | judges weight "Real value and problem validation" at 20% | do A10 if possible; otherwise use the ⚠ fallback lines in the pitch script unchanged | updated pitch script | 15 min | A10 |
| A9 | **Confirm official requirements in the submission portal** | the public page (updated 15 Oct 2026) lists prototype, deck, demo video and English only; the 6-minute video, BMC, Agent Card and weights are from your brief | log in to the portal when submissions open; note the exact deadline day, video limits and required files; correct SUBMISSION_READINESS if anything differs | portal text noted in SUBMISSION_READINESS | 30 min | — |
| A11 | **Submit through the official portal** | final step | upload deck, video links, repository link, BMC (`BUSINESS_MODEL_CANVAS.md`, export to PDF if needed), Agent Card (`AGENT_CARD.md`), judge URL and access code (private field, not public); check all links in a private window | submission confirmation email/screenshot | 1 h | all above |

## B. Strongly recommended
| # | Action | Why | Exact steps | Evidence | Time | Depends on |
|---|---|---|---|---|---|---|
| A10 | **Customer interviews (target 10)** | the biggest scoring gap: no validation evidence | `PROBLEM_VALIDATION_PLAN.md` + `CUSTOMER_INTERVIEW_SCRIPT.md`; anonymised notes in `competition/validation/` using the template | filled VALIDATION_EVIDENCE summary table | 3 weeks, ~1 h each | — |
| B1 | **Approve pricing hypotheses** | the deck shows "pay per verified fix" | read `PRICING_AND_UNIT_ECONOMICS.md`; pick 3 price points to test in interviews; never present them as validated | your chosen test points in the file | 30 min | — |
| B2 | **Run the coding-agent comparison** | backs up (or refutes) the differentiation claim | `COMPARISON_PROTOCOL.md`; ideally a friend runs arm C; save results in `evidence/comparison/` | RESULTS.md | 1 day | A1 |
| B3 | **Rotate the Gemini key used during development** | it has been used on several machines and logs | Google AI Studio → create a new key for the deployment; delete old ones | — | 10 min | before A2 |
| B4 | **Add a licence file** | public repo without a licence = all rights reserved; judges may ask | choose (e.g. MIT or a source-available licence) and add `LICENSE` | file in repo | 10 min | — |
| B5 | **Decide on `.claude/launch.json`** | it is tracked and contains a local Windows path | either `git rm --cached .claude/launch.json` and add `.claude/` to `.gitignore`, or keep it | — | 2 min | — |
| B6 | **Captions and audio check** for both videos | accessibility and clarity | YouTube auto-captions → correct names | — | 30 min | A5, A6 |

## C. Optional improvements
| # | Action | Why | Time |
|---|---|---|---|
| C1 | Enable Google billing for a stronger model and more live runs (**spending decision**) | better code-repair numbers; fewer 429s | 15 min + cost |
| C2 | More live schema-drift runs on a different free model | measure code repair on ≥6 runs | 1 h per day of quota |
| C3 | Ask a mentor to watch the 6-minute video cold | outside view before submitting | 1 h |
| C4 | A short written case study of one incident class for LinkedIn | channel test (GO_TO_MARKET phase 0) | 2 h |
