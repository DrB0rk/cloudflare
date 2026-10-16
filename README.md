# cloudflare-cf

> Operational skill for coding agents managing Cloudflare's new agent-oriented `cf` CLI (beta), its 2,900+ API commands, and Workers projects.

## Overview

Cloudflare's **`cf`** (also installed as **`cloudflare`**) is an agent-oriented CLI for Cloudflare public API operations and Workers projects. It introduces schema inspection, dry-run capabilities, profile management, and typed configuration (`cloudflare.config.ts`).

This skill equips AI coding agents (OMP, Claude Code, Cursor, Codex, OpenCode, Cline, etc.) with safe operating protocols, discovery routines, guardrails, and deterministic helper scripts to interact with Cloudflare via `cf`.

## Key Capabilities

- **Command & Schema Discovery**: Live inspection via `cf cli search`, `cf docs search`, and `cf schema` without hallucinating flags or endpoints.
- **Safety Preflight & Guardrails**: Automated guardrails (`scripts/cf_guard.py`) preventing accidental mutations, unauthorized deletes, and project-tool mismatches.
- **Read-Only Diagnostics**: `scripts/cf_doctor.py` safely inspects working directory status, runtime, and configuration without leaking secrets.
- **Wrangler Coexistence**: Enforces strict separation between legacy Wrangler (`wrangler.toml` / `wrangler.json`) and `cloudflare.config.ts` projects.
- **Typed Configuration**: Guidance for authoring and validating typed Workers configurations.

## Repository Structure

```
├── LICENSE
├── README.md
└── skills/
    └── cloudflare-cf/
        ├── SKILL.md                     # Skill specification and agent instruction set
        ├── agents/                      # Agent interface definitions
        │   └── openai.yaml
        ├── assets/                      # Workflow examples and CI templates
        │   ├── AGENTS.example.md
        │   └── github-actions-cf.yml
        ├── references/                  # Deep-dive guides and playbooks
        │   ├── authentication.md
        │   ├── capability-map.md
        │   ├── ci-cd.md
        │   ├── command-discovery.md
        │   ├── debugging.md
        │   ├── installation.md
        │   ├── resource-playbooks.md
        │   ├── sources.md
        │   ├── typed-config.md
        │   ├── version-drift.md
        │   ├── workers-lifecycle.md
        │   └── wrangler-migration.md
        ├── scripts/                     # Deterministic helper tools
        │   ├── cf_discover.py           # Command & documentation discovery
        │   ├── cf_doctor.py             # Secret-redacting environment report
        │   └── cf_guard.py              # Static command preflight
        └── tests/                       # Unit tests for helpers
            └── test_helpers.py
```

## Installation

### Via `skills` CLI
```bash
npx skills add DrB0rk/cloudflare-cf -g
```

### Manual / Symlink
Symlink or copy into your global skills directories:
```bash
# Agents standard skills directory
ln -s "/home/drb0rk/Projects/cloudflare-cf/skills/cloudflare-cf" ~/.agents/skills/cloudflare-cf

# OMP agent skills directory
ln -s "/home/drb0rk/Projects/cloudflare-cf/skills/cloudflare-cf" ~/.omp/agent/skills/cloudflare-cf

## Testing

Run unit tests for deterministic helpers:
cd skills/cloudflare-cf && python3 -m unittest discover tests

## License

[MIT](LICENSE) © 2026 DrB0rk
