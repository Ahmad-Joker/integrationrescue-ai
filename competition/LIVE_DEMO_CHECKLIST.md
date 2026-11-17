# Live demo checklist

Tick every line before recording or presenting. Details: [docs/LIVE_DEMO_RUNBOOK.md](../docs/LIVE_DEMO_RUNBOOK.md).

**The day before**
- [ ] `GEMINI_API_KEY` works: `verify_deployment.py --provider gemini` printed 15/15 (uses about 15 requests)
- [ ] Model quota for today checked in Google AI Studio; at least 40 requests left (rehearsal + take + spare)
- [ ] Backup live recording exists and is captioned with its date (`DEMO_BACKUP_PLAN.md`)
- [ ] CI green on the commit being shown (GitHub Actions page)

**Ten minutes before**
- [ ] State reset (delete `var\demo` or `POST /api/admin/reset`)
- [ ] Dashboard opens; the purple "simulated and fictional" banner is visible
- [ ] Access code entered and accepted (deployed) or printed codes noted (local)
- [ ] New incident → "Paid for Pro, still on Free" selected → Decision maker shows **Live AI agent (Gemini)**
- [ ] Notifications off, browser zoom 110%, mouse cursor visible, terminal windows hidden

**During**
- [ ] Mode banner says **LIVE AI AGENT** before you talk about AI
- [ ] Pause on the hypotheses, the diff, the regression test FAIL-before, and the approval click
- [ ] You click **Approve & promote** yourself (on camera)
- [ ] Verification tab shows each check with expected vs observed
- [ ] One sentence of limitations: simulated systems, fictional data, prototype

**If something goes wrong**
- [ ] MODEL UNAVAILABLE → wait 60 s, new incident; still failing → switch to the backup recording and say so
- [ ] Ends DIAGNOSED instead of VERIFIED → say "it refused to ship an unproven fix", then show the backup run
- [ ] Never switch to the baseline without saying "this is the rule-based baseline, not the AI"
