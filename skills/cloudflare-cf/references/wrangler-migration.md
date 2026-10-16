# Wrangler coexistence, migration, and incompatible commands

## Zero-regression rule

**If there is a `wrangler.json`, `wrangler.jsonc`, or `wrangler.toml` and no `cloudflare.config.ts`, do not run `cf dev`, `cf build`, `cf deploy`, `cf init .`, `cf previews deploy` or other build-backed `cf` project commands.** Automatic setup does not read Wrangler configuration and can generate a static site or replacement Worker without existing bindings, or fail.

Use existing Wrangler project commands (`wrangler dev`, `wrangler deploy`, etc.) and `cf` **resource/API** operations safely side by side. In an unmigrated project, `cf` does not read Wrangler's `account_id`: set account explicitly.

## Differences to understand

| Concern | Wrangler | `cf` |
| --- | --- | --- |
| Tool focus | Workers + subset of products | public Cloudflare API + Workers project orchestration |
| Project config | `wrangler.jsonc`, `wrangler.toml` | typed `cloudflare.config.ts` |
| Auth | Wrangler OAuth | independent `cf auth` OAuth profiles or API token |
| Environments | `--env` configuration merge | `--mode` complete function-generated config |
| Remote/local | product command dependent | remote by default; `--local` supported on narrow subset |
| Build output | Wrangler artifact | `.cloudflare/output/v0/` specification |
| Resource identifiers | often friendly names | often API IDs |
| Underlying build | Wrangler | Vite plugin beta or Wrangler 4.136.0+ in migrated project |

## Safe migration procedure (only when requested)

1. Inventory all Worker triggers, routes/domains, secrets, service bindings, D1/KV/R2/Queues, DO migrations, Workflows, Containers and CI secrets. Identify deployment and rollback targets.
2. Use Node >=22.18, install `cf` globally/locally, and install current project dependencies. With Wrangler bundling, require **Wrangler >=4.136.0**.
3. Commit or stash **all tracked and untracked** work: `cf migrate` refuses a dirty worktree (unless `--force`, which should not be a default).
4. Run `cf migrate --dry-run` in the directory with exactly one Wrangler file, or `cf migrate path/to/wrangler.jsonc --dry-run`. **A dry run can exit `1` if required follow-ups exist**; read the output.
5. Let `cf` select the current bundler (Vite if declared, otherwise Wrangler) unless user specifically wants a bundler change. If choosing Vite intentionally, install compatible `@cloudflare/vite-plugin@beta` and `vite`, update `vite.config.ts`, and move build settings. Vite `configPath` option may need removal.
6. Run `cf migrate [path]`. It generates `cloudflare.config.ts`, sometimes `wrangler.config.ts`, and adds a local `cf` dependency; it retains original Wrangler config. It does not necessarily update package scripts, sources or tsconfig.
7. Check `git status` and `git diff`. Resolve every generated **`TODO(@cloudflare)`** (especially DO lifecycle/migrations, Workflows, Containers and package scripts) before deleting the protective `throw new Error("Migration incomplete...")`.
8. Run typecheck/tests, `cf workers types`, `cf build` and `cf deploy --dry-run`; compare final Worker name, bindings, routes, triggers and source code with old configuration.
9. Stage and verify before approved production deployment. Do not remove Wrangler config while any fallback Wrangler commands still need it.

`cf migrate --force` bypasses the *dirty Git worktree* check only; it cannot overwrite existing `cloudflare.config.ts` or the required `wrangler.config.ts` when they exist. The migration can write files and return exit `1` due to required follow-ups; this is **not** the same as complete failure.

### Examples of manual conversions

- `main` → `worker.entrypoint` (path or `cf-worker` import).
- `name` → `worker.name`, `compatibility_date` → `worker.compatibilityDate`, `account_id` → top-level `accountId`.
- `vars`, `d1_databases`, `kv_namespaces`, `r2_buckets`, queues and services → builders inside `worker.env`.
- `triggers.crons`, routes, queue consumers → `worker.triggers` with `triggers.scheduled`, `.fetch`, `.queue`.
- `env` blocks → function-form `defineConfig(({mode}) => ...)`; no implicit inheritance.
- Durable Object `migrations` → new `exports` lifecycle declaration (manual and state-sensitive).
- Vite build settings → `vite.config.ts`; Wrangler-backed build settings → generated `wrangler.config.ts`.

## Commands still requiring Wrangler (as of beta.17)

```bash
npx wrangler tail WORKER_NAME
npx wrangler secret put SECRET_NAME --name WORKER_NAME
```

The `cf` CLI cannot yet stream live logs or set one secret directly as documented. Alternative for version-wide secrets: `cf deploy --secrets-file PATH` or `cf workers versions create --secrets-file PATH`. Wrangler does **not** read `cloudflare.config.ts`; it needs an appropriate Wrangler config or explicit Worker name. Check the latest mapping at https://developers.cloudflare.com/cf/wrangler/reference/ before treating this list as exhaustive.

## Common failure recovery

If an agent accidentally ran build-backed `cf` commands in an unmigrated project: inspect `git status`, identify newly created files and changed scripts. Restore *only* changes caused by the command (don't delete legitimate user files), then run the controlled migration. Verify old Worker code and bindings are still present. Never assume a successful `cf build` in this state means the correct Worker was built.

Sources: https://developers.cloudflare.com/cf/wrangler/ ; https://developers.cloudflare.com/cf/wrangler/migrate/ ; https://developers.cloudflare.com/cf/wrangler/reference/
