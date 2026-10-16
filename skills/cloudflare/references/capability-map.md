# Capability map: Cloudflare's new `cf` CLI

Verified context: Cloudflare launched the public beta on 2026-09-28. As of 2026-10-16, the latest inspected release is `1.0.0-beta.17`. `cf` exposes **more than 2,900** public-API operations plus hand-written project commands. The real command tree is generated from the OpenAPI specification and changes between releases. This page maps capabilities, not an exhaustive immutable list of 2,900 command strings.

## Table of contents
1. Local CLI and project functions
2. Cloudflare API product families
3. Verified command anchors
4. Search recipes
5. Coverage gaps and alternative tools

## 1. Local CLI and project functions

| Capability | Verified entry points | Meaning |
| --- | --- | --- |
| Install/version | `npm i -g cf`; `cf --version` | Package installs equivalent `cf` and `cloudflare` commands; Node >= 22.18 |
| Help/completion | `cf --help`; `cf <group> --help`; `cf complete bash` | Inspect CLI trees/flags; bash, zsh, fish, PowerShell completion |
| Semantic operation lookup | `cf cli search "task"` | Local, no authentication; top five ranked commands as JSON |
| Technical documentation lookup | `cf docs search "question"` | Beta.15+; ranked live documentation URLs, title and description; login not required |
| API schema introspection | `cf schema <group> <operation>` | Generated API operation HTTP method, path, path/query params and request body fields |
| API dry-run | `<generated-command> --dry-run` | Print planned request JSON without sending it; validate redaction |
| Accounts/profiles | `cf auth login`, `whoami`, `create`, `list`, `activate`, `deactivate`, `delete`, `logout` | OAuth profiles, directory bindings, token override |
| Project creation | `cf init <dir>`; `cf init .` | Set up typed Worker project or supported framework; can modify local files/install packages |
| Development | `cf dev` | Delegate to framework/Vite or supported Wrangler build tool |
| Build | `cf build` | Validate `.cloudflare/output/v0`; no Cloudflare authentication required |
| Deploy | `cf deploy` | Build, provision missing bindings unless disabled, upload version and deploy |
| Preview deploy | `cf previews deploy [name]` | Branch/feature preview; remote write and authentication required |
| Mode selection | `cf dev/build/deploy --mode staging` | Function-form config environment selection, not `wrangler --env` |
| Prebuilt deployment | `cf deploy --prebuilt --mode production` | Deploy existing Build Output; mode must match manifest |
| Version operations | `cf workers versions create`; `cf workers deployments create`; `cf workers triggers deploy` | Separate uploading from deploying/routing triggers |
| Worker checks and types | `cf workers check`; `cf workers types` | CPU profile/startup timings; type generation `.cloudflare/types/index.d.ts` |
| Migration | `cf migrate --dry-run`; `cf migrate` | Convert Wrangler config with follow-up TODOs and review |
| Temporary tunnels | `cf tunnels quick-start <local-url>` | Development exposure; optional `--allowed-mail` in beta.13+ |
| Telemetry | `cf telemetry disable`; `CF_SEND_TELEMETRY=false` | Anonymous usage telemetry controls |

## 2. Product families accessible through generated commands

**Important:** product names below describe capability areas. They are not guaranteed to be exact CLI group names or proof that every action has an endpoint. Use `cf cli search` and `cf schema` for the installed release.

### Account administration and billing
Accounts, memberships, API tokens and access management, subscriptions, billing, profile settings, audit logs, services and account-level configuration. Scope credentials, resource and user carefully; never mutate permissions from guessed commands.

### DNS and zone administration
Zones, DNS records, DNS analytics/settings, DNSSEC, zone settings, redirects, SSL/TLS, certificates, managed origins, custom hostnames, cache rules, purge, Always Online, load balancing, health checks, traffic steering and domain products. Distinguish zone IDs from domains; inspect proxy/CDN impact.

### Developer compute
Workers scripts/versions/deployments, Workers Builds, Worker routes/domains/triggers, Pages projects and deployments (if surfaced in the public API), Containers, Durable Objects, Workflows, Cron Triggers, Queues, Dispatch namespaces/Workers for Platforms, Browser Run/Browser Rendering, Worker observability and analytics.

