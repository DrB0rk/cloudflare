# Cloudflare resource-operation playbooks

Use these as **patterns**, not blind copy-paste scripts. Discover actual commands and flags (`cf cli search`, `cf schema`, `--help`) and authenticate to a confirmed account first. Examples use non-production placeholder names/IDs. A read is normally safe; a change requires scope review and authorization; delete/bulk/traffic/security operations require extra verification.

## General mutation sequence

1. Inventory target and dependencies via GET/LIST, following **all pages**.
2. Determine desired state and diff it against current state. Prefer idempotent reconcile where the API supports it.
3. Discover and inspect API schema. Use `--body` for JSON documents where indicated.
4. Inspect API method and zone/account/record IDs with `--dry-run`.
5. Execute only approved narrow mutation.
6. Fresh readback verifies the postcondition; document rollback.

## A. DNS records / zone administration

```bash
cf zones list --name example.com
cf dns records list --zone example.com --name api.example.com
cf dns records create --zone ZONE_ID --body '{"type":"A","name":"api","content":"192.0.2.1","proxied":true}' --dry-run
# execute only after approval, with live zone name or explicit ID:
cf dns records create --zone example.com --body '{"type":"A","name":"api","content":"192.0.2.1","proxied":true}'
cf dns records list --zone example.com --name api.example.com
```

DNS record deletion: get the **exact record ID** first, confirm TTL/proxy/record type, inspect `cf dns records delete --help`, dry-run, then delete. `--force` can skip prompt and requires explicit authorization. Confirm the intended record is gone and unrelated records unchanged. For mail records, distinguish MX/SPF/DKIM/DMARC impact. For websites, verify origins and routing after changes.

## B. D1 databases / SQL changes

```bash
cf cli search "list D1 databases"
cf d1 list
cf cli search "query a D1 database"
cf d1 query DATABASE_ID --sql 'SELECT 1'
# Local simulation uses a different command:
cf d1 raw DATABASE_ID --sql 'SELECT 1' --local
cf d1 migrations list --local
cf d1 migrations apply --local
```

Do not substitute database **name** where the API needs database **ID**. Distinguish local state from remote production. Back up/export before schema migrations; understand transaction behavior, migration history, `--local` persistence and downtime risk. Never run `DROP`, bulk `DELETE`, or migration apply on production without an explicit plan and approval.

## C. KV namespaces and keys

```bash
cf cli search "list KV namespaces"
cf kv namespaces list
cf cli search "put a KV key"
cf kv keys put --help
cf kv keys get --help
```

Read scope and value/metadata format from schema. KV is eventually consistent and namespace IDs matter. Supported `--local` key operations exist, but are not the same state as an active Vite dev server unless explicitly bridged. Bulk operations can affect many keys; inventory selection, rate limits, and rollback.

## D. R2 buckets and objects

```bash
cf r2 buckets list
cf r2 objects list --bucket-name example-bucket --local
cf r2 objects get --help
cf r2 objects put --help
```

R2 object downloads may produce raw bytes, so redirect output; do not parse as JSON. Before overwriting/deleting, check bucket, key, version/ETag and retention, and test with a non-production object. Distinguish API bucket management from S3-compatible data-plane clients. Bulk-delete must be explicitly authorized and confirmed.

## E. Workers, routes and domain

Use `references/workers-lifecycle.md`. Always validate `worker.name`, `accountId`, route, hostname, triggers, version, bindings and deployment mode. `cf deploy` may provision missing resources unless `--no-provision` is supplied. For split traffic, inspect and calculate allocations; verify versions/deployments and monitor requests after rollout. Do not assume `cf workers versions create` activates that version.

## F. Cache purging and site rules

```bash
cf cli search "purge cached files for a URL"
cf cache purge --help
cf cli search "update zone cache settings"
```

Prefer targeted URL/tag/prefix purges to global purge. Estimate cache miss / origin amplification impact; understand revalidation behavior. For WAF/redirect/rate-limit rule changes, read the entire ruleset first to preserve ordering and expressions. Do not overwrite a ruleset from an incomplete paginated listing.

## G. Zero Trust / WAF / API Shield / bot controls

```bash
cf cli search "list Access applications"
cf cli search "create an Access policy"
cf cli search "list WAF custom rulesets"
cf cli search "update firewall rate limiting rule"
cf cli search "configure API Shield schema validation"
```

These are **discovery queries**. Confirm account, zone, configuration version, order/priority, service tokens and impacted principals. Make a backup of rules and evaluate syntax before changing enforcement. Use a staged/log-only configuration when supported. Verify real user and bot traffic, and plan fast rollback.

## H. Cloudflare Tunnel and local development sharing

```bash
cf tunnels quick-start http://localhost:3000
cf tunnels quick-start http://localhost:3000 --allowed-mail 'alice@example.com,*@example.org'
cf cli search "list named Cloudflare Tunnels"
```

`--allowed-mail` was added in beta.13 and requires **cloudflared 2026.9.2+** for protected temporary tunnels. Tunnel/API management and the running `cloudflared` connector are different. Check if exposing a dev server is appropriate and auth is enforced; temporary public URLs should not be used as permanent secure production endpoints.

## I. Analytics and logs

```bash
cf cli search "get Workers analytics metrics"
cf cli search "query zone security events"
cf cli search "list Logpush jobs"
```

Read schema parameters (time range, granularity, zone/account and pagination). `cf` does not currently stream live Worker logs; use `npx wrangler tail WORKER_NAME` or inspect local traces via Local Explorer. Never publish sensitive traffic logs in reports.

## J. Media, AI, and other products

```bash
cf cli search "run Workers AI inference"
cf cli search "list Images uploaded to an account"
cf cli search "get a video Stream status"
cf cli search "list Vectorize indexes"
cf cli search "create a Queue"
cf cli search "create Hyperdrive configuration"
```

Search results are not evidence of account entitlement or command availability. Inspect model/binary output type, cost/usage limits and token permissions. Redirect binary outputs to files, never parse them as JSON. For product implementations, consult the product-specific Cloudflare documentation via `cf docs search`.

Sources: https://developers.cloudflare.com/cf/get-started/resources/ ; https://developers.cloudflare.com/cf/projects/ ; https://developers.cloudflare.com/cf/agents/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
