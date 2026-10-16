---
name: cloudflare
description: >-
  Comprehensive Cloudflare platform skill for coding agents. Defaults always to Cloudflare's agent-oriented cf CLI (beta) for public API, resource orchestration, and typed Workers projects, with Wrangler available strictly as a fallback. Covers architecture (Anycast, V8 isolates, request lifecycle, bindings RPC), storage (KV, D1, R2, Hyperdrive, Queues), AI (Workers AI, Vectorize, Agents SDK), networking (Cloudflare Tunnels, Zero Trust, WARP), security (WAF, Turnstile), live docs retrieval (cf docs search, cf schema), guardrails, and deterministic helpers.
---

# Cloudflare Platform Skill: Architecture, Tooling & Operations

A unified operational skill for building, deploying, and managing infrastructure and code across the Cloudflare ecosystem.

---

## 1. Tool Precedence: Always Default to `cf`

Coding agents operating in Cloudflare environments must enforce a strict tool priority:

```
[Cloudflare Task]
       │
       ▼
[1. Default & Primary: `cf` CLI] ──► Use for all public API resources, account/zone operations,
       │                             DNS, D1, KV, R2, Queues, Tunnels, AI, and modern typed
       │                             Workers projects (`cloudflare.config.ts`).
       │ (Only if unmigrated legacy configuration exists)
       ▼
[2. Fallback Only: `wrangler`] ────► ONLY when an existing project has `wrangler.jsonc` or
                                     `wrangler.toml` and cannot yet be migrated to `cf`.
                                     Recommend deliberate migration (`references/wrangler-migration.md`).
```

### Why `cf` Is the Primary Tool for Agents
- **Self-Discovering**: 2,900+ generated API commands discoverable in real time via `cf cli search "<intent>"`.
- **Schema-Aware**: Inspect exact JSON payloads via `cf schema <group> <op>` without guessing parameters.
- **Built-in Docs Search**: Instant documentation retrieval via `cf docs search "<query>"`.
- **Dry-Run Inspection**: Safe preflight preview with `--dry-run` outputting method, path, query, and payload.
- **Modern Typed Configuration**: Direct authoring with TypeScript autocomplete via `cloudflare.config.ts`.

---

## 2. Cloudflare Architecture & Execution Model

### The Global Anycast Edge
- **330+ edge datacenters (colos)** announce the identical IP address block via BGP Anycast.
- Traffic automatically terminates at the topologically closest datacenter to the user.
- No central AWS/GCP-style regions: compute and storage run globally distributed across every node.

### V8 Isolates vs Containers (`workerd`)
- Cloudflare Workers run on Google V8 engine isolates inside the open-source **`workerd`** runtime.
- **Cold start: < 5ms** (effectively zero) vs 200ms–2,000ms for Docker/microVM containers.
- **Memory footprint: ~3MB baseline** vs 50MB+ for traditional Lambda containers.
- Thousands of independent customer isolates run concurrently within single processes with hardware-grade memory protection.

### Request Lifecycle
```
[Client Request]
       │
       ▼
[1. Anycast BGP Routing] ──► Reaches closest Edge Colo (e.g., AMS, LHR, SFO)
       │
       ▼
[2. TLS 1.3 / HTTP/3] ─────► Handshake terminated at the edge
       │
       ▼
[3. Layer 3/4/7 Protection] ─► Magic Transit DDoS mitigation, WAF Rulesets, Bot Management, Turnstile
       │
       ▼
[4. Cache Lookup] ──────────► Tiered Cache / Cache Reserve
       │ (Miss)
       ▼
[5. V8 Isolate Execution] ──► Worker `export default { fetch }` handler executes
       │
       ├──► Zero-overhead internal RPC to Bindings (D1, KV, R2, Vectorize, Hyperdrive, AI)
       ├──► Subrequests (`fetch`) to Origin backends or external APIs
       └──► Durable Objects / WebSockets routing
       │
       ▼
[6. Response Streaming] ────► `TransformStream` pipes chunked response directly to client
       │
       ▼
[7. Background Tasks] ──────► `ctx.waitUntil(promise)` continues processing after response finishes
```

### Bindings: Zero-Overhead RPC
Unlike typical cloud services where database access requires external TCP handshakes, TLS negotiation, and secret management:
- Cloudflare bindings (`env.DB`, `env.KV`, `env.AI`, `env.BUCKET`) are **in-process memory or local socket IPC handles**.
- No database credentials, API tokens, or secrets leak into application code; authorization is cryptographically enforced by the edge runtime.

### Smart Placement
- When a Worker frequently queries a backend origin database (e.g., Postgres in `us-east-1`), enabling Smart Placement (`smart_placement = true`) automatically moves the Worker execution to an edge datacenter adjacent to the database origin, eliminating cross-continental round-trip delays.

---

## 3. Product & Feature Architecture

### Compute
- **Workers**: Serverless edge compute for APIs, proxies, and full-stack backends (`references/workers/`).
- **Pages**: Jamstack frontend hosting with Git deployments and full-stack Pages Functions (`references/pages/`).
- **Durable Objects**: Globally unique actor instances with strongly consistent, embedded SQLite storage (`ctx.storage.sql`) and WebSocket hibernation (`references/durable-objects/`).
- **Workflows**: Durable multi-step state machines with automatic retry, exponential backoff, and arbitrary sleep (`references/workflows/`).
- **Containers & Sandboxes**: Ephemeral container execution for untrusted code execution (`references/containers/`, `references/sandbox/`).
- **Snippets**: Lightweight edge logic for fast HTTP header and request modification (`references/snippets/`).

