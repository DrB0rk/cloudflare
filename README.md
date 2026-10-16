# Cloudflare — senior engineering skill for AI agents

[![skills.sh install count](https://skills.sh/b/DrB0rk/cloudflare)](https://skills.sh/DrB0rk/cloudflare)

A reusable Cloudflare platform engineering skill covering design, development, security, performance, operations and resource administration. It integrates Cloudflare's new cf CLI, existing Wrangler workflows, official documentation, Cloudflare connectors and Terraform/Pulumi without forcing a tool migration.

## Install with the Skills CLI

Install the public, independently maintained `cloudflare` skill from this repository:

```bash
npx skills add DrB0rk/cloudflare --skill cloudflare
```

To inspect discovery before installation or install across projects:

```bash
npx skills add DrB0rk/cloudflare --list
npx skills add DrB0rk/cloudflare --skill cloudflare -g
```

**skills.sh listing:** No submission form or special publishing command exists. Public skills become eligible for the [skills.sh directory](https://skills.sh/) through genuine installations with the `skills` CLI's optional anonymous telemetry. An installable repository is not necessarily indexed or visible in search immediately. Follow the [publishing guide](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context) and [FAQ](https://skills.sh/docs/faq). This is a community skill and is not affiliated with or endorsed by Cloudflare. Cloudflare API credentials are configured separately and are never required for the skill installation itself.

## What it teaches an agent

- **Architecture judgment:** choose Workers, Pages, Static Assets, D1, KV, R2, Durable Objects, Hyperdrive, Queues, Workflows, AI and private networking using latency, consistency, cost, availability and recovery requirements.
- **Security engineering:** least privilege, scoped API tokens, identity/access policies, WAF/DDoS/Bot/API Shield, TLS Full (strict), origin isolation, Turnstile validation, input security, tenant boundaries, prompt/tool injection protections and audit trails.
- **Production operations:** SLOs, observability, incident runbooks, CI/CD, staging/canary rollouts, IaC drift, migrations, rollback and FinOps.
- **Practical execution:** live cf command/schema/docs lookup; version-sensitive config verification; full verification after changes; preservation of existing Wrangler and IaC workflows.
- **Product catalog:** detailed product references across the existing Cloudflare families plus senior cross-cutting technical guides.

## Agent-specific installation

The installable entrypoint is **skills/cloudflare/SKILL.md**. Do not install the repository root as a skill; install the directory containing SKILL.md.

The Skills CLI command at the top of this README is the recommended installation method. Select project or global scope in the installer. To verify after installation, use `npx skills list` (project) or `npx skills list -g` (global). Manual symlinks are only a fallback:

    ln -s /path/to/cloudflare/skills/cloudflare ~/.agents/skills/cloudflare

For ChatGPT, package the **skills/cloudflare/** directory as one skill ZIP using a validator before upload. See your agent's local skill setup instructions; folder names and discovery conventions differ between runtimes.

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
