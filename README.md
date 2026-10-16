# cloudflare

> Comprehensive Cloudflare platform skill for AI coding agents. **Defaults always to Cloudflare's new agent-oriented `cf` CLI**, using Wrangler strictly as a last-resort fallback for legacy projects. Covers global edge architecture, live documentation discovery, V8 isolates, request lifecycle, distributed storage, AI, Zero Trust tunnels, and deterministic safety guardrails.

---

## 1. Tool Precedence: Default to `cf`

```
┌────────────────────────────────────────────────────────┐
│  PRIMARY / DEFAULT: `cf` CLI (Cloudflare Agent CLI)    │
│  - 2,900+ OpenAPI commands with live search & schema   │
│  - Live Cloudflare Docs search (cf docs search)        │
│  - Typed Workers projects (cloudflare.config.ts)       │
│  - All resource & zone operations (DNS, D1, R2, WAF)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (Only when project is unmigrated)
┌────────────────────────────────────────────────────────┐
│  FALLBACK ONLY: `wrangler` CLI                         │
│  - Strictly for legacy unmigrated projects             │
│    (wrangler.jsonc / wrangler.toml)                    │
│  - Recommend intentional migration to cf               │
└────────────────────────────────────────────────────────┘
```

---

## 2. Cloudflare Architecture & Execution Model

This skill incorporates deep architectural knowledge of Cloudflare's global edge:

* **Global Anycast Network**: 330+ edge datacenters (colos) announce the same BGP IP block. Traffic automatically terminates at the topologically closest datacenter to the user.
* **V8 Isolates vs Containers (`workerd`)**: Cloudflare Workers execute as lightweight Google V8 engine isolates inside single processes. Startup/cold start is **< 5ms** (effectively zero) with a **~3MB memory baseline**, compared to 200ms–2s cold starts and 50MB+ overhead for Docker/Lambda containers.
* **Bindings as Zero-Overhead RPC**: Resource bindings (`env.DB`, `env.KV`, `env.R2`, `env.AI`) operate via in-process memory or local socket IPC. No TCP handshakes, external HTTP calls, or credentials exposed in code.
* **Durable Objects**: Globally unique actor instances with strongly consistent embedded SQLite storage (`ctx.storage.sql`) and WebSocket connection hibernation.
* **Smart Placement**: Automatically moves Worker execution adjacent to backend database origins when cross-continental backend latency exceeds user edge latency.
* **Workflows Engine**: Multi-step stateful durable executions with automatic retries, exponential backoff, and arbitrary sleep periods.

*See [`references/architecture-deep-dive.md`](skills/cloudflare/references/architecture-deep-dive.md) for full architectural documentation.*

---

## 3. Live Documentation & Schema Retrieval

**Never hallucinate API signatures, endpoint flags, or limits.** Coding agents must discover live schemas and documentation:

1. **Live Docs Search**:
   ```bash
   cf docs search "how to configure D1 database"
   python3 skills/cloudflare/scripts/cf_discover.py "D1 database" --docs
   ```
2. **OpenAPI Schema Discovery**:
   ```bash
   cf schema d1 create
   python3 skills/cloudflare/scripts/cf_discover.py "create D1 database" --inspect
   ```
3. **Command Discovery**:
   ```bash
   cf cli search "create DNS record"
   ```
4. **Authoritative Sources**:
   * Developer Documentation: `https://developers.cloudflare.com/`
   * Platform Changelog: `https://developers.cloudflare.com/changelog/`

*See [`references/docs-retrieval.md`](skills/cloudflare/references/docs-retrieval.md) for live retrieval protocol.*

---

## 4. Product & Feature Matrix

The skill includes deep reference playbooks across **76 product categories**:

* **Compute & Execution**: Workers, Pages, Durable Objects, Workflows, Containers, Cron Triggers, Snippets, Tail Workers.
* **Storage & Data**: D1 (distributed SQL), KV, R2 (zero-egress object storage), Hyperdrive (Postgres/MySQL accelerator), Queues, Vectorize, Secrets Store.
* **AI & Machine Learning**: Workers AI (Llama 3, Mistral, Whisper, embeddings), Agents SDK, AI Gateway, AI Search.
* **Networking & Ingress**: Cloudflare Tunnels (`cf` / `cloudflared` named & quick tunnels), Spectrum (TCP/UDP proxy), TURN relay, Argo Smart Routing.
* **Security**: Web Application Firewall (WAF), Managed Rulesets, Rate Limiting, Bot Management, API Shield, Turnstile (invisible CAPTCHA).

---

## 5. Repository Structure

```
├── LICENSE
├── README.md
└── skills/
    └── cloudflare/
        ├── SKILL.md                     # Master specification, architecture, and cf-first directives
        ├── agents/                      # Agent interface definitions
        │   └── openai.yaml
        ├── assets/                      # Workflow templates
        │   ├── AGENTS.example.md
        │   ├── github-actions-cf.yml
        │   └── github-actions-wrangler.yml
        ├── references/                  # Deep-dive library across 76 categories
        │   ├── architecture-deep-dive.md# Global Anycast, V8 isolates, request lifecycle, RPC
        │   ├── docs-retrieval.md        # Protocol for cf docs search and live schema retrieval
        │   ├── command-discovery.md     # cf cli search and dynamic discovery
        │   ├── typed-config.md          # cloudflare.config.ts reference
        │   ├── wrangler-migration.md    # Step-by-step migration from Wrangler to cf
        │   ├── workers/
        │   ├── d1/
        │   ├── r2/
        │   ├── kv/
        │   ├── vectorize/
        │   ├── workers-ai/
        │   ├── tunnel/
        │   └── ...
        ├── scripts/                     # Deterministic helper tools
        │   ├── cf_discover.py           # Command, schema & docs discovery
        │   ├── cf_doctor.py             # Secret-redacting environment diagnostic
        │   └── cf_guard.py              # Static command preflight
        └── tests/                       # Unit tests
            └── test_helpers.py
```

---

## 6. Installation

### Via `skills` CLI
```bash
npx skills add DrB0rk/cloudflare -g
```

### Manual / Symlink
```bash
# Universal agents standard skills directory (Cursor, Claude Code, Cline, etc.)
ln -s "/home/drb0rk/Projects/cloudflare/skills/cloudflare" ~/.agents/skills/cloudflare

# OMP agent skills directory
ln -s "/home/drb0rk/Projects/cloudflare/skills/cloudflare" ~/.omp/agent/skills/cloudflare
```

---

## 7. Deterministic Helpers

* **`cf_doctor.py`**: Local environment inspection (detects Node, `cf` CLI, Wrangler, `cloudflared`, project config, and redacts secrets).
* **`cf_guard.py`**: Static preflight assessing proposed commands, flagging destructive actions (`delete`, `purge`), unvetted `--force` flags, and notifying if Wrangler is used instead of `cf`.
* **`cf_discover.py`**: Discovery helper executing `cf cli search`, `cf docs search`, schema checks, and `--help` queries without shell injection risk.

---

## 8. Testing

Run unit tests:
```bash
cd skills/cloudflare && python3 -m unittest discover tests
```

---

## License

[MIT](LICENSE) © 2026 DrB0rk