### Storage and data platforms
R2 buckets and objects, D1 databases and migrations/queries, Workers KV namespaces/keys, Vectorize, Hyperdrive, Analytics Engine, R2 data-platform services where exposed, data pipelines and database services. Be alert to `--local` only on supported commands, and the difference between resource *name* and ID.

### AI and media
Workers AI, AI Gateway, AI Search where surfaced, Vectorize, model metadata and inference endpoints, Images, Stream, Media Transformation, Web Analytics and Browser Run. Raw binary responses may be written to stdout; redirect to file.

### Security and Zero Trust
WAF managed/custom rules and rulesets, rate limiting, Bot Management, DDoS controls, API Shield, Turnstile, Zero Trust Access apps/policies, Tunnels and connectors, Gateway, device posture, security analytics, firewall/security settings. These can affect live traffic and identities immediately.

### Connectivity / networking
Tunnels, Magic WAN and Magic Transit, Spectrum, load balancers, IP address management, network interconnect, private network resources and related public API capabilities. Note that managing a Tunnel by API and running the `cloudflared` tunnel connector are distinct tasks.

### Monitoring, reporting and analytics
Zones analytics, Workers metrics, GraphQL Analytics API (as supported), Logpush jobs, audit records, error traces, security analytics and other published analytics endpoints. Inspect period, aggregation grain and pagination; some data products have a distinct GraphQL/SQL interface.

### Email and domains
Email Routing, email products, domain registrar operations and related account settings when surfaced through the public API.

## 3. Verified command anchors

The following **specific syntax anchors** are from published CLI docs/changelog. Re-run `--help` in your environment because beta.16 renamed several groups into kebab-case.

```bash
cf zones list
cf zones list --name example.com
cf dns records list --zone example.com --type A
cf dns records create --zone example.com --body '{"type":"A","name":"test","content":"192.0.2.1","proxied":true}' --dry-run
cf dns records delete RECORD_ID --zone example.com
cf d1 create --name example-db --dry-run
cf d1 query DATABASE_ID --sql 'SELECT 1'
cf d1 raw DATABASE_ID --sql 'SELECT 1' --local
cf d1 migrations list --local
cf d1 migrations apply --local
cf kv namespaces list
cf r2 buckets list
cf r2 objects list --bucket-name my-bucket --local
cf cache purge --help
cf workers versions create
cf workers triggers deploy
cf workers deployments create --worker example-worker --strategy percentage --versions '[{"version_id":"VERSION_ID","percentage":100}]'
cf workers types
cf workers check
cf tunnels quick-start http://localhost:3000 --allowed-mail 'person@example.com'
```

`cf d1 query` uses a **database ID**, not a friendly name. For DNS create, `--body` is required by the published guide, while some other generated operations expose body-field options.

## 4. Search recipes: always discover before acting

```bash
cf cli search "list API tokens for an account"
cf cli search "list and update WAF custom rules"
cf cli search "create an R2 bucket"
cf cli search "put an object in R2"
cf cli search "manage Hyperdrive database configurations"
cf cli search "create an Access application policy"
cf cli search "create a Worker version"
cf cli search "show recent Workers logs"
cf cli search "list Pages deployment status"
cf cli search "purge cache for a URL"
cf cli search "query Workers AI model"
cf cli search "configure Cloudflare Tunnel routes"
cf docs search "how to connect a Cloudflare Worker to a D1 database"
```

These are **search inputs**, not proof that a matching command currently exists. Use returned summaries to select the best candidate. Inspect the schema/help, output and authorization before running anything.

## 5. Known coverage gaps

- `cf` does not yet stream live Worker logs (`npx wrangler tail WORKER_NAME`).
- `cf` does not yet set a *single* Worker secret like `wrangler secret put` (use `npx wrangler secret put NAME --name WORKER_NAME` or deploy with `--secrets-file`).
- Some existing Wrangler project features require conversion/manual follow-ups, especially DO migrations, Workflows and Containers.
- A local Worker may use a Vite plugin or Wrangler as its underlying build/development tool even when `cf` is the top-level CLI.
- The public API surface is not the same as every UI-only feature, internal endpoint, product SDK, streaming/debug function, or `cloudflared` connector daemon.
- A generated API command may exist but require permissions/products not enabled on the current plan; do not equate command existence with entitlement.

Primary sources: https://developers.cloudflare.com/cf/ ; https://developers.cloudflare.com/cf/agents/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md ; https://developers.cloudflare.com/cf/wrangler/reference/