### Storage & Persistence
- **D1**: Serverless distributed SQLite with read replication, Time Travel point-in-time recovery, and transactions (`references/d1/`).
- **KV**: Ultra-low-latency globally replicated key-value store for read-heavy workloads (`references/kv/`).
- **R2**: S3-compatible object storage with **zero egress bandwidth fees** and event notifications (`references/r2/`).
- **Hyperdrive**: Connection pooling and query caching accelerator for existing Postgres/MySQL databases (`references/hyperdrive/`).
- **Queues**: Serverless edge message broker with at-least-once delivery, dead-letter queues, and batching (`references/queues/`).
- **Vectorize**: Globally distributed vector database for embeddings, similarity search, and RAG (`references/vectorize/`).

### AI & Agents
- **Workers AI**: Serverless GPU inference on global edge hardware for Llama 3, Mistral, Whisper, and embeddings (`references/workers-ai/`).
- **Agents SDK**: Framework for building stateful, collaborative AI agents backed by Durable Objects (`references/agents-sdk/`).
- **AI Gateway**: Unified reverse proxy for external and internal LLM providers with caching, rate limiting, and observability (`references/ai-gateway/`).

### Networking & Security
- **Cloudflare Tunnels**: Expose private services and local dev ports securely without opening firewall ports (`references/tunnel/`).
- **WAF**: Managed OWASP rulesets, rate limiting, and custom firewall expressions (`references/waf/`).
- **Turnstile**: Friction-free, privacy-preserving CAPTCHA replacement (`references/turnstile/`).
- **Spectrum**: TCP/UDP proxying and DDoS protection for non-HTTP protocols (`references/spectrum/`).

---

## 4. Live Documentation & Schema Retrieval Protocol

**Never guess an API signature, endpoint, or product limit.**

```
[Agent Task]
     │
     ▼
[1. Command Search] ──► `cf cli search "<task description>"`
     │
     ▼
[2. Docs Retrieval] ──► `cf docs search "<technical term>"`
     │
     ▼
[3. Schema Discovery] ► `cf schema <group> <operation>`
     │
     ▼
[4. Preview / Dry-Run] ► `cf <command> --dry-run`
     │
     ▼
[5. Execute & Verify] ► Execute approved command → query remote state to confirm
```

### Authoritative Documentation Sources
- Built-in search: `cf docs search "D1 migrations"`
- Official documentation: `https://developers.cloudflare.com/`
- Platform Changelog: `https://developers.cloudflare.com/changelog/`
- Local detailed playbooks: `references/` (76 product categories)

---

## 5. Quick Reference: Primary `cf` CLI

```bash
# 1. Environment & Auth
cf --version
cf auth whoami
cf auth login                 # Human browser approval
cf auth login --no-browser   # Container / remote session

# 2. Discovery
cf cli search "create D1 database"
cf docs search "schedule cron trigger"
cf schema d1 create
cf d1 create --help

# 3. Resources & Zones
cf zones list
cf dns records list --zone example.com
cf d1 list
cf d1 create --name my-db --dry-run
cf r2 bucket list

# 4. Project Development & Deployment
cf init my-worker             # Scaffolds typed cloudflare.config.ts
cf dev                        # Local development
cf build                      # Bundle project
cf deploy --dry-run           # Preview deployment payload
cf deploy                     # Production deployment
cf deploy --no-provision      # Prevent automatic resource creation

# 5. Diagnostic & Guardrail Helpers
python3 scripts/cf_doctor.py --cwd .
python3 scripts/cf_guard.py --cwd . cf deploy --dry-run
```

### Fallback Only: Legacy Wrangler Commands
```bash
# Use ONLY when project is unmigrated (wrangler.jsonc / wrangler.toml)
wrangler whoami
wrangler dev
wrangler deploy --dry-run
wrangler deploy
```

---

## 6. Guardrails & Best Practices

1. **Default to `cf`**: Always prefer `cf` commands and `cloudflare.config.ts`. Only invoke `wrangler` when handling legacy, unmigrated projects.
2. **Secret Redaction**: Never print `.env` files, `CLOUDFLARE_API_TOKEN`, or account keys in chat, logs, or outputs.
3. **No Blind `--force`**: Flags like `--force` or `-y` can bypass confirmation or alter API semantics. Always review command parameters first.
4. **Independent Postcondition Verification**: After executing a mutation or deployment, verify remote status via a read query (`list`, `get`, or health probe).
5. **Workers Anti-Patterns**:
   - *Floating Promises*: Never invoke background work without `ctx.waitUntil(...)`.
   - *Memory Buffering*: Never buffer large files into memory; stream via `TransformStream`.
   - *Global State*: Never mutate global variables across requests; isolates are ephemeral. Use Durable Objects for stateful coordination.
   - *Compatibility Dates*: Always set `compatibility_date` to a recent date (<30 days) and specify `"nodejs_compat"` when using Node standard modules.
