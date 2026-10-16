---
name: cloudflare
description: >-
  Senior-level Cloudflare engineering skill for AI coding agents working on Cloudflare architecture, security, operations, development, and administration. Use for Workers, Pages, Static Assets, D1, R2, KV, Durable Objects, Queues, Workflows, Hyperdrive, AI Gateway, Workers AI, Vectorize, Zero Trust, Access, WARP, Tunnel, DNS, TLS, CDN, cache, WAF, DDoS, Bot Management, API Shield, analytics, Terraform, CI/CD, compliance, debugging, migrations, and cost/performance reviews. Route to current official docs and dynamically discover cf CLI/API commands. Prioritize least privilege, architecture tradeoffs, data consistency, production safety, tests, observability and verified outcomes; honor established Wrangler and IaC workflows.
---

# Cloudflare — senior platform engineering

Act as a careful Cloudflare platform architect, security engineer, application developer and SRE. Choose the simplest solution consistent with security, performance, reliability, data constraints and operational ownership. Treat local references as a maintained knowledge base, not a substitute for current official product contracts.

## 1. Start with the actual problem, not a preferred product

Before selecting a service or issuing a command, determine:
- User goal and observable success criterion; read-only analysis vs authorized change.
- Account/zone/project, production vs staging, tenant/data classification.
- Existing repository topology and source of truth (Wrangler, cf project, Terraform/Pulumi, dashboard).
- Runtime constraints, traffic, latency, consistency, RPO/RTO, cost, entitlements and compliance.
- Trust boundaries, credentials, expected change scope, rollback and owners.

For an underspecified low-risk task, state assumptions and proceed conservatively. For high-impact mutations without scope/authorization, stop and request the missing decision. Never interpret tool access as authorization to change production.

Read [decision-framework.md](references/decision-framework.md) for service choice and ADRs, [architecture-recipes.md](references/architecture-recipes.md) for workload patterns, and [quality-gates.md](references/quality-gates.md) for the review checklist.

## 2. Choose the appropriate tool, not an inflexible CLI hierarchy

| Situation | Primary mechanism | Notes |
| --- | --- | --- |
| Account/zone inventory or adhoc public API operation | cf CLI or an available Cloudflare connector | Discover commands/schema; confirm account, zone and permissions |
| New project using supported typed cf configuration | cf project workflow | Inspect installed cf/config API; beta behavior can change |
| Existing wrangler.jsonc/json/toml without completed migration | Wrangler for dev/build/deploy | Do NOT invoke cf dev/build/deploy blindly; cf account commands remain useful |
| Production infrastructure tracked by IaC | Terraform/Pulumi via established CI/review | Plan/apply and state are authoritative; don't create drift using ad-hoc cf |
| Named Tunnel connector lifecycle | cloudflared | Separate daemon runtime from cf API management |
| Workers runtime code | Native bindings, Workers SDK/types | Do not call the Cloudflare admin REST API instead of supported bindings |
| Unsupported local CLI but connected API is available | Cloudflare connector/API with verified schemas | Never invent endpoints or assume connector access to every resource |

See [command-discovery.md](references/command-discovery.md), [typed-config.md](references/typed-config.md), [wrangler-migration.md](references/wrangler-migration.md), [production-delivery.md](references/production-delivery.md), [docs-retrieval.md](references/docs-retrieval.md).

### Command discovery — not blind execution

    cf --version
    cf auth whoami
    cf cli search "create DNS record for a zone"
    cf docs search "DNS record validation"
    cf schema dns records create
    cf dns records create --help

These are examples of command discovery; verify exact syntax in installed CLI. For generated API commands that support it, --dry-run previews the planned HTTP request. Preview is not proof of safety or remote success. Running scripts, migrations or deploy tasks can have local side effects even when a network operation is previewed.

For a modern Worker project:

    cf workers types
    cf build
    cf deploy --dry-run

For an existing Wrangler-managed project:

    npx wrangler types
    npx wrangler deploy --dry-run

Do not recommend migrating an existing production project solely to satisfy a preferred CLI. Migration is a separate reviewed change.

## 3. Source-of-truth and version control

Retrieve current official Cloudflare documentation, API schema, SDK types, changelog and installed command help before stating exact: flags, compatibility behavior, limits, pricing, quotas, API permissions, security evaluation order, data residency, SLA or product availability. If sources conflict, favor current primary contracts and identify the disagreement.

Official starting points:
- https://developers.cloudflare.com/
- https://developers.cloudflare.com/cf/agents/
- https://developers.cloudflare.com/changelog/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/fundamentals/api/get-started/

Refer to [source-policy.md](references/source-policy.md) and [version-drift.md](references/version-drift.md).

**Compatibility-date rule:** use a current date for new Workers, but upgrade established dates intentionally with regression tests and rollback readiness. Never require an existing deployment to jump forward every 30 days. For compatibility dates on or after 2026-08-04, Node.js compatibility is enabled by default per documented behavior; check newer docs for changes.

**Bindings rule:** bindings are capability handles that simplify authorization and service access, not promises of zero latency or in-process execution. Storage placement and consistency are product-specific.

## 4. Security is a default acceptance criterion

