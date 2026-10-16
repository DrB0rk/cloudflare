# Cloudflare CLI policy for coding agents

When interacting with Cloudflare, prefer the new `cf` CLI for its public API and for project operations only when `cloudflare.config.ts` is present. Existing repositories with only `wrangler.json`, `wrangler.jsonc` or `wrangler.toml` must keep Wrangler for dev/build/deploy until the operator authorizes `cf migrate`; never auto-rewrite a Wrangler project.

Discover commands rather than guessing: `cf cli search "task"`, then `cf schema ...`, `<command> --help`, and (when applicable) `--dry-run`. Use `cf docs search "topic"` on beta.15+ for current Cloudflare documentation. Run `node --version` (22.18+ required) and `cf --version` before changing tooling. Use explicit account, zone, resource ID, Worker and mode. Review code/resource diffs; do not hide side effects behind `--force` or auto-provisioning.

Use named profiles for interactive project separation or scoped `CLOUDFLARE_API_TOKEN` + explicit `CLOUDFLARE_ACCOUNT_ID` in unattended CI. Do not disclose secrets. Treat a dry-run as a preview, not a deployment, and independently verify resulting resource state after any mutation. For missing live tail/single-secret commands, use Wrangler fallback deliberately with Worker name. Consult the installed `cloudflare-cf` skill and its version drift notes.
