# Cloudflare platform architecture — verified mental model

This guide translates the edge platform into actionable architecture tradeoffs. Use principal-systems-internals.md for the limits of implementation claims, decision-framework.md for service selection, security-baseline.md for threats and data-integrity.md for correctness.

## Global request processing

A request traverses internet routing, Cloudflare's network and configured security/cache/Worker/origin paths. Actual execution phases depend on zone configuration, route, product entitlement and individual request; not all products run in a universal chain.

- DNS maps name to IP; proxied DNS differs from DNS-only.
- Anycast helps route connections to Cloudflare's network; it does not guarantee nearest physical colo.
- Edge TLS terminates the client connection; origins may still need TLS validation and network protection.
- Workers execute application code in isolates; do not rely on process lifetime or identical execution location.
- Cache can reduce latency and origin traffic for **safely cacheable** resources; private responses require deliberate exclusions.
- Internal resources accessed through bindings can involve storage networks and service-specific availability/consistency.

## Request data path checklist

1. Draw client, zone, Worker, cache, origin, storage, external provider and IdP as separate nodes.
2. Annotate each trust boundary with identity and key management.
3. Identify which hops carry PII, credentials, customer content and log metadata.
4. Specify sync vs async operations, timeout, retry, idempotency and end-to-end SLA.
5. Decide how to handle origin failures, regional latency, partial writes and replay.
6. Instrument each hop without exposing secrets.

## Runtime choices

Workers: stateless edge API/SSR/transform. Durable Objects: coordination by object identity. D1: SQL. R2: object data. KV: read-heavy eventually consistent lookup. Hyperdrive: access to existing database. Queues: async messages with at-least-once semantics. Workflows: multi-step durable state. Containers: when application truly needs container execution rather than isolate APIs. Check product catalog for finer comparisons.

## Network and private access

Tunnel creates outbound connectivity from origin to Cloudflare and does not itself establish user authorization. Access evaluates identities and policies for protected applications. WARP and Gateway shape client/private network flows. Spectrum handles certain non-HTTP proxy patterns; verify actual plan/protocol capability.

Origin security requires explicit design: TLS Full (strict) where suitable, restricted network path, meaningful app authorization and optionally AOP (not for Tunnel origins). Do not interpret Cloudflare edge protection as automatic protection for bypassed origin addresses.

## Failure and operations

- Static cache cannot repair a broken origin for uncacheable requests.
- DO coordination can be constrained by hot keys; data architecture must allow retries/reconnects.
- KV cached stale values are expected under eventual consistency; avoid authorization revocation decisions based on them.
- Queues/Workflows must handle duplicates and checkpoint changes.
- IaC and deployment changes may alter live traffic; record blast radius and rollback.
- Observe actual p95/p99 and error budget; architecture claims alone do not show correctness.

Current docs: https://developers.cloudflare.com/ ; https://developers.cloudflare.com/workers/ ; https://developers.cloudflare.com/cloudflare-one/ ; https://developers.cloudflare.com/workers/platform/.
