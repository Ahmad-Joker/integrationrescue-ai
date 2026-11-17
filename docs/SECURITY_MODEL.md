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
- **Execution**: customer code runs via `python -I` with an allow-listed environment (no API keys or access codes;
  `security/child.py`) and wall-clock timeouts (handler 15 s, tests 90 s). On POSIX (the container) an exec trampoline
  also applies kernel limits: CPU seconds = the timeout, 2 GiB address space, 64 MiB max file size, 256 open files, no
  core dumps (`security/rlimit_exec.py`; tested in `tests/unit/test_child_limits.py`, which runs on Linux in CI).
  The container runs as an unprivileged user (uid 10001) whose only writable directory is the fictional `/data`.
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
- **Secrets**: redaction of key/token patterns in tool output and uploads; `.env` git-ignored and excluded from the
  Docker context; `IR_SKIP_DOTENV=1` in the container; `/api/health` reports which providers are configured, never keys.
- **Model failures are not decisions**: a quota, network or refusal error is stored as `provider_error`
  (`infrastructure` / `budget` / `model`), shown as MODEL UNAVAILABLE, ends ESCALATED or DIAGNOSED, never VERIFIED
  (`tests/integration/test_provider_failures.py`); the evaluation excludes infrastructure errors from scores.

## Public demo controls (`IR_DEMO_MODE=1`, `security/access.py`, `config.py`)
| Risk on a public URL | Control | Test |
|---|---|---|
| Anyone creates or approves incidents, drains the model quota | shared access code (`x-access-token`, constant-time compare) on every state-changing `/api` and `/sim` request; reads stay open (fictional data) | `test_demo_mode.py::test_state_changes_need_the_access_code` |
| Skipping the human gate | `auto_approve` refused with 403 in demo mode; approval is a separate authenticated request | `test_judge_flow_requires_human_approval` |
| Quota exhaustion | daily cap on live-model incidents (`IR_MAX_LIVE_INCIDENTS_PER_DAY`), per-incident call cap, concurrency cap | `test_live_model_cap_protects_quota` |
| Request floods, large bodies | per-client sliding-window rate limit; bodies over 2.5 MB refused; uploads type- and size-limited | `test_rate_limit_and_body_size` |
| Spoofed client address | `X-Forwarded-For` honoured only with `IR_TRUST_PROXY=1` | code review |
| State reset by visitors | `/api/admin/*` needs a separate admin code; disabled when unset | `test_admin_reset_reseeds_fictional_state` |
| Misconfiguration | app refuses to start without an access code, with short or identical codes, `*` or malformed CORS origins | `test_invalid_configuration_refuses_to_start`, CI container job |
| Path traversal in static serving | resolved path must stay inside the static root | `test_dashboard_is_served_without_path_traversal` |
| Clickjacking, MIME sniffing, referrer leaks | CSP (`frame-ancestors 'none'`, `default-src 'self'`), `X-Frame-Options: DENY`, `nosniff`, `no-referrer` | same |
| CPU-heavy UI actions | evaluation suite cannot be launched from the public UI | `test_judge_flow_requires_human_approval` |

This is competition-grade access control: one shared code, no user accounts, rotated by redeploying. The approver
name is free text (whoever holds the code), so the audit trail records a claimed name, not a verified identity.

## Dependency policy
`pip-audit` (Python) and `npm audit --omit=dev --audit-level=high` (shipped frontend code) must be clean in CI.
Build tooling is audited at `critical`: as of 2026-11-18, picomatch (used by Vite during the build) has a high
ReDoS advisory with no fixed release. It only matches glob patterns from this repository's own config, never user
input, and it is not in the shipped bundle. Revisit when a fix ships.

## Known gaps
- Child processes have resource limits (POSIX) but no filesystem or network isolation: customer code could read what
  the service user can read and open sockets. Acceptable for the bundled fictional repo; real customer code needs a
  per-run sandbox (gVisor, Firecracker, or a locked-down container per run). On Windows (local development) only the
  timeout applies.
- Regex-based forbidden-code checks are a speed bump, not a guarantee; the test suite + replay verification are the real gate.
- Local development mode (no `IR_ACCESS_TOKEN`) has no authentication and binds to 127.0.0.1. The public demo uses one
  shared access code. Neither has per-user identity, which a product would need.
- Prompt-injection resistance of the live model: Gemini (flash-lite) handled the injected-ticket variant (2/2 VERIFIED,
  no policy violations) in live run 2; a small sample, not a guarantee.
