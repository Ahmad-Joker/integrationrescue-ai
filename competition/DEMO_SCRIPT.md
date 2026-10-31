# Demo script (≈4 minutes) — draft

Setup: `./scripts/dev.ps1 reset`, start backend and frontend, open http://127.0.0.1:5173. State the mode on screen:
**"This run is DETERMINISTIC MODE (rule-based baseline)"** unless a live model is configured — never present it as live AI.

1. **The incident (30 s).** New incident → "Payment succeeded but Pro entitlement was not granted". Read the ticket:
   paid, still "Upgrade to Pro".
2. **Surprise failure (15 s).** Tick *Duplicate webhook delivery*. Create and investigate.
3. **Investigation (60 s).** Investigation tab: each tool call with its rationale; hypotheses H1 (not delivered) refuted —
   delivery acked 202; H2 (crash) refuted; H3 (tenant mapping missing the paid price) supported. Root cause names the
   tenant file. "Failure reproduced in isolation."
4. **Repair review (60 s).** Repair tab: one-line config diff, policy risk *low*, suite PASS, regression test FAILS on
   unpatched code (proving it tests the bug), sandbox replay PASS. Approve.
5. **Proof (45 s).** Verification tab: expected plan derived from the billing ledger, observed *pro*, exactly one charge,
   exactly one grant despite the duplicate webhook. Reproduction table shows the same checks failing before the fix.
6. **Honesty beat (30 s).** New incident with *Billing ledger unavailable* → INDETERMINATE, no patch, no VERIFIED claim.
7. **Close (15 s).** Evaluation lab: recorded numbers, including the misses (schema drift needs a code fix the baseline
   won't attempt — that's where the live model is evaluated next).

Fallback: `./scripts/dev.ps1 demo` runs the same flow in the terminal.
