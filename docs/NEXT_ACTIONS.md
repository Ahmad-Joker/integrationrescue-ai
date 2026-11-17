# Next actions (ordered, updated 2026-11-18)

Founder-only actions (accounts, recordings, interviews, submission) are tracked in
[competition/USER_ACTIONS.md](../competition/USER_ACTIONS.md).

| # | Task | Importance | Files | Depends on | Done when | Status |
|---|---|---|---|---|---|---|
| 1 | Push the 2026-11-18 changes; confirm all three CI jobs are green | P0 | .github/workflows/ci.yml | founder OK to push | run green on GitHub | done (`7b04941`, run 44201180724, all 3 jobs green) |
| 2 | Deploy the container and verify the public URL (deterministic + live) | P0 | Dockerfile, render.yaml, scripts/verify_deployment.py | hosting account (founder) | two 15/15 runs against the URL recorded in JUDGE_ACCESS | ready, blocked on account |
| 3 | Record the 2-minute live demo and the 6-minute pitch | P0 | competition/DEMO_*, PITCH_* | #2 or local demo | videos uploaded unlisted | founder |
| 4 | Customer discovery: 8–10 interviews, fill VALIDATION_EVIDENCE | P0 (business) | competition/PROBLEM_VALIDATION_PLAN.md | founder | evidence file filled with real notes | todo |
| 5 | Run the coding-agent comparison (10 cases) | P1 | integrationrescue/comparison.py, competition/COMPARISON_PROTOCOL.md | a coding-agent account; independent operator ideally | `evidence/comparison/RESULTS.md` filled | harness done, runs todo |
| 6 | More live runs: schema_drift (code repair) and a stronger model | P1 | evaluation.py | quota / billing decision | code-repair rate on ≥6 scored runs | partial |
| 7 | Incident families: CRM field mapping (needs CRM simulator), duplicate side effect | P1 | scenarios/, simulators/ | — | setup, defect, held-out variant, tests, eval rows | 5 of 8 |
| 8 | Per-run OS isolation for customer code (gVisor/Firecracker/container per run) | P1 | security/child.py, agent/sandbox.py | hosting that allows it | filesystem + network isolation tested | rlimits done; isolation todo |
| 9 | Screenshot analysis via a vision model, cross-checked with API state | P3 | agent/, api.py | #6 | text-only vs multimodal comparison recorded | todo |
| 10 | Playwright "customer app" page + browser tool restricted to the local origin | P3 | simulators/, agent/tools.py | — | agent reproduces the "Upgrade to Pro" banner | todo |
| 11 | Confirm the official rules: exact deadline day, video lengths, required documents | P0 (business) | competition/SUBMISSION_READINESS.md | founder (portal access) | portal text cited | public page read 2026-11-18: "January 2027", no day |
