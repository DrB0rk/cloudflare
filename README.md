# cloudflare

> Comprehensive Cloudflare platform skill for coding agents. Covers Workers, Pages, storage (KV, D1, R2, Hyperdrive, Queues), AI (Workers AI, Vectorize, Agents SDK, AI Gateway), networking (Cloudflare Tunnels, Zero Trust, WARP), security (WAF, Turnstile, DDoS), developer tooling (Wrangler v3/v4, agent-oriented `cf` CLI beta, `cloudflared`, REST API), typed configuration, guardrails, and deterministic helpers.

## Overview

Modern Cloudflare projects span multiple developer layers:
- **`wrangler`**: The canonical CLI for Workers, Pages, local emulation (Miniflare), resource bindings, and deployments (`wrangler.jsonc`).
- **`cf` / `cloudflare`**: Cloudflare's agent-oriented CLI (beta) for live OpenAPI schema inspection, 2,900+ public API commands, and typed Workers projects (`cloudflare.config.ts`).
- **`cloudflared`**: Connectors for Cloudflare Tunnels (ephemeral Quick Tunnels, named ingress tunnels, and Zero Trust access).
- **Global Services**: Distributed storage (D1, KV, R2, Hyperdrive), AI/ML (Workers AI, Vectorize, Agents SDK), and edge security (WAF, Turnstile).

This skill equips AI coding agents (OMP, Claude Code, Cursor, Codex, OpenCode, Cline, etc.) with architectural decision trees, operational guardrails, secret-redacting diagnostics, and deep product playbooks across 76 categories.

## Architecture & Decision Trees

### Quick Navigation
- **Compute**: Workers, Pages, Durable Objects, Workflows, Containers, Cron Triggers, Snippets
- **Storage**: KV, D1 (SQL), R2 (Objects), Hyperdrive, Queues, Vectorize, Secrets Store
- **AI / ML**: Workers AI, Vectorize, Agents SDK, AI Gateway, AI Search
- **Networking**: Cloudflare Tunnels, Spectrum, TURN, Argo Smart Routing
- **Security**: WAF, DDoS mitigation, Bot Management, API Shield, Turnstile

## Repository Structure

```
├── LICENSE
├── README.md
└── skills/
    └── cloudflare/
        ├── SKILL.md                     # Master operational specification and decision trees
        ├── agents/                      # Agent interface definitions
        │   └── openai.yaml
        ├── assets/                      # Workflow examples and CI templates
        │   ├── AGENTS.example.md
        │   ├── github-actions-cf.yml
        │   └── github-actions-wrangler.yml
        ├── references/                  # Deep-dive guides across 76 product categories
        │   ├── authentication.md
        │   ├── capability-map.md
        │   ├── command-discovery.md
        │   ├── resource-playbooks.md
        │   ├── typed-config.md
        │   ├── wrangler-migration.md
        │   ├── workers-best-practices/
        │   ├── wrangler/
        │   ├── workers/
        │   ├── d1/
        │   ├── r2/
        │   ├── kv/
        │   ├── vectorize/
        │   ├── workers-ai/
        │   ├── tunnel/
        │   └── ...
        ├── scripts/                     # Deterministic helper tools
        │   ├── cf_discover.py           # Command & documentation discovery
        │   ├── cf_doctor.py             # Secret-redacting environment diagnostic
        │   └── cf_guard.py              # Static command preflight
        └── tests/                       # Unit tests for helpers
            └── test_helpers.py
```

## Installation

### Via `skills` CLI
```bash
npx skills add DrB0rk/cloudflare -g
```

### Manual / Symlink
Symlink into your agent skill directories:
```bash
# Universal agents standard skills directory (Cursor, Claude Code, Cline, etc.)
ln -s "/home/drb0rk/Projects/cloudflare/skills/cloudflare" ~/.agents/skills/cloudflare

# OMP agent skills directory
ln -s "/home/drb0rk/Projects/cloudflare/skills/cloudflare" ~/.omp/agent/skills/cloudflare
```

## Deterministic Helper Tools

### 1. Environment Diagnostic (`scripts/cf_doctor.py`)
Inspects the local working directory without sending API calls or leaking `.env` secrets:
```bash
python3 skills/cloudflare/scripts/cf_doctor.py --cwd .
```
Outputs installed CLI versions (Node, Wrangler, `cf`, `cloudflared`), configuration type (`wrangler-only`, `cf-configured`, or `unconfigured`), and credential presence flags.

### 2. Static Command Guardrail (`scripts/cf_guard.py`)
Validates proposed commands before execution, flagging destructive operations (`delete`, `purge`), unvetted `--force` flags, and project-tool mismatches:
```bash
python3 skills/cloudflare/scripts/cf_guard.py --cwd . wrangler deploy
python3 skills/cloudflare/scripts/cf_guard.py --cwd . cf d1 create --name db --dry-run
```

### 3. Command Discovery (`scripts/cf_discover.py`)
Safely introspects Cloudflare CLI commands, documentation, and OpenAPI schemas:
```bash
python3 skills/cloudflare/scripts/cf_discover.py "create DNS record" --inspect
```

## Testing

Run unit tests for deterministic helpers:
```bash
cd skills/cloudflare && python3 -m unittest discover tests
```

## License

[MIT](LICENSE) © 2026 DrB0rk
