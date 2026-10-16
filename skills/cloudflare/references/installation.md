# Install the Cloudflare Skill

Use the official [Skills CLI](https://skills.sh/docs/cli) for supported coding agents. This is the same installation method documented in the repository README.

```bash
npx skills add DrB0rk/cloudflare --skill cloudflare
```

The CLI discovers `skills/cloudflare/SKILL.md` in the public GitHub repository and installs its complete directory. The skill is named **cloudflare**, not the former **cloudflare-cf**. Choose an agent and project/global installation scope when prompted.

## Supported installation options

```bash
# Global installation
npx skills add DrB0rk/cloudflare --skill cloudflare -g

# Noninteractive install for Codex (global)
npx skills add DrB0rk/cloudflare --skill cloudflare --agent codex -g -y

# List remotely available skills without installing
npx skills add DrB0rk/cloudflare --list

# Show project-installed or global-installed skills
npx skills list
npx skills list -g
```

Compatible coding-agent options include Codex, Claude Code and Pi. The Skills CLI determines their installation paths; do not assume every agent uses `~/.agents/skills` or manually unpack to outdated `cloudflare-cf` paths. Restart or reload the agent if needed.

## Verify the installed files

Locate the installed `cloudflare` directory displayed by the CLI. It must contain `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, and `tests/`. From inside that directory run:

```bash
python3 scripts/skill_lint.py --root .
python3 -m unittest discover -s tests -v
```

The checks do not require Cloudflare credentials or change remote resources. Continuous integration also performs genuine Skills CLI installs and runs tests against the installed copy.

## Skill versus Cloudflare CLI

Installing this skill **does not** install Cloudflare's `cf` CLI, deploy software or grant Cloudflare account access. To run new `cf` commands locally, install that CLI separately with Node.js >=22.18 (for the current beta):

```bash
node --version
npm install --global cf
cf --version
```

For interactive account access, a person may run `cf auth login`; for unattended workflows use scoped API tokens from a secrets manager. The skill also supports existing Wrangler/IaC setups and Cloudflare connectors without forcing a migration.

## Unsupported installers

If an environment (including ChatGPT skill uploads) cannot invoke the Skills CLI, package or copy the entire `skills/cloudflare/` directory using that environment's documented skill-loading mechanism. This is a fallback; do not package the repository root as the skill.

Sources: https://skills.sh/docs/cli ; https://github.com/vercel-labs/skills ; https://developers.cloudflare.com/cf/
