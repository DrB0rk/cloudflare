# Workers development and deployment lifecycle with `cf`

## Table of contents
1. New/existing projects
2. Build system and artifacts
3. Modes, environments and preview
4. Deploy / version and traffic
5. Type generation and profiling
6. Local resource data
7. Common traps

## 1. New or existing projects

`cf init my-worker` creates a new Worker project containing `cloudflare.config.ts`, `vite.config.ts`, source entrypoint, TypeScript configuration, package metadata and gitignore. `cf init .` configures the current directory. Use `cf init .` for an existing supported framework project **only after confirming it is not a Wrangler-configured project**.

`cf init ... --package-manager npm` chooses a manager; `--no-install` creates files without package installation. A new empty project normally includes `cf` as a dev dependency; type declaration generation may run after dependency installation. See `cf init --help` for the installed release.

Check file diffs before invoking `cf init` because it writes to the repository. A noninteractive `cf dev`, `cf build`, or `cf deploy` can trigger automatic configuration in projects lacking `cloudflare.config.ts`; this may install packages and modify `package.json`, lockfiles, `vite.config.ts` and other files. In a Wrangler project this can ignore real Worker bindings.

## 2. Build delegates / Build Output

`cf` orchestrates development/build. It does **not** contain its own dev server/bundler. It selects:

1. A supported framework's own dev/build command (e.g. Vite or Astro, via configured package manager), or
2. the Cloudflare build tool declared in package dependencies (`@cloudflare/vite-plugin@beta`, or Wrangler **4.136.0+** as supported backing tool).

Cloudflare Vite plugin **2.0 beta** reads `cloudflare.config.ts`. Wrangler-backed migrations have experimental `wrangler.config.ts` for build-only settings.

`cf build` writes **`.cloudflare/output/v0/`**, with a `config.json` manifest, and validates it. It does not upload and needs no Cloudflare credentials. `cf deploy` builds, validates, resolves credentials/account, creates a Worker Version, and deploys.

**Important:** `cf` does not run `package.json`'s `build` script on its own; a script like `tsc -b && vite build` will **not** have its type-check step run automatically. Chain it yourself:

```json
{"scripts": {"build": "tsc -b && cf build", "typecheck": "cf workers types && tsc --noEmit"}}
```

Framework delegation only forwards `--mode` in many cases. `cf dev --port 8788` can fail for Vite; configure Vite's `server.port` or invoke `vite` directly. `cf dev --persist-to` is rejected as unsupported (beta.15 fix) even if help mentions it.

## 3. Modes, staging and previews

Wrangler `--env staging` is **not** the same as `cf --mode staging`. Use function-form `defineConfig(({ mode, isPreview }) => ...)` to return one fully specified Worker configuration for each mode. Modes do not merge inherited environment blocks by default.

```bash
cf dev --mode staging
cf build --mode staging
cf deploy --mode staging
```

When omitted, Vite defaults to `development` for dev and `production` for builds; Wrangler-backed builds may leave mode undefined. To deploy prebuilt output, use exactly the mode recorded in `.cloudflare/output/v0/config.json` at `buildContext.mode`.

```bash
cf build
cf deploy --prebuilt --mode production --dry-run
# After authorized review:
cf deploy --prebuilt --mode production
```

If the manifest does not record a mode, omit `--mode` on prebuilt deployment. `--prebuilt` bypasses automatic configuration and build; it does not suppress remote deployment.

`cf previews deploy [preview-name]` produces an isolated Worker Preview (defaults to branch name when known), with `isPreview:true` in the config. It **requires credentials** and **does not offer `--dry-run`** as documented. Determine naming explicitly in detached HEAD CI. Container-backed previews have stated limitations in the beta. Inspect the result's JSON URLs and IDs.

## 4. Deploy, versions and traffic

```bash
cf deploy --dry-run                                  # builds and validates, no API upload
cf deploy --no-provision                             # prevent missing-binding auto-provisioning
cf deploy --message 'fix request parsing' --tag v1.2.0
cf deploy --secrets-file /secure/private/secrets.env  # do not print or commit the file
cf deploy --containers-rollout gradual               # explicit rollout strategy
cf workers versions create --dry-run                 # build/validate; upload only without --dry-run
cf workers triggers deploy --dry-run                 # validate triggers; no API calls in dry run
```

Without `--no-provision`, `cf deploy` may provision missing resources for bindings without IDs; it does **not** write IDs back into `cloudflare.config.ts`. For production pipelines, favor `--no-provision` and explicitly managed infrastructure unless auto-provisioning is part of the authorized design.

A Worker Version is not the same as an active Deployment. `cf workers versions create` uploads a Version but does not deploy it. Use `cf workers deployments create` to allocate traffic percentages, verifying percentages and Worker IDs with current help/schema:

```bash
cf workers deployments create --worker example-worker --strategy percentage --versions '[{"version_id":"VERSION_ID","percentage":100}]'
```

`cf workers triggers deploy` applies routes, domains, `workers.dev`, cron schedules, Queue consumers and Workflows from Build Output without uploading new code. Treat this as production infrastructure mutation.

`--worker <NAME>` selects one Worker from multi-Worker Build Output. `--dispatch-namespace` is supported for Workers for Platforms. `--secrets-file` supports JSON or `.env` formats in deploy/version creation.

## 5. Types and startup profiling

`cf workers types` derives `.cloudflare/types/index.d.ts`, including `Env` bindings and Workers runtime. Use `--no-include-runtime` when you need to omit runtime types and `--mode` to generate types for a particular mode. Vite plugin normally generates the file during development/build; Wrangler-backed projects may require explicit type generation.

`cf workers check` builds (or reads `--prebuilt`) and reports local Worker bundle size and startup timings in JSON, plus a `worker-startup.cpuprofile`. The numbers are **local performance measurements**, not Cloudflare production execution latency. `--outfile PATH` chooses the profile path.

## 6. Local state via `--local`

The CLI normally operates on *remote* resources. Supported local commands (as of documentation check):

- `cf kv keys get|list|put|delete`; `cf kv bulk get|put|delete`.
- `cf d1 raw`, `cf d1 migrations list`, `cf d1 migrations apply`.
- `cf r2 objects get|put|list|bulk-delete`.
- Some local list metadata: `cf d1 list`, `cf kv namespaces list`, `cf r2 buckets list`.

Not supported: `cf d1 query --local` (use `cf d1 raw ... --local`). Local data defaults to a shared `state/v3` under the `cf` configuration directory; `--persist-to DIRECTORY` is supported on certain `--local` API commands to isolate this state. This **is not the same store** as the Vite plugin's `.cloudflare/state/` for an active dev server. For live local Worker data, use the Local Explorer API described in `references/debugging.md`.

## 7. Deployment checklist

- [ ] Correct repository root, project type, Git baseline, lockfile and Node version.
- [ ] Correct `accountId`, Worker name, routes, domains and mode.
- [ ] Required binding names/IDs, intended provisioning behavior, secret preservation.
- [ ] Test/build/typecheck successful; intended Build Output version and mode recorded.
- [ ] Dry-run reviewed (not assumed entirely local-side-effect-free).
- [ ] Explicit approval for production traffic change.
- [ ] Deploy executed and remote Worker version, routes, triggers and health verified.
- [ ] Rollback target/version recorded.

Sources: https://developers.cloudflare.com/cf/projects/ ; https://developers.cloudflare.com/cf/projects/cloudflare-config/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
