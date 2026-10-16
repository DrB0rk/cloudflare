# Cloudflare systems internals — engineering model and epistemic boundaries

This document describes the **publicly useful execution model** for architecture reviews. It intentionally avoids fictional implementation guarantees. Blog posts, benchmark snapshots and internal code can explain mechanisms, but are not stable platform contracts.

## 1. Edge ingress and request path

Illustrative flow:

    Internet client
      -> DNS and Anycast routing to Cloudflare network
      -> TLS/HTTP and product-dependent security/rules evaluation
      -> cache / Worker routing / origin fetch (ordering depends on route configuration)
      -> Worker logic, bindings, subrequests or origin
      -> streaming response and optional background activity

Do not assume that every request always passes WAF, Magic Transit, Turnstile, Worker and Cache in one fixed sequence. Product enablement, plans, route configuration, ruleset phases, requests and cache settings matter. BGP picks a network route, not necessarily the geographically nearest colo. Cloudflare may internally steer traffic.

## 2. Workers V8 isolate model

- The Workers runtime is based on workerd and V8; isolates allow multi-tenant execution with fast startup compared to conventional processes.
- Isolates are security boundaries built atop Cloudflare's runtime policies, not a substitute for app authentication, authorization or tenant isolation.
- The live Worker environment can be reused, migrated or evicted. Global variables are not durable state; use appropriate products for persistence and coordination.
- CPU, memory, startup limits, supported APIs, outgoing connections and duration depend on current product contracts and plan. Retrieve https://developers.cloudflare.com/workers/platform/limits/ before sizing.
- Small benchmark cold-start times and memory sizes are **illustrative measurements**, not globally enforceable upper bounds.
- Use Web Streams for large bodies. Memory usage includes more than JS heap and performance depends on payload and code paths.

## 3. Bindings and capabilities

Bindings expose services as typed capability handles (KVNamespace, D1Database, R2Bucket, DurableObjectNamespace and others). They simplify identity and avoid embedding Cloudflare administrator API credentials in application code.

**Do not claim** every binding is zero-copy, in-process or zero network latency. A binding call may depend on a service with remote storage, RPC or a routing layer; the consistency and failure model belongs to that service. Auth and tenant authorization in business logic are still necessary. Avoid storing secret tokens in config vars.

## 4. Storage and coordination

- KV: centralized write path plus multi-tier caches; eventually consistent reads including negative lookups. Strong read-after-write guarantees are **not** implied.
- D1: SQLite semantics for supported queries and transactions. Replication, sessions and read freshness require explicit handling; consult product documentation.
- Durable Objects: per-object identity and private storage; useful for serialized coordination. Object location and lifecycle can change and a hot object can limit throughput.
- R2: object-store access; no guarantee of cross-object transaction.
- Queues: at-least-once delivery, duplicates possible.
- Workflows: durable steps/checkpoints; external side effects need idempotency.

See data-integrity.md for application implications.

## 5. Smart Placement and backend locality

Smart Placement may help Worker handlers that incur repeated remote backend latency; may hurt workloads where client proximity matters most. Benchmark representative requests before and after. Product runtime can schedule work intelligently; do not promise exact colo placement or percentage improvement.

## 6. Background tasks and liveness

- await work needed for response correctness.
- ctx.waitUntil can extend work beyond response with platform-specific limitations; it does not create a durable queue or guarantee eventual completion through outages.
- Use Queues and Workflows when execution must survive retried or interrupted handlers.
- Error handling and idempotency must cover partial completion and duplicate events.

## 7. Security architecture, without invented implementation details

- Edge security controls include TLS, WAF, bot products, network DDoS protections, Access and API Shield. They differ by phase, plan, policy and traffic type.
- JA3/JA4 fingerprinting and bot scores are **signals** subject to false positives, not a cryptographic human proof.
- Turnstile needs server-side Siteverify; client-side challenges alone are bypassable.
- Origin protection requires more than proxied DNS: use appropriate origin network restrictions, TLS Full (strict) and, where relevant, Authenticated Origin Pulls.
- Do not claim Wirefilter is always compiled to eBPF, every request uses particular congestion control, or microarchitectural mitigations have an undocumented formal guarantee.

## 8. Distinguish evidence types

**Guaranteed contract**: official docs/API reference current as of inspection, specific to plan/date.

**Documented implementation**: official source/changelog/blog; may change without being a service guarantee.

**Measured behavior**: benchmark in specified workload/location/traffic.

**Hypothesis**: unverified or inferred; do not state as settled fact.

References: https://github.com/cloudflare/workerd ; https://developers.cloudflare.com/workers/ ; https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/kv/concepts/how-kv-works/.
