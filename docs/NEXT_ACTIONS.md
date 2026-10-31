# Next actions (ordered)

| # | Task | Importance | Files | Depends on | Done when | Status |
|---|---|---|---|---|---|---|
| 1 | Run live Claude provider on all families; fix adapter issues; record eval | P0 | agent/providers.py, evaluation.py | API key (BLOCKERS #1) | `--provider claude` eval saved; schema_drift repaired & VERIFIED or failure analysed | blocked |
| 2 | Create GitHub repo `integrationrescue-ai`, push, confirm CI green | P1 | .github/workflows/ci.yml | founder approval | CI run inspected and passing | done (public; run 41154637560 green) |
| 3 | Add families 4–7: timeout-after-commit (lost_ack), duplicate side effect in handler, credential expiry, CRM tenant field mapping (needs CRM simulator) | P1 | scenarios/, simulators/ | — | each has setup, defect, held-out variant, tests, eval rows | todo |
| 4 | General coding-agent baseline comparison harness | P1 | evaluation.py | #1 | same verifier scores both; report failures | todo |
| 5 | Screenshot analysis via vision model → structured observations cross-checked with API state | P3 | agent/, api.py | #1 | text-only vs multimodal comparison recorded | todo |
| 6 | Playwright "customer app" page + browser tool restricted to local origin | P3 | simulators/, agent/tools.py | — | agent can reproduce "Upgrade to Pro" banner and verify after fix | todo |
| 7 | OS-level isolation for child processes (Windows job objects or containers when Docker works) | P1 | simulators/sync_service.py, agent/sandbox.py | — | CPU/mem limits enforced, tested | todo |
| 8 | Mark confirmed hypothesis on diagnosis; show it in UI | P2 | agent/providers.py | — | H3 shows "confirmed" | done |
| 9 | Competition materials: pitch deck, scripts, demo video plan, Q&A, business model | P3 | competition/ | — | all listed files exist and match recorded evidence | partial |
| 10 | Confirm official competition rules, deadline, Youth eligibility | P0 (business) | docs/PRODUCT_REQUIREMENTS.md | founder | official source cited | blocked on founder |
