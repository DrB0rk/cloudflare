# Cloudflare agent skill — engineering audit

Date: 2026-10-16. Scope: main agent entrypoint, product index, representative architecture/Workers/security content, tool helpers, existing test suite, documentation claims and release workflow. **Not** an exhaustive line-by-line verification of all product reference files.

## Summary

The repository began with ~350 files and 63 product-reference folders. It covered many services but too frequently described implementation details, performance measurements and CLI/tool preferences as universal guarantees. The revision preserves the broad catalog and adds an evidence-based senior engineering workflow with a cross-cutting security baseline.

## Findings and changes

| Severity | Finding | Resolution |
| --- | --- | --- |
| Critical | "Zero-overhead"/in-process bindings and fixed request pipeline asserted as public guarantees | Rewrote principal systems internals and architecture deep dive to distinguish API contracts, internal descriptions and measurements |
| High | Compatibility dates forced within 30 days; Node.js compatibility flag advice stale | Corrected SKILL, docs retrieval and Workers rules/review; no automatic production date bumps; default Node compatibility documented for >=2026-08-04 |
| High | Strict cf-first policy could create migration errors or IaC drift | Added context-aware cf/Wrangler/IaC/connector/cloudflared selection, preserving active project source of truth |
| High | Security practices incomplete as a unified operational standard | Added security baseline, Workers application security, Access/Tunnel/Gateway, DNS/TLS/WAF and agent safety policies |
| High | Services presented without decision constraints | Added ADR/service-selection framework and concrete production recipes |
| High | Async/data correctness risks underexplained | Added data integrity, idempotency, replication and recovery guide |
| Medium | No end-to-end production/SRE and governance framework | Added production delivery, incident/SLO, FinOps and privacy/compliance guides |
| Medium | Reference discoverability and stale links hard to detect | Added product service index, structural lint and regression workflow |
| Medium | Auto-push sample CI deployed on main without deliberate production gate | Changed cf sample to manual workflow_dispatch and protected production environment requirement |

## Operational acceptance criteria

Before a Cloudflare agent describes a deployment as successful:
1. Confirm account/zone/project/environment and intended user permission.
2. Discover correct syntax, type contracts and current product docs.
3. Check IaC ownership, identities and secrets, blast radius, backups and rollback.
4. Test normal and negative paths, including security controls.
5. Apply only authorized change and independently verify remote state/end-user response.
6. Record outcomes, costs, residual risk and limitations.

## Remaining work

- Product-level API examples under individual service folders must be checked against installed SDK versions and current Cloudflare product docs during task execution. 63 folders exist; the present pass did **not** certify every API example.
- Integration tests of live cf, Wrangler, Workers, Access, WAF or database mutations were not run. The new structural checks and offline fixtures are not substitutes for staging validation.
- Example CI uses moving major-action tags; for security-sensitive repositories pin each external GitHub Action to a reviewed immutable commit SHA and enforce CODEOWNERS/branch protection.
- Confirm Cloudflare plan entitlements, legal compliance, limits, billing and product contracts before production decisions.
- Assess and version-bump the distributed cf CLI helpers when beta command formats change.

## Primary references

- https://developers.cloudflare.com/cf/
- https://developers.cloudflare.com/cf/agents/
- https://developers.cloudflare.com/workers/configuration/compatibility-dates/
- https://developers.cloudflare.com/workers/configuration/compatibility-flags/
- https://developers.cloudflare.com/fundamentals/api/get-started/
- https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/
- https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
