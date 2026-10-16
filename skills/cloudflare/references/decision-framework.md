# Cloudflare architecture decision framework

Use this reference before selecting Cloudflare services, planning a new topology, or migrating a production workload. This is a decision procedure, not a sales catalog.

## 1. Establish requirements before selecting products

Record:
- Scope: account, zone, hostname, environment, owned and third-party systems.
- Objective: request flow, user journey, workload type, expected traffic and peak factor.
- Functional boundaries: public HTTP, private TCP, realtime sockets, scheduled work, events, batch jobs.
- Nonfunctional: availability SLO, p95/p99 latency, RPO/RTO, throughput, burst, maximum payload, compliance.
- Data: classification, location/residency, retention, encryption, consistency, recovery, deletion obligations.
- Security: identity model, authentication and authorization boundary, secrets, trust boundaries and threat actors.
- Operations: on-call, cost budget, IaC ownership, portability, migration and rollback.
- Constraints: plan/entitlements, documented product limits, framework and compatibility date.

Unknown inputs must be documented as assumptions; do not present assumptions as fact.

## 2. Service selection and rejection criteria

| Need | Prefer | Avoid when | Hard design questions |
| --- | --- | --- | --- |
| Static site / SPA | Workers Static Assets or Pages, chosen by existing toolchain and current docs | Dynamic SSR treated as static | SPA routing, cache invalidation, preview workflow |
| Stateless API, gateway, transformation | Workers | Need persistent OS processes or unsupported binaries | CPU/memory, egress, retry and timeout strategy |
| Durable sequential actor, live collaboration | Durable Objects | Global shared state required synchronously across many IDs | ID partition, hotspot, failure recovery, region |
| Structured SQL with SQLite model | D1 | Heavy Postgres-specific features, external database contract | Query plan, migrations, read replication/session guarantees |
| Existing Postgres/MySQL | Hyperdrive + existing database | A new database is actually required | Connection model, query caching, placement |
| High read, low write config/cache | Workers KV | Financial transactions, locks, mutable authorization truth | Eventual consistency and negative cache behavior |
| Objects, files, backups | R2 | Strong multi-object transaction needed | Key naming, access policy, signed access, lifecycle |
| Async jobs, buffering | Queues | Exactly-once required without application idempotency | Duplicate deliveries, DLQ, retries, poison messages |
| Durable multi-step jobs | Workflows | High-frequency low-latency RPC | Step idempotency, checkpoints, retry policy |
| Vector search | Vectorize | Structured exact-match query is enough | Embedding governance, data lifecycle, quality |
| Model inference | Workers AI / AI Gateway | Privacy, egress, cost, or model constraint unsuitable | Prompt injection, routing, timeout, metering |
| Customer-deployed code | Workers for Platforms | Standard multi-tenant worker sufficient | Isolation and tenant quotas |
| Untrusted code requiring OS process | Containers/Sandbox only after threat review | Isolates alone assumed to be arbitrary-process sandboxes | Network egress, filesystem, resource budgets |
| Internal app access | Cloudflare Access + Tunnel | Publishing origin openly | Policy scope, IdP, device posture, service identity |
| Existing private services | Tunnel + WARP/private networks | Server-initiated routing assumed | CIDR overlap, DNS, split tunnels |
| Layer 7 protection | WAF, API Shield, Bot, rate limiting | Used instead of application authorization | False positives, staging, bypass policy |
| Reproducible infrastructure | Terraform/Pulumi | Imperative changes as exclusive source of truth | Imports, state locking, review, drift |

Use the existing references/<product>/ documents for product-specific details; check official documents for version-sensitive claims.

## 3. Cross-cutting comparisons

### Consistency
- KV: eventually consistent, including caching of absent keys. Not a lock, transactional store, or authoritative rapidly changing authorization database.
- Durable Objects: single logical actor ID with durable storage; coordinate operations through that object, understand partitioning and availability.
- D1: SQL storage; use documented sessions/bookmarks where read replication can otherwise return stale replicas. Design explicit transactions and test failure behavior.
- R2: object-store semantics; do not assume atomic multi-object transactions.
- Queues: at-least-once. Deduplicate consumers and use idempotency keys for side effects.
- Workflows: durable steps can retry, so steps that trigger external effects must be idempotent.

### Placement / latency
- A Worker executes on Cloudflare infrastructure; do not assume each product's authoritative data is local to the request colo.
- Evaluate latency from client to Worker and from Worker to database, origin, identity provider and third-party APIs.
- Smart Placement is a tradeoff: backend-adjacent execution may speed backend-heavy handlers and slow edge-proximate processing. Benchmark representative traffic.
- For DO: choose IDs that bound hotspots and coordination requirements. A single global actor can become a bottleneck.

### Cost / limits
Model requests, CPU duration, subrequests, storage bytes and operations, egress (service-specific), queues/messages, observability sampling and retention. Use current price pages, region/account plan and real load. Do not infer free tier or product availability from CLI command presence.

## 4. Architecture Decision Record (ADR)

Create a short ADR for any material production choice:

1. Context and constraints (measured, with sources).
2. Alternatives, including doing nothing and a non-Cloudflare solution where appropriate.
3. Chosen design and rationale.
4. Security and privacy model: threats, trust boundaries, data flow.
5. Data consistency and recovery guarantees; expected failure modes.
6. Cost estimate with assumptions and monitoring trigger.
7. Rollout, rollback, owner and decision-review date.

Never claim a service is globally strongly consistent, always local, free, or unlimited unless its current contract confirms that property.

Official entry points: https://developers.cloudflare.com/workers/platform/ ; https://developers.cloudflare.com/workers/platform/storage-options/ ; https://developers.cloudflare.com/changelog/.
