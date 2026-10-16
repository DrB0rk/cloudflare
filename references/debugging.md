# Debugging, Local Explorer and observed output

## Decision tree

1. `cf --version` + `node --version` and project-type inspection first.
2. For **CLI syntax**, run `cf cli search`, `cf schema`, command `--help`; for product rules, `cf docs search` and official docs.
3. For **authorization**, test `cf auth whoami`, confirm `CLOUDFLARE_API_TOKEN` presence and account selection without exposing values.
4. For **project config**, inspect `cloudflare.config.ts`, `package.json`, `vite.config.ts`, `wrangler.config.ts`, `mode` and worker name.
5. For **local Worker execution**, prefer Local Explorer traces/logs and a reproducible request. For remote live logs, use `npx wrangler tail WORKER_NAME` while unsupported in `cf`.
6. For **deploy**, inspect `.cloudflare/output/v0/config.json` and the mode; confirm remote worker/version after deployment.

## Local Explorer API for coding agents

When `cf dev` uses the Cloudflare Vite plugin or Wrangler build tooling in an agent environment, the dev server may print an API hint such as:

```text
http://localhost:8787/cdn-cgi/local/explorer/api
```

This endpoint **serves the OpenAPI specification** for the available Local Explorer operations. Use it to discover actual paths/parameters rather than assume an undocumented shape:

```bash
curl http://localhost:8787/cdn-cgi/local/explorer/api
```

Typical capabilities: inspect local KV/R2/D1 bindings and data, Durable Object state, Workflow executions, correlated OpenTelemetry traces and console logs, and debug failing routes. The observability query endpoint is documented at `POST /cdn-cgi/local/explorer/api/local/observability/query` and supports SQL-based trace/log queries. Do not send raw credentials or production data into local debug prompts. Some endpoints mutate local state; require intent-specific approval even if the server is local.

**Crucial distinction:** `cf --local` resource commands may run separate short-lived Miniflare and store data in a shared `state/v3`; the Vite plugin keeps active local state in `.cloudflare/state/`. For debugging a running dev process, use the API URL actually printed by that server.

## Common errors and causes

| Symptom | Likely reason | Safe diagnostic |
| --- | --- | --- |
| `cloudflare.config.ts loading is not supported on Bun` | Running `cf` with Bun | Launch through Node >=22.18 |
| Node import errors with config | Wrong Node/version or package `type` | Check Node >=22.18, `"type":"module"`, local dependency |
| `Cannot resolve entry module index.html`, 404 in migrated-looking project | `cf` auto-config ran over Wrangler project | Inspect `git status`; restore only generated artifacts; migrate intentionally |
| `No Cloudflare dev-server is installed` | No recognized framework/build tool | Inspect package.json and `cf init` prerequisites |
| Unsupported `cf dev --port` | Framework command does not forward flags | Configure `vite.config.ts` or run framework command |
| `--mode` mismatch prebuilt | Build Output recorded another mode | Check `buildContext.mode` manifest, use exact mode |
| Missing Build Output on `--prebuilt` | `.cloudflare/output/v0/config.json` absent | Build or restore complete artifact |
| Multi-account noninteractive failure | No explicit account selection | Set `CLOUDFLARE_ACCOUNT_ID` securely |
| `--local` not implemented | Command isn't in supported subset | Use supported local equivalent or explicitly remote |
| `cf migrate` exit `1` with TODOs | Required migration follow-ups | Resolve typed config and remove protective throw after review |
| `cf docs search` unknown | CLI predates beta.15 | Pin/update after user approval or use official docs directly |
| Command renamed after update | Beta.16 kebab-case generator changes | Re-run `cf cli search`, inspect help; never hardcode old camelCase |
| Aborted noninteractive delete | Requires explicit confirmation/`--force` | Inspect version, review force semantics, verify remote state |

## Performance and observability

Use `cf workers check` to generate `worker-startup.cpuprofile`, local startup timings and bundle size, not a production latency guarantee. Treat prod telemetry sampling, Logpush, trace collection and cost limits separately.

Sources: https://developers.cloudflare.com/workers/local-development/local-explorer/ ; https://developers.cloudflare.com/cf/agents/ ; https://developers.cloudflare.com/cf/projects/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
