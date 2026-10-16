---
name: cloudflare
description: >-
  Comprehensive Cloudflare platform skill for coding agents. Covers Workers, Pages, storage (KV, D1, R2, Hyperdrive, Queues), AI (Workers AI, Vectorize, Agents SDK, AI Gateway), networking (Cloudflare Tunnels, Zero Trust, WARP, Spectrum), security (WAF, DDoS, Turnstile), developer tooling (Wrangler v3/v4, agent-oriented cf CLI beta, cloudflared, REST API), typed cloudflare.config.ts and wrangler.jsonc configuration, architectural decision trees, safety guardrails, and deterministic helpers.
---

# Cloudflare Platform Skill: Architecture, Tooling & Operations

A unified operational skill for building, deploying, and managing infrastructure and code across the entire Cloudflare ecosystem.

## Tooling Landscape: Choosing the Right Tool

| Tool | Primary Purpose | Project Files | Command Style |
| :--- | :--- | :--- | :--- |
| **`wrangler`** | Canonical Workers, Pages, local dev (Miniflare), bindings, and deploys | `wrangler.jsonc`, `wrangler.json`, `wrangler.toml` | `npx wrangler dev`, `npx wrangler deploy` |
| **`cf` / `cloudflare`** | Agent-oriented CLI for public API resources and typed Workers projects | `cloudflare.config.ts` | `cf cli search`, `cf schema`, `cf dev` |
| **`cloudflared`** | Ingress, local service tunneling, Quick Tunnels, Zero Trust WARP routing | `config.yml` (optional) | `cloudflared tunnel run`, `cloudflared tunnel route` |
| **REST / IaC** | Account automation, bulk resources, cross-zone orchestration | Terraform (`.tf`), Pulumi (`index.ts`) | Cloudflare v4 REST API, Terraform Cloudflare Provider |

### Decision Rules for Coding Agents
1. **Existing project with `wrangler.jsonc`, `wrangler.json`, or `wrangler.toml`**: Use **Wrangler** for dev, build, and deploy. `cf` can still inspect public API resources, but **never run `cf init`, `cf dev`, `cf build`, or `cf deploy`** in a Wrangler project before explicit migration (`references/wrangler-migration.md`).
2. **Project with `cloudflare.config.ts`**: Use **`cf`** for dev, build, deploy, and bindings.
3. **Infrastructure/Resource Operations (DNS, Zones, Tunnels, WAF, Turnstile, Accounts)**: Use **`cf`** CLI with schema discovery (`cf cli search "..."` → `cf schema <group> <op>`) or Wrangler for resource bindings (`wrangler d1`, `wrangler r2`, `wrangler kv`).
4. **Local Port Exposure / Tunnels**: Use **`cloudflared`** (`cloudflared tunnel --url http://localhost:PORT` for quick testing; named tunnels for persistent DNS routing).

---

## Architectural Decision Trees

### 1. Compute & Application Runtime
```
Need to run code?
├─ Serverless HTTP/WebSocket API at the edge → references/workers/
├─ Full-stack web app with static assets & SSR → references/pages/ or references/static-assets/
├─ Strongly-consistent stateful coordination / WebSockets → references/durable-objects/
├─ Long-running, multi-step durable workflows → references/workflows/
├─ Ephemeral sandboxed container executions → references/containers/ or references/sandbox/
├─ Customer-facing multitenant code execution → references/workers-for-platforms/
├─ Scheduled background tasks → references/cron-triggers/
├─ Lightweight HTTP request/response modifications → references/snippets/
├─ Execution logs and trace processing → references/tail-workers/
└─ Dynamic routing to origin backend → references/smart-placement/
```

### 2. Storage & Data Persistence
```
Need storage?
├─ Fast globally distributed Key-Value (config, sessions, metadata) → references/kv/
├─ Relational serverless SQL database (SQLite distributed with read replication) → references/d1/
├─ S3-compatible zero-egress object storage (assets, exports, buckets) → references/r2/
├─ Accelerated pooled proxy for existing Postgres/MySQL database → references/hyperdrive/
├─ Asynchronous message queues (guaranteed delivery, batching) → references/queues/
├─ Vector embeddings store for RAG / similarity search → references/vectorize/
├─ Strongly-consistent transaction state per single entity → references/do-storage/
├─ Centralized secrets management and rotation → references/secrets-store/
└─ High-throughput streaming data into R2 (ETL) → references/pipelines/
```

### 3. AI & Machine Learning
```
Need AI / ML?
├─ Serverless model inference (Llama, Mistral, Whisper, Embeddings) → references/workers-ai/
├─ Vector search index for semantic embeddings → references/vectorize/
├─ Stateful AI agents with memory, tool calling, and human-in-the-loop → references/agents-sdk/
├─ Unified AI provider proxy (caching, fallback, analytics, rate limiting) → references/ai-gateway/
└─ AI-powered site search widget → references/ai-search/
```

### 4. Networking & Connectivity
```
Need connectivity?
├─ Expose local dev server to the public internet securely → references/tunnel/
├─ TCP / UDP proxy for non-HTTP services (gaming, SSH, databases) → references/spectrum/
├─ WebRTC TURN relay server for low-latency P2P media → references/turn/
├─ Private multi-cloud or on-prem connectivity → references/network-interconnect/
└─ Intelligent latency-optimized edge routing → references/argo-smart-routing/
```

### 5. Security & Threat Prevention
```
Need security?
├─ Programmable Web Application Firewall & custom rulesets → references/waf/
├─ DDoS protection and layer 7 rate limiting → references/ddos/
├─ Bot mitigation and automated scraper detection → references/bot-management/
├─ API Schema validation and mTLS → references/api-shield/
└─ Invisible, privacy-preserving CAPTCHA alternative → references/turnstile/
```