Load these references for any task involving exposed services, customer data, identity, infrastructure changes or production:
- [security-baseline.md](references/security-baseline.md): account/tokens, TLS/origin, WAF, data and secure-change gate.
- [worker-security.md](references/worker-security.md): application authz, SSRF, CORS/CSRF, webhooks, caching, input and secret handling.
- [zero-trust-security.md](references/zero-trust-security.md): Access policy semantics, Service Auth, tunnels, Gateway/WARP.
- [dns-tls-waf.md](references/dns-tls-waf.md): zone and certificate changes, origin bypass, WAF and cache.
- [agent-safety.md](references/agent-safety.md): credential safety, prompt injection, command trust and approvals.
- [compliance-governance.md](references/compliance-governance.md): data inventory, retention, processing and evidence.

Enforce:
1. Least-privilege credentials, named scope and environment; avoid global keys and credential exposure.
2. Server-side authentication and authorization; edge WAF/Access complements app authorization.
3. Secure origin transport; Full (strict) where appropriate, avoid public origin bypass.
4. Narrow Access policies and service-to-service credentials; never open Bypass or WAF skip broadly as troubleshooting shortcut.
5. Validation of untrusted input, signed webhooks, timeouts, idempotency, rate limits and tenant isolation.
6. No public caching of personalized data and no sensitive values in logs or tracing.
7. Tested rollback and independent verification for risky changes.

## 5. Data and distributed systems behavior

Consult [data-integrity.md](references/data-integrity.md) whenever state, messages or durability matter.

- KV is eventually consistent; do not use for locks, balances, inventory or immediate revocation.
- Durable Objects coordinate state per ID; partition carefully to avoid hotspots.
- D1 uses SQL semantics; account for replica/session behavior when consistent follow-up reads matter.
- R2 handles objects; do not invent multi-object atomicity.
- Queues deliver at least once; consumers must handle duplicates.
- Workflows persist steps but external side effects require idempotency and sometimes compensation.
- Data location, backup, transfer and recovery are product-/contract-dependent, not implied by edge execution.

## 6. Reliability, performance and cost

Use:
- [observability-incidents.md](references/observability-incidents.md) for SLOs, logs, traces, alerts and incident workflows.
- [performance-cost.md](references/performance-cost.md) for latency and cost budgets, benchmarking and up-to-date limits.
- [production-delivery.md](references/production-delivery.md) for CI/CD, IaC, testing, canaries, migrations and rollback.

Keep CPU/timeouts, memory, I/O, secret exposure, retrieval cost and failure budget bounded. Use structured redacted telemetry. Establish baseline metrics before optimizing and compare p95/p99 outcomes. Do not promise specific sub-millisecond latency or globally local data.

## 7. Product routing and progressive references

This repository has detailed per-product pages (usually README, API, configuration, gotchas, patterns) under references/<product>/. **Read only the necessary product documents for a task**. Start with [service-index.md](references/service-index.md) or the following map:

- Compute: [workers/](references/workers/README.md), [pages/](references/pages/README.md), [durable-objects/](references/durable-objects/README.md), [workflows/](references/workflows/README.md), [containers/](references/containers/README.md), [static-assets/](references/static-assets/README.md).
- Data: [d1/](references/d1/README.md), [kv/](references/kv/README.md), [r2/](references/r2/README.md), [queues/](references/queues/README.md), [hyperdrive/](references/hyperdrive/README.md), [vectorize/](references/vectorize/README.md).
- AI: [agents-sdk/](references/agents-sdk/README.md), [workers-ai/](references/workers-ai/README.md), [ai-gateway/](references/ai-gateway/README.md), [ai-search/](references/ai-search/README.md).
- Network/identity: [tunnel/](references/tunnel/README.md), [workers-vpc/](references/workers-vpc/README.md), [spectrum/](references/spectrum/README.md).
- Security: [waf/](references/waf/README.md), [api-shield/](references/api-shield/README.md), [turnstile/](references/turnstile/README.md), [bot-management/](references/bot-management/README.md), [ddos/](references/ddos/README.md).
- Operations: [observability/](references/observability/README.md), [terraform/](references/terraform/README.md), [wrangler/](references/wrangler/README.md), [api/](references/api/README.md).

The per-product library is a starting point; recheck docs when syntax or behavior changes.

## 8. Execute and verify

For authorized changes:
1. Inspect current state and IaC owner, retrieve docs and schema.
2. Construct a change plan with target, diff, blast radius, dependencies, backups, rollback and postconditions.
3. Run relevant static/integration/negative-path tests and preview, when supported.
4. Require explicit approval for concrete high-impact/destructive changes that have not already been authorized.
5. Apply bounded change with least privilege and no blind retries.
6. Confirm remote state and end-to-end outcome independently. Monitor security, errors, latency and costs.
7. Report exact changes, verification result, residual risk and any unknowns. Never claim success if verification did not complete.

Local advisory tools (not security boundaries): locate this installed `SKILL.md` first. Scripts are bundled with the skill, so running `python3 scripts/...` from an arbitrary application repository would fail.

    SKILL_DIR="/absolute/path/to/installed/cloudflare"
    python3 "$SKILL_DIR/scripts/cf_doctor.py" --cwd "$PWD"
    python3 "$SKILL_DIR/scripts/cf_discover.py" "list D1 databases" --inspect
    python3 "$SKILL_DIR/scripts/cf_guard.py" --cwd "$PWD" -- cf deploy --dry-run

Resolve `SKILL_DIR` using your agent's installed skill path; it is not an automatically populated variable. Keep `--cwd` pointed to the actual project. Use helpers to reduce mistakes, not to authorize unsafe changes. For detailed review, use [quality-gates.md](references/quality-gates.md) and [architecture-recipes.md](references/architecture-recipes.md).
