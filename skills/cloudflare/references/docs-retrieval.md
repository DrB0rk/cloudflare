# Live Cloudflare documentation and schema retrieval

## Authority

Prefer current official documentation, CLI/SDK schemas, Cloudflare OpenAPI, changelog and installed dependency types over curated skill notes. Track inspected version/date and identify unresolved conflicts. Do not invent commands or infer entitlements from existence of a generated API route.

## CLI discovery

    cf --version
    cf cli search "describe exact task"
    cf docs search "relevant feature and limits"
    cf <group> <operation> --help
    cf schema <group> <operation>

Search results are candidates, not permission to run. Exact group and operation differ between releases. cf docs search requires a compatible release (introduced during beta); fall back to https://developers.cloudflare.com/ when missing.

For supported generated API commands:

    cf <group> <operation> [verified options] --dry-run

A preview may disclose sensitive request data or exercise local build logic. Redact it, interpret actual command help, and never send a mutation on the assumption that every command supports --dry-run.

The skill's local scripts/cf_discover.py executes command/docs/schema/help lookups without shell invocation. Scripts and PATH binaries remain untrusted until inspected.

## Typed Worker projects

Use installed cf/config type definitions and official configuration explorer for cloudflare.config.ts; verify generated bindings/types and the actual build output. Existing Wrangler projects should keep Wrangler build/deploy until deliberate migration. For configured Wrangler projects use wrangler types and wrangler documentation.

## Compatibility dates, as of 2026-10-16

- New projects: current compatibility date after validating framework/runtime.
- Existing projects: upgrade periodically when justified, with integration/regression tests; do not automatically bump every 30 days.
- Cloudflare docs state Node.js compatibility is enabled by default for Workers and Pages at compatibility dates >= 2026-08-04. Do not add redundant flags automatically on those dates; inspect flags for older projects.
- Never automatically enable unspecified experimental flags or reset Durable Object migrations.

## Retrieval targets

- Docs: https://developers.cloudflare.com/
- cf agents: https://developers.cloudflare.com/cf/agents/
- cf CLI overview: https://developers.cloudflare.com/cf/
- Compatibility dates: https://developers.cloudflare.com/workers/configuration/compatibility-dates/
- Compatibility flags: https://developers.cloudflare.com/workers/configuration/compatibility-flags/
- Worker limits: https://developers.cloudflare.com/workers/platform/limits/
- Changelog: https://developers.cloudflare.com/changelog/

For security and pricing consult source-policy.md and product-specific official pages.
