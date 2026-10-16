# Quality gates and review rubric

Apply these checks whenever delivering Cloudflare changes. Link findings to specific files and evidence.

## Correctness

- The chosen solution follows documented platform behavior, not inferred low-level implementation specifics.
- CLI flags and API payloads match installed version and live schemas.
- Target account, zone and environment confirmed.
- Data consistency, idempotency, event order and failure behavior documented.
- Application/test framework and compatibility date supported.
- Security contracts and entitlements validated.

## Security

- Identity and authz boundaries tested, including cross-tenant negative cases.
- No credentials in repo, logs, browser payloads, app vars or chat transcript.
- Least-privilege API tokens, Access policies, WAF rules and bounded Tunnel ingress.
- TLS Full (strict) as appropriate; origin bypass addressed.
- Request parsing, SSRF, CSRF, caching, signed webhooks, replay and abuse limits tested.
- Dependency risk and CI credentials reviewed.
- Logs and metrics redacted; retention clear.

## Reliability and observability

- Staging, rollback, data recovery and migrations tested.
- Availability/latency/error objectives instrumented.
- Request IDs, traces, async dead-letter paths and on-call alert routing present.
- Failures cause clear user-safe responses and actionable internal diagnostics.
- Cost and relevant quotas bounded, no unbounded retries.

## Audit format

For each finding report:
- Severity: critical / high / medium / low / informational.
- Evidence: exact file line or live command and observed outcome.
- Impact: potential exploit, outage, cost, consistency or maintenance failure.
- Fix: precise change with owner and scope.
- Test: automated or manual verification and result.
- Confidence: confirmed, likely or requires live environment.

Priority is risk = probability x impact, adjusted for detectability and blast radius, not how dramatic a claim sounds.

## Required workflow order

1. Static lint/type/secret and source verification.
2. Architecture/security/operational review.
3. Negative-path unit and integration tests.
4. Preview/staging deployment (when applicable).
5. Approved production rollout.
6. Independent verification and monitoring.
7. Post-deploy reconciliation and documented outcome.
