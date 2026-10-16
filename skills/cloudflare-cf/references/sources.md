# Primary sources and audit trail

Checked **2026-10-16**. This skill is an independently compiled operational guide and is not a Cloudflare-published package. Favor primary vendor docs, current CLI output, and the live release changelog over bundled examples.

## Stable discovery entry points

- Main documentation: https://developers.cloudflare.com/cf/
- Documentation index for agents: https://developers.cloudflare.com/cf/llms.txt
- Full Cloudflare CLI docs as machine-readable text: https://developers.cloudflare.com/cf/llms-full.txt
- GitHub CLI source: https://github.com/cloudflare/cf
- CLI release list: https://github.com/cloudflare/cf/releases
- CLI version history/changelog: https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
- Official Cloudflare skill (comparison/baseline): https://github.com/cloudflare/skills/blob/main/skills/cf-cli/SKILL.md
- Launch announcement (2026-09-28): https://blog.cloudflare.com/cloudflare-cf-cli-launch/

## Task-specific documentation

- Install, OAuth, profiles/account/zone scopes, `.env`: https://developers.cloudflare.com/cf/get-started/
- First Worker / init: https://developers.cloudflare.com/cf/get-started/first-worker/
- Resource commands and DNS example: https://developers.cloudflare.com/cf/get-started/resources/
- `cf` for coding agents, schema, output, local Explorer: https://developers.cloudflare.com/cf/agents/
- Project dev/build/deploy, modes, Build Output, local subset: https://developers.cloudflare.com/cf/projects/
- Programmatic `cloudflare.config.ts`: https://developers.cloudflare.com/cf/projects/cloudflare-config/
- Type/config explorer: https://developers.cloudflare.com/cf/projects/config-explorer/
- Wrangler comparison: https://developers.cloudflare.com/cf/wrangler/
- Migration and manual follow-ups: https://developers.cloudflare.com/cf/wrangler/migrate/
- Command/config mapping and missing Wrangler functionality: https://developers.cloudflare.com/cf/wrangler/reference/
- CI with API tokens, prebuilt artifact: https://developers.cloudflare.com/cf/ci/
- Environment variables: https://developers.cloudflare.com/cf/environment-variables/
- Agent Local Explorer OpenAPI: https://developers.cloudflare.com/workers/local-development/local-explorer/

## Evidence levels

1. **Live CLI verified**: a real `cf --version`, search/schema/help/dry-run/remote get confirmed against the user's installed tool and account.
2. **Versioned upstream**: current release or linked changelog describes the behavior; may conflict with older docs.
3. **Official docs**: published guidance and examples, may lag current prerelease.
4. **Skill patterns**: examples and agent guardrails bundled here; not a claim they ran against Cloudflare.

**Current build testing boundary:** this archive's Python helper scripts can be executed in a standard local Python environment. The build environment used to author the skill did not have a runnable `cf` installation (Node was below 22.18 and network package installation was unavailable), so no live API operations, CLI search requests or end-to-end deployments were performed. Validate installed CLI behavior before using it to modify resources.
