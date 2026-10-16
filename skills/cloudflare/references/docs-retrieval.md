# Cloudflare Documentation Retrieval: Guidelines for AI Agents

A protocol for discovering, querying, and verifying live Cloudflare documentation, API schemas, and platform capabilities.

---

## 1. The Core Principle: Discover Rather Than Guess

Cloudflare continuously evolves its public API, OpenAPI specs, compatibility flags, and product limits. **Never hallucinate flags, endpoint paths, or binding shapes.** An agent must always query live references before executing mutations or writing non-trivial configurations.

### Authoritative Hierarchy
1. **Live CLI Schema & Help**: `cf schema <group> <op>` and `<cmd> --help`.
2. **Live Docs Search**: `cf docs search "<query>"`.
3. **Official Developer Docs**: `https://developers.cloudflare.com/`.
4. **Product Changelog**: `https://developers.cloudflare.com/changelog/`.
5. **Local Reference Files**: `references/` (curated high-density knowledge base).

---

## 2. Using `cf docs search` (Interactive & Scriptable)

The `cf` CLI includes a built-in search engine for Cloudflare's entire documentation:

```bash
# Search live documentation guides
cf docs search "how to configure D1 database"
cf docs search "Workers AI model pricing and limits"
cf docs search "Durable Objects SQLite migration"
cf docs search "Cloudflare Tunnel ingress rules"

# Or use the skill's discovery helper:
python3 scripts/cf_discover.py "D1 database" --docs
```

The output returns direct URLs, section titles, and concise excerpts from Cloudflare's official docs.

---

## 3. OpenAPI Schema Inspection (`cf schema`)

To verify the exact JSON request body, required fields, and path parameters for any generated API command:

```bash
# Discover schema for a command group and operation
cf schema d1 create
cf schema dns records create
cf schema r2 bucket create
cf schema workers deployments create

# Or inspect schema automatically via helper:
python3 scripts/cf_discover.py "create D1 database" --inspect
```

### Reading Schema Output
- `httpMethod`: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- `path`: Contains required path parameters (e.g., `/accounts/{account_id}/d1/database`).
- `body`: Type definition of all acceptable fields (strings, booleans, enums).
- `required`: List of properties that must be supplied for the request to succeed.

---

## 4. Compatibility Dates and Flags

Workers projects require a `compatibility_date` in their configuration (`cloudflare.config.ts` or `wrangler.jsonc`).

```typescript
// cloudflare.config.ts
export default {
  name: "my-worker",
  main: "src/index.ts",
  compatibility_date: "2026-10-15",
  compatibility_flags: [
    "nodejs_compat",            // Full Node.js standard library polyfills
    "no_global_navigator",      // Modern web standard compliance
  ]
};
```

### Guidelines for Agents
- **Always set `compatibility_date` to a recent date** (within 30 days of the current date) to ensure modern JavaScript and web standard behaviors.
- **Node.js Compatibility**: Always specify `"nodejs_compat"` when importing Node built-in modules (`node:crypto`, `node:buffer`, `node:stream`, `node:events`).
- **Never guess a compatibility flag**: If a library requires special flags, check `cf docs search "compatibility flags"` or https://developers.cloudflare.com/workers/configuration/compatibility-dates/.

---

## 5. Live Retrieval Workflow for Coding Tasks

```
[Agent Receives Task]
         │
         ▼
[1. Search Command] ───────► `cf cli search "describe task"` (identifies command path)
         │
         ▼
[2. Search Docs] ──────────► `cf docs search "technical term"` (clarifies caveats/limits)
         │
         ▼
[3. Inspect Schema] ───────► `cf schema <group> <op>` (gets exact payload structure)
         │
         ▼
[4. Preview via Dry-Run] ──► `cf <cmd> --dry-run` (verifies generated payload safely)
         │
         ▼
[5. Author Code / Apply] ──► Executes verified command with explicit parameters
```

---

## 6. Official Documentation Endpoints

| Product Domain | Canonical Documentation URL |
| :--- | :--- |
| **Workers & Edge Compute** | `https://developers.cloudflare.com/workers/` |
| **Durable Objects** | `https://developers.cloudflare.com/durable-objects/` |
| **D1 SQL Database** | `https://developers.cloudflare.com/d1/` |
| **R2 Object Storage** | `https://developers.cloudflare.com/r2/` |
| **KV Storage** | `https://developers.cloudflare.com/kv/` |
| **Vectorize** | `https://developers.cloudflare.com/vectorize/` |
| **Workers AI** | `https://developers.cloudflare.com/workers-ai/` |
| **Cloudflare Tunnels** | `https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/` |
| **WAF & Security** | `https://developers.cloudflare.com/waf/` |
| **Turnstile** | `https://developers.cloudflare.com/turnstile/` |
| **Platform Changelog** | `https://developers.cloudflare.com/changelog/` |
