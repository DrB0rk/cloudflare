# Typed `cloudflare.config.ts` and binding configuration

## 1. Contract

The new `cloudflare.config.ts` is a **TypeScript module**, not a JSON/TOML rewrite. It is loaded by `cf`, including many API commands that need only account settings. Set `"type": "module"` in `package.json`, use Node **22.18+**, and install `cf` as a local devDependency so `cf/config` can resolve.

It is currently a **beta API**; load the installed `cf/config` TypeScript declaration and https://developers.cloudflare.com/cf/projects/config-explorer/ before editing advanced fields.

Top-level `defineConfig(...)` supports `accountId`, `complianceRegion`, `worker`, `containers`. It accepts a plain object, promise or context function (`mode`, `isPreview`), enabling typed dynamic configuration. `defineWorker()` and `defineContainer()` allow reusable definitions; the default export remains `defineConfig()`.

## 2. Minimal verified syntax

```ts
import { defineConfig } from "cf/config";
import * as entrypoint from "./src/index.ts" with { type: "cf-worker" };

export default defineConfig({
  worker: {
    name: "example-worker",
    entrypoint,
    compatibilityDate: "2026-10-01",
  },
});
```

A **file path** string is also allowed as `entrypoint`, e.g. `"src/index.ts"`. The special `cf-worker` import attribute enables richer type inference.

`compatibilityDate` is **an example**: choose and validate a runtime date appropriate for the real project. An assets-only Worker can omit `entrypoint`, but the build must provide static assets.

## 3. Mode-sensitive configuration (sample)

```ts
import { bindings, defineConfig, triggers } from "cf/config";
import * as entrypoint from "./src/index.ts" with { type: "cf-worker" };

export default defineConfig(({ mode, isPreview }) => {
  const staging = mode === "staging" || isPreview;
  return {
    // Prefer a project-scoped accountId or CLOUDFLARE_ACCOUNT_ID at runtime.
    worker: {
      name: staging ? "orders-api-staging" : "orders-api",
      compatibilityDate: "2026-10-01",
      entrypoint,
      env: {
        APP_ENV: bindings.text(staging ? "staging" : "production"),
        FEATURES: bindings.json({ search: true }),
        DB: bindings.d1({ name: staging ? "orders-staging" : "orders-production" }),
        JOBS: bindings.queue({ name: staging ? "orders-jobs-staging" : "orders-jobs" }),
        API_KEY: bindings.secret(),
      },
      triggers: [triggers.scheduled({ schedule: "0 * * * *" })],
    },
  };
});
```

This is a **pattern**, not permission to deploy: `bindings.d1({name:...})` can enable automatic provisioning; consider explicitly providing IDs and `cf deploy --no-provision`. Secrets are declared in config but values belong in protected sources, never the file. Mode functions return a **complete** configuration; they do not inherit an `env` block from another mode.

## 4. Important configuration families

| Concern | Config surface | Notes |
| --- | --- | --- |
| Worker identity/runtime | `worker.name`, `worker.entrypoint`, `worker.compatibilityDate`, `worker.compatibilityFlags` | Worker name and date are required for executed code |
| Environment and bindings | `worker.env` via `bindings.*` | typed text/json/secret/D1/KV/R2/Queues/DO/service/workflow bindings; verify exact builder signatures |
| Routing and scheduling | `worker.triggers` via `triggers.fetch`, `.scheduled`, `.queue`, `.email`, `.connect` | Distinguish domain/route and trigger mutation |
| Custom domains | `worker.domains` | May affect production traffic |
| Named exports | `worker.exports` via `exports.*` | DO/Workflow exports and storage lifecycle; not legacy `migrations` |
| Observability | `worker.observability`, `worker.logpush`, `worker.tailConsumers` | Configure logs, traces, sampling |
| Performance/security | `worker.limits`, `worker.placement`, `worker.cache` | Platform features may vary by product and plan |
| Assets | `worker.assets` | Controls **runtime** behavior; not a Wrangler `assets.directory` copy |
| Containers | Top-level `containers` with `defineContainer` | DO-managed Containers need lifecycle bindings and review |
| Auth/account | Top-level `accountId`, `complianceRegion` | API commands can use an account-only config export |

`bindings.worker()` / `bindings.durableObject()` / `bindings.workflow()` may reference typed Worker definitions to validate exported names at compile time.

**Static assets:** in Vite projects, source assets are built via Vite (`publicDir`, typically `public`). With a Wrangler-backed bundler, build settings are in generated `wrangler.config.ts`. There is no direct `assets.directory` field on `cloudflare.config.ts`.

**Durable Objects:** Wrangler legacy `migrations` arrays do not automatically map. Modern lifecycle definitions use `worker.exports` plus `exports.durableObject({storage: "sqlite"})` patterns; consult the installed type and official migration guide before editing an existing DO deployment. Never erase an active DO migration history to satisfy a type check.

## 5. Validation

1. Inspect local installed `cf/config` API via editor/TypeScript and configuration explorer.
2. `cf workers types` for binding inference.
3. `npm run typecheck` if available and the project's tests.
4. `cf build --mode staging`; inspect output and config manifest.
5. `cf deploy --dry-run --mode staging --no-provision` when help supports all flags and correct project config is present.
6. Apply only with approval and verify resulting Worker ID, routes and dependencies.

Sources: https://developers.cloudflare.com/cf/projects/cloudflare-config/ ; https://developers.cloudflare.com/cf/projects/config-explorer/ ; https://developers.cloudflare.com/cf/wrangler/migrate/
