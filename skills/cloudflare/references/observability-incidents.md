# Observability, SRE and incident response

Agent must design observability before production cutover, not after an outage.

## 1. Service objectives

- Define user-facing SLIs (availability, correct responses, p95/p99 latency, error ratio, freshness, job lag).
- Specify an SLO and error budget per critical user journey; not every Cloudflare metric is a business SLI.
- Track RED (rate, errors, duration) for synchronous services and USE (utilization, saturation, errors) for bottlenecks; event lag, retries, drop, dead-letter count for async.
- Establish baseline by environment and compare to change windows. Do not infer cause from a single graph.

## 2. Telemetry design

- Use Workers Observability logs/traces, analytics, Logpush, GraphQL analytics, security events or external APM as justified. Availability and sampling depend on product/plan.
- Emit structured logs with environment, version, component, request ID, sanitized tenant identifier, outcome, latency and error type.
- Correlate edge request IDs with origin and downstream traces. Validate propagation across Worker-to-Worker and queued boundaries.
- Set head sampling based on traffic, cost, security and incident needs; ensure critical errors have sufficient signal.
- Prefer metrics for alerting and traces for investigation; logs for discrete events and audit evidence.
- Redact tokens, IP/PII where not necessary, raw bodies, cookies, Authorization and model prompts. Document retention and access.
- Instrument errors at boundaries: client, Cloudflare WAF/Access, Worker, origin, D1, R2, DO, third-party and external DNS.

## 3. Health checks

- Distinguish Worker readiness, edge response, origin, auth flows, queue consumption and database operations.
- Do not make a public health endpoint expose credentials or DB details.
- External synthetic checks should exercise TLS/hostnames, Access if appropriate, critical read/write flow and multiple regions.
- Check account/rate limits and alarms; a successful deploy response is not sufficient verification.

## 4. Incident playbook

1. **Triage**: define severity, onset time, impacted hostnames, customers, environment, deploys and security indicators.
2. **Contain**: if active abuse, narrow block/rate limit or revoke compromised tokens, avoiding blanket outages unless necessary.
3. **Measure**: compare error types (4xx challenge, 5xx, 52x origin/TLS, DNS, timeouts, script exceptions), colo, routes, plans.
4. **Isolate**: correlate Cloudflare events, edge logs, origin metrics and recent changes. Differentiate WAF block from application 403.
5. **Mitigate**: rollback version/route/rule, fail over backend, throttle, disable new feature or restore data as appropriate.
6. **Validate**: test customer journey and independent readback; track improvement over baseline.
7. **Recover**: reconcile IaC, renew credentials, restore monitoring; confirm no hidden backlog or stale data.
8. **Postmortem**: causal timeline, contributing factors, five whys or equivalent, action owner and preventive test.

## 5. Failure mode matrix

| Symptom | Hypotheses | Checks |
| --- | --- | --- |
| 522/524 | Origin connectivity/timeout | Origin logs, firewall, connection count, TLS, load |
| 525/526 | TLS handshake/certificate | Full (strict), chain, SNI, expiry, AOP |
| 403 spike | WAF/Access/authz | Security events, policy/rules, token validity |
| CPU exception | Hot loop, transformation | Worker CPU profile, deploy diff |
| D1 stale read | Replica consistency | Session/bookmark path, read source |
| KV old value | Eventual consistency | Cache TTL, negative lookups, write time |
| Queue growth | Consumer failures/throughput | DLQ, retries, batch sizes |
| Tunnel 502 | Connector/origin unavailable | cloudflared health, ingress target, origin TLS |
| Cost surge | Load, attack, retries, logs | Request distribution, per-service usage and limits |

Official: https://developers.cloudflare.com/workers/observability/ ; https://developers.cloudflare.com/cloudflare-one/insights/ ; https://developers.cloudflare.com/waf/analytics/.
