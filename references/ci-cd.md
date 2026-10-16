# CI/CD, reproducibility and permissions

## Principles

- Run with **Node.js >=22.18**, not Bun.
- Install `cf` as a local devDependency and commit lockfile to pin the release (global `cf` delegates to project-installed copy).
- Use a project already configured with `cloudflare.config.ts`, not automatic configuration in CI. For Wrangler projects, migrate explicitly first or keep using Wrangler build/deploy.
- Supply narrowly scoped `CLOUDFLARE_API_TOKEN` and explicit `CLOUDFLARE_ACCOUNT_ID` through CI secrets **only to the stage that changes remote resources**; never expose to untrusted fork PRs.
- Build once, validate, then deploy the **same** `.cloudflare/output/v0/` artifact. Match `--mode` recorded in Build Output.
- Keep production deployment authorization tied to branch/environment protection and approvals. A success exit code isn't a remote health check.
- Avoid accidental provisioning via `--no-provision` when infrastructure is separately managed; pre-create named resources and bind stable identifiers.

## Example GitHub Actions pipeline

Copy and adapt `assets/github-actions-cf.yml` to `.github/workflows/cloudflare.yml`. The example is deliberately scoped to one Worker with npm and production Vite mode. The `push` step that deploys should use a protected branch/environment and verified account.

```yaml
name: Cloudflare Worker
on:
  pull_request:
  push:
    branches: [main]
jobs:
  worker:
    runs-on: ubuntu-latest
    env:
      CF_SEND_TELEMETRY: "false"
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: '22.18.0'
          cache: npm
      - run: npm ci
      - run: npx cf build
      - run: npx cf deploy --prebuilt --mode production --dry-run
      - if: github.event_name == 'push'
        run: npx cf deploy --prebuilt --mode production --no-provision
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

This is a **template**, not a workflow activated by installing the skill. Review `--no-provision` availability on pinned CLI, minimum permissions for the actual bindings, worker metadata and trigger requirements before enabling production deployment.

## Secrets and noninteractive behavior

`cf auth login` requires a human browser approval and must not be used in CI. If credentials can see multiple accounts without explicit account selection, noninteractive `cf` fails. For account/zone resource jobs, set both account and zone explicitly.

**Documentation drift warning:** official CI docs previously described unattended declined deletes returning code `0`, but the `cf@1.0.0-beta.15` changelog changes that to exit `1`. Neither outcome verifies a delete. For destructive jobs, always fetch/read back the remote state and keep a narrowly scoped decision gate.

## Production rollback

For Worker code deploy, record the prior active Worker Version/deployment IDs and preserve the last known good Build Output; plan a `cf workers deployments create` strategy based on the current API schema. For DNS, WAF, and security policies, export the exact existing document before applying a change. For data mutation, take a tested restore point when feasible.

Sources: https://developers.cloudflare.com/cf/ci/ ; https://developers.cloudflare.com/cf/projects/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
