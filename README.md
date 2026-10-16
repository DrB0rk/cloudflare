# Cloudflare — senior engineering skill for AI agents

[![skills.sh install count](https://skills.sh/b/DrB0rk/cloudflare)](https://skills.sh/DrB0rk/cloudflare)

A reusable Cloudflare platform engineering skill covering design, development, security, performance, operations and resource administration. It integrates Cloudflare's new cf CLI, existing Wrangler workflows, official documentation, Cloudflare connectors and Terraform/Pulumi without forcing a tool migration.

## Install

**Recommended:** Install the public `cloudflare` skill using the official [Skills CLI](https://skills.sh/docs/cli):

```bash
npx skills add DrB0rk/cloudflare --skill cloudflare
```

The installer selects a supported agent and an installation scope interactively. To install globally, target a particular agent, or inspect the public skill:

```bash
npx skills add DrB0rk/cloudflare --list
npx skills add DrB0rk/cloudflare --skill cloudflare -g
npx skills add DrB0rk/cloudflare --skill cloudflare --agent codex -g -y
```

To verify, run `npx skills list` for project installations or `npx skills list -g` for global installations. Restart your coding agent if needed; the Skills CLI manages the agent-specific directory. No manual symlinks or cloning are needed.

**skills.sh listing:** No submission form or special publishing command exists. Public skills become eligible for the [skills.sh directory](https://skills.sh/) through genuine installations with the `skills` CLI's optional anonymous telemetry. An installable repository is not necessarily indexed or visible in search immediately. Follow the [publishing guide](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context) and [FAQ](https://skills.sh/docs/faq). This is a community skill and is not affiliated with or endorsed by Cloudflare. Cloudflare API credentials are configured separately and are never required for the skill installation itself.

## What it teaches an agent

- **Architecture judgment:** choose Workers, Pages, Static Assets, D1, KV, R2, Durable Objects, Hyperdrive, Queues, Workflows, AI and private networking using latency, consistency, cost, availability and recovery requirements.
- **Security engineering:** least privilege, scoped API tokens, identity/access policies, WAF/DDoS/Bot/API Shield, TLS Full (strict), origin isolation, Turnstile validation, input security, tenant boundaries, prompt/tool injection protections and audit trails.
- **Production operations:** SLOs, observability, incident runbooks, CI/CD, staging/canary rollouts, IaC drift, migrations, rollback and FinOps.
- **Practical execution:** live cf command/schema/docs lookup; version-sensitive config verification; full verification after changes; preservation of existing Wrangler and IaC workflows.
- **Product catalog:** detailed product references across the existing Cloudflare families plus senior cross-cutting technical guides.

## Validate the installed skill

The install command above is the primary method; do not manually unpack or symlink this repository unless your agent does not support the Skills CLI. The installer should find exactly one skill named `cloudflare` (see [installation details](skills/cloudflare/references/installation.md)).

From the installed `cloudflare` directory reported by the CLI, run:

```bash
python3 scripts/skill_lint.py --root .
python3 -m unittest discover -s tests -v
```

These checks run offline. The [CI installation workflow](.github/workflows/skills-sh-discovery.yml) also tests genuine installs for Codex, Claude Code, and Pi and verifies all installed references and scripts.

Installing the skill does **not** install Cloudflare's separate `cf` CLI or authenticate to a Cloudflare account. Use Node.js >=22.18 and install `cf` separately when necessary; no Cloudflare API key is required for skill installation.
## Essential workflows

**Explore a Cloudflare architecture:** read SKILL.md -> references/decision-framework.md -> relevant product reference -> security-baseline.md -> production-delivery.md.

**Review a security posture:** references/security-baseline.md -> worker-security.md or zero-trust-security.md -> quality-gates.md. No automatic production mutations.

**Operate existing Workers:** identify cloudflare.config.ts vs wrangler.jsonc/toml and IaC ownership. For cf-ready projects:

    cf --version
    cf cli search "list D1 databases"
    cf docs search "D1 session read replication"

For Wrangler-only applications, keep existing Wrangler dev/build/deploy until deliberately migrated. For IaC-owned account resources, edit plan/apply through the IaC owner rather than creating hidden drift.

**Run local helper tests** (no Cloudflare credentials necessary):

    cd skills/cloudflare
    python3 -m unittest discover tests

## Organization

- skills/cloudflare/SKILL.md — agent control plane and task routing
- skills/cloudflare/references/ — architectural, security, operational and product-specific references
- skills/cloudflare/scripts/ — read-only discovery and advisory command diagnostics
- skills/cloudflare/tests/ — deterministic regression tests
- skills/cloudflare/assets/ — templates for working in repositories

## Truth and safety

This is an independent skill, not official Cloudflare documentation. Platform features, beta cf syntax, prices, limits, permissions, availability and security behavior may change. The agent must verify critical claims in official docs and installed CLI help, scope credentials, review blast radius, protect secrets and verify mutations. Advisory scripts do not grant permission to execute changes.

Core official references:
- https://developers.cloudflare.com/
- https://developers.cloudflare.com/cf/
- https://developers.cloudflare.com/cf/agents/
- https://developers.cloudflare.com/workers/best-practices/workers-best-practices/
- https://developers.cloudflare.com/fundamentals/api/get-started/

MIT license; see LICENSE.