---

## The Required Agent Operating Loop

1. **Inspect without mutation:**
   Run `python scripts/cf_doctor.py --cwd .` to identify working directory status, installed tools (Node, Wrangler, `cf`, `cloudflared`), configuration files, and active credentials without leaking secrets.
2. **Choose tool and config target:**
   Determine whether the project uses `wrangler.jsonc` or `cloudflare.config.ts`. Never mix build systems blindly.
3. **Discover rather than hallucinate commands:**
   - For `cf` CLI: `cf cli search "intent"` → `cf schema <group> <op>` → `<command> --help`.
   - For Wrangler: `wrangler --help` or inspect `references/wrangler/commands-guide.md`.
   - For Cloudflare Docs: `cf docs search "query"` or consult `references/`.
4. **Scope the target:**
   Resolve explicit `CLOUDFLARE_ACCOUNT_ID`, `--zone`, environment (`--env production`), and resource ID before mutating anything.
5. **Preflight Guardrail:**
   Run `python scripts/cf_guard.py --cwd . <command>` to verify the command path. Flags like `--force` or write operations (`delete`, `purge`, `revoke`, `deploy`) require explicit operator authorization.
6. **Preview:**
   Use `--dry-run` where supported (`cf deploy --dry-run`, `wrangler deploy --dry-run`). Review output payload structure.
7. **Execute:**
   Run with explicit flags; capture return codes and stdout/stderr. Do not hide errors.
8. **Verify Remote Postcondition:**
   Issue a read query (`list`, `get`, `check`) to verify the state on Cloudflare's network independently.

---

## Quick Reference: Core Commands

### Wrangler CLI
```bash
# Check version & status
wrangler --version
wrangler whoami

# Project development & build
wrangler dev                    # Local development with Miniflare
wrangler dev --remote           # Dev server against real Cloudflare resources
wrangler deploy                 # Deploy Worker to production
wrangler deploy --dry-run       # Preview deployment without publishing
wrangler types                  # Generate TypeScript bindings from config

# Storage & Bindings
wrangler d1 list
wrangler d1 execute <db-name> --command "SELECT * FROM users;"
wrangler kv namespace list
wrangler kv key get <namespace-id> <key>
wrangler r2 bucket list
wrangler vectorize list

# Secrets
wrangler secret put <KEY>
wrangler secret list

# Real-time Logs
wrangler tail                   # Stream live invocation logs
```

### `cf` CLI (Agent-Oriented)
```bash
# Discovery
cf cli search "create DNS record"
cf docs search "D1 database migrations"
cf schema d1 create
cf d1 create --help

# Execution & Dry Run
cf auth whoami
cf zones list
cf dns records list --zone example.com
cf d1 create --name my-db --dry-run
cf deploy --dry-run
```

### Cloudflare Tunnels (`cloudflared`)
```bash
# Quick ephemeral tunnel (no account required, trycloudflare.com)
cloudflared tunnel --url http://localhost:8080

# Authenticated named tunnel
cloudflared tunnel login
cloudflared tunnel create my-service
cloudflared tunnel route dns my-service api.example.com
cloudflared tunnel run my-service
```

---

## Guardrails & Best Practices

- **Never Hallucinate Flags or APIs**: Always verify with `cf schema`, `wrangler --help`, or `references/`.
- **Secret Redaction**: Never print `.env` values, `CLOUDFLARE_API_TOKEN`, or account keys in chat, logs, or reports.
- **Workers Anti-Patterns**:
  - *Floating Promises*: Never initiate background promises without `ctx.waitUntil(promise)`. Unawaited promises can be terminated prematurely when the response finishes.
  - *Streaming*: Never buffer large payloads into memory. Use `TransformStream` and stream directly to/from R2 or client.
  - *Global State*: Never rely on global variable mutations across requests; Workers are ephemeral isolates. Use Durable Objects for stateful coordination.
- **Wrangler Config**: Always prefer `wrangler.jsonc` (JSON with comments) over `wrangler.toml` for modern features and strict typing.
- **Explicit Rollback**: Always specify rollback commands when proposing infrastructure changes.

---

## Reference Library Index

The `references/` directory contains complete documentation across 76 product categories:

- **Operational Playbooks**: `references/command-discovery.md`, `references/authentication.md`, `references/typed-config.md`, `references/wrangler-migration.md`, `references/version-drift.md`, `references/resource-playbooks.md`, `references/debugging.md`, `references/ci-cd.md`.
- **Wrangler & Rules**: `references/wrangler/commands-guide.md`, `references/workers-best-practices/rules.md`, `references/workers-best-practices/review.md`.
- **Compute**: `references/workers/`, `references/pages/`, `references/durable-objects/`, `references/workflows/`, `references/containers/`, `references/cron-triggers/`, `references/snippets/`.
- **Storage**: `references/kv/`, `references/d1/`, `references/r2/`, `references/hyperdrive/`, `references/queues/`, `references/vectorize/`, `references/secrets-store/`.
- **AI & ML**: `references/workers-ai/`, `references/agents-sdk/`, `references/ai-gateway/`, `references/ai-search/`.
- **Networking & Security**: `references/tunnel/`, `references/waf/`, `references/turnstile/`, `references/ddos/`, `references/bot-management/`, `references/api-shield/`, `references/spectrum/`.
- **Media & Content**: `references/images/`, `references/stream/`, `references/browser-rendering/`, `references/zaraz/`.
- **Infrastructure as Code**: `references/terraform/`, `references/pulumi/`, `references/api/`, `references/graphql-api/`.
