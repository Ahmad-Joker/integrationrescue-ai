# Security model

## Trust boundaries
| Source | Trust | Handling |
|---|---|---|
| Ticket text, operator notes, uploads | untrusted | passed to the decision maker as data; uploads type/size-limited and redacted |
| Logs, API responses | untrusted | redacted + truncated before reaching the model |
| Customer repo files | untrusted | readable via allow-listed paths only; executed only in child processes |
| Model output (tool calls, patches) | untrusted | schema-validated, phase-gated, policy-reviewed |
| Verifier, policy, orchestrator | trusted | deterministic code, never modifiable by patches |

## Controls (all enforced in code, covered by `tests/adversarial`, `tests/unit/test_policy.py`)
- **Typed tools** with `extra="forbid"` Pydantic models; unknown tools and extra arguments rejected.
- **Phase gating**: `propose_patch` only in patch phase; no tool can mark an incident verified.
- **Read paths**: no absolute paths, traversal, dotfiles, `.env*`, keys, `secrets/`, `.git`.
- **Write paths** (patches): `tenants/*.json`, `sync/*.py` only; tests and conftest denied; ≤5 edits, ≤40 lines;
  forbidden constructs in code edits (`subprocess`, `os`, `socket`, `eval`, `exec`, `__import__`, …); plan values allow-listed.
- **Network**: tools use a GET-only simulator client restricted to approved local origins.
- **Execution**: customer code runs via `python -I` with a stripped environment and timeouts (handler 15 s, tests 90 s).
- **Sandboxing**: patches applied to copies; replay on cloned databases; promotion requires approval.
- **Side effects**: payments idempotent on key; replay redelivers stored events only; receiver dedups by event id;
  verifier asserts exactly one charge and one grant.
- **Verification independence**: read-only SQLite connection; expected state from the ledger; agent output never consulted.
- **Trust changes**: edits to a tenant's `accepted_signing_keys` must be a list of key ids (`whsec_…`) and are marked
  medium risk with an explicit "confirm with the billing provider" note for the approver. The orchestrator rejects any
  newly trusted key id that billing's own logs never announced for that tenant (forged events can carry any key id).
  This is enforced in code because live Gemini, despite the prompt, trusted the event's key without checking.
- **No-action claims**: `report_no_action_needed` is accepted only if the independent verifier passes on the live
  environment; a contradicted claim returns to investigation once, then escalates.
- **Budgets**: 40 tool calls per incident, 3 patch attempts, model call cap (`IR_MAX_LLM_CALLS`).
- **Secrets**: redaction of key/token patterns in tool output and uploads; `.env` git-ignored.

## Known gaps
- Child processes are not OS-sandboxed (no container/job-object isolation; Docker unavailable). Acceptable for fictional
  local code; required before running real customer code.
- Regex-based forbidden-code checks are a speed bump, not a guarantee; the test suite + replay verification are the real gate.
- No authentication on the local API (binds to 127.0.0.1). Required before any deployment.
- Prompt-injection resistance of the live model: Gemini (flash-lite) handled the injected-ticket variant (2/2 VERIFIED,
  no policy violations) in live run 2; a small sample, not a guarantee.
