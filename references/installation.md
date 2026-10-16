# Installing the skill in coding agents

This ZIP contains one reusable `cloudflare-cf` skill directory. It does **not** install the Cloudflare CLI or authenticate you. Use Node.js **22.18+** and `npm install --global cf` separately, then approve `cf auth login` as a human, or configure a scoped API token for unattended use.

## ChatGPT Skills

Upload the provided `skill.zip` through the ChatGPT Skills interface (or your workspace's skill upload mechanism). The skill package includes `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/` and `assets/`. Access to a real terminal and installed `cf` must be available for command execution; in connector-only chats, retrieval/analysis may be possible but locally executing this CLI is not guaranteed.

## Claude Code

Unpack the `cloudflare-cf` folder to `~/.claude/skills/cloudflare-cf/` or the project's `.claude/skills/cloudflare-cf/`. Optionally copy `assets/AGENTS.example.md` Cloudflare instructions into `CLAUDE.md` after review.

## Codex

Unpack to `~/.codex/skills/cloudflare-cf/` (or a supported project skill location). Agent tool permissions must allow safe `cf` invocations and prevent unsupervised production changes. Merge the included generic instructions into `AGENTS.md`.

## Pi / oh-my-pi / OMP

Unpack to `~/.pi/agent/skills/cloudflare-cf/` (Cloudflare's agent-skills repository documents this Pi directory). OMP wrappers may change skill paths and enable/disable auto-discovery; verify in the **installed** OMP version rather than assuming identical loading. Keep the Cloudflare CLI accessible on OMP's process PATH and do not include API keys in project agent instructions.

## OpenCode

Unpack to `~/.config/opencode/skills/cloudflare-cf/` (as documented by Cloudflare's skills repository); follow your installed tool's skill-loading conventions.

## Generic AGENTS.md instruction

Copy or adapt `assets/AGENTS.example.md` into user- or project-level agent instructions. Important point: do not install Wrangler in a new `cf` project, and do not run build-backed `cf` commands on an unmigrated Wrangler project.

## Test after installation

```bash
node --version
npm install --global cf
cf --version
cf cli search "list DNS records"
cf docs search "how to configure a Worker"
python3 scripts/cf_doctor.py --cwd .
python3 scripts/cf_discover.py "create a D1 database" --inspect
python3 -m unittest discover -s tests -v
```

`cf cli search` does not need credentials. `cf docs search` requires external documentation lookup but not Cloudflare OAuth. Running the helpers with `--inspect` only calls read-only command/schema/help introspection.

Reference directory guidance: https://github.com/cloudflare/skills ; https://developers.cloudflare.com/cf/agents/
