# Competitive positioning

Sources and method: [docs/COMPETITOR_RESEARCH.md](../docs/COMPETITOR_RESEARCH.md) (web research 2026-10-31; vendor
claims are self-reported and unverified). **No superiority claim is made until the comparison in
[COMPARISON_PROTOCOL.md](COMPARISON_PROTOCOL.md) has results.**

## Landscape
| Category | Examples | What they do well | Where they stop (for this problem) |
|---|---|---|---|
| AI SRE / incident investigation | Datadog Bits AI SRE, Cleric, Resolve.ai, Traversal | investigate alerts across observability data | start from an alert; silent business-state failures produce none; focus on infrastructure |
| Error-to-fix | Sentry Seer | root cause from stack traces, proposes code fixes and PRs | needs an exception; a 202 with the wrong entitlement throws nothing |
| General coding agents | Claude Code, Copilot agent, Devin, Cursor | edit code, run tests, open PRs | judge success by tests passing, not by the cross-system business outcome; given the right context they may produce the same patch |
| Integration platforms | Workato, Zapier, Askel | build and run integrations, show run logs | the integration "ran"; whether the customer got access is outside their view |
| API / synthetic monitoring | Postman monitors, Checkly | detect failing endpoints | the endpoint returned 202 |

## Position
**IntegrationRescue closes the loop on the business outcome:** starting from a customer-visible symptom, it
investigates across billing, webhooks, code and entitlements. It ships only a sandbox-tested, human-approved repair,
and calls it fixed only when an independent, ledger-derived check passes. It also says "nothing to fix" or "cannot
tell" when that is the truth.

## Defensibility (honest version)
| Asset | Strength today | How it compounds |
|---|---|---|
| Independent verifier + policy layer | real and tested, but replicable by a determined team | becomes a trust and compliance asset with audit history and certifications |
| Incident-family library with hidden ground truth | 5 families; small | every pilot incident becomes a family, with held-out variants; few others have labelled integration-failure data |
| Evaluation harness reporting verified outcomes | real | lets us publish comparable reliability numbers; a sales asset |
| Connectors | none real yet | per-platform depth (edge cases, API versions) is slow to copy |
| Model choice | none: model-agnostic by design | we benefit when models improve; we are not tied to one vendor |

Risks: a coding-agent vendor or billing platform adds "verify the business outcome" as a feature. Our response is
depth in incident data, connectors and verified-outcome reporting, and partnering with billing platforms rather
than competing with them.
