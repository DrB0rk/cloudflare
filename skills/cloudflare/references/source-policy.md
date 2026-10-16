# Source policy and truth maintenance

## Evidence levels

A. Official Cloudflare API spec, current product docs and local installed CLI/runtime output for exact behavior.
B. Current first-party changelog, official SDK/types/source for implementation details.
C. Curated skill reference documents, marked with retrieval date.
D. Third-party tutorials or inference, explicitly labeled and validated.

Prefer A/B to resolve conflicts. A precise value without a current authoritative source is unknown, not a license to guess.

For undocumented runtime internals, never infer guarantee from implementation blog, a historical benchmark or a source code snapshot. Prefer public supported behavior. Distinguish supported product contract from context-specific measurement.

## Verification triggers

Always recheck docs/CLI for:
- Command and flag syntax, beta version changes, SDK types and migration behavior.
- Pricing, limits, entitlements, regions, retention, compliance, SLA and product availability.
- Security policy precedence, default settings and changed security controls.
- Breaking compatibility-date/Node.js semantics.
- Data replication/consistency and backup/recovery statements.

Examples:
- For new Worker choose a current compatibility date. For existing Worker upgrade intentionally and regression-test; no mandatory 30-day change rule.
- Compatibility dates on/after 2026-08-04 enable Node.js compatibility flags by default, according to current docs; don't blindly add redundant flags.
- A Cloudflare service binding eliminates most explicit API-token handling but can still involve remote I/O and latency. Never call it zero-overhead.
- Workloads in globally available Workers do not imply all data is colocated or region-resident.
- Runtime performance and isolated memory footprint vary; do not turn benchmark numbers into SLAs.

## Primary links

- https://developers.cloudflare.com/
- https://developers.cloudflare.com/changelog/
- https://developers.cloudflare.com/cf/
- https://developers.cloudflare.com/cf/agents/
- https://developers.cloudflare.com/workers/best-practices/workers-best-practices/
- https://developers.cloudflare.com/workers/configuration/compatibility-dates/
- https://developers.cloudflare.com/workers/configuration/compatibility-flags/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/fundamentals/api/get-started/
- https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/
- https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
- https://developers.cloudflare.com/kv/concepts/how-kv-works/

Reviewed 2026-10-16; treat as pointers, not permanent claims.
