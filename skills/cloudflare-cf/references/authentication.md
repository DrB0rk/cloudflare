# Authentication, profiles, scope and environment

## 1. Requirements

- Node.js **22.18+** (not merely Node 22.0); running the CLI under Bun is unsupported when `cloudflare.config.ts` loads.
- Install globally `npm install --global cf`. The package provides `cf` **and** `cloudflare` executables. `cloudflare` is an alternative if `cf` conflicts on PATH.
- In a project, prefer an exact/lockfile-pinned `cf` devDependency. The global `cf` delegates to the project version.
- Check `cf --version`. For signed-in calls, check `cf auth whoami`; do not print or capture secrets.

## 2. Credential resolution precedence

1. `CLOUDFLARE_API_TOKEN` in process environment or a supported current-directory `.env`.
2. Named OAuth profile supplied via `--profile NAME`.
3. Nearest directory-bound OAuth profile from `cf auth activate`.
4. Default OAuth profile set by `cf auth login`.

A token **overrides** all profiles. If `cf auth activate`/`deactivate`/`create`/`delete` fails unexpectedly, first check whether `CLOUDFLARE_API_TOKEN` is set (check presence only). `cf` does **not** reuse Wrangler's OAuth login and does **not** support the Global API Key.

### Interactive profile commands

```bash
cf auth login                  # browser+one-time code, human approval
cf auth login --no-browser     # SSH/container, still requires human approval
cf auth login --force          # sign in again
cf auth whoami
cf auth list
cf auth create personal
cf auth create work
cf auth activate work          # bind to current directory and descendants
cf auth activate personal /path/to/project
cf auth deactivate            # unbind current directory
cf auth delete work
cf auth logout
cf --profile personal zones list
```

`cf auth activate` binds to a directory and descendants, useful for multi-tenant agencies/consultancies. Bind per-project profiles; don't rely on whichever profile happened to be active in another working directory. Avoid deleting or logging out profiles without user instruction.

## 3. Account selection precedence

1. `CLOUDFLARE_ACCOUNT_ID` environment variable.
2. `accountId` in nearest `cloudflare.config.ts` default export.
3. Previously chosen account stored for project.
4. Only accessible account, or interactive account selection; **noninteractive multi-account selection fails** if ambiguous.

Account selection may be cached in `.cache/cloudflare/` inside nearest `node_modules/`, otherwise `.cloudflare/cache/` in current directory. Cache files may be profile-specific. Prefer explicit environment account ID rather than relying on cache in scripts/CI. Do not guess or clear caches as a standard repair.

Zones: pass `--zone example.com` or `--zone ZONE_ID`; this overrides `CLOUDFLARE_ZONE_ID`. For dry-run requests use zone **ID** when you need an accurate API URL; no domain lookup is performed during dry-run.

## 4. `.env` and injected credentials

API commands read a `.env` in the current directory, not `.env.local`, `.env.production`, or other mode-specific files. OS-level environment variables take precedence over `.env`. `--local` resource commands do not load `.env`; build-backed deploy commands load `.env` after build.

Relevant `.env` keys include `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_ZONE_ID`, `CLOUDFLARE_COMPLIANCE_REGION`, `CLOUDFLARE_ACCESS_CLIENT_ID`, `CLOUDFLARE_ACCESS_CLIENT_SECRET`.

Never commit `.env`, backup copies, raw auth responses, CLI token dumps or cached OAuth material. CI uses its native secret store and a narrow account-scoped token; prefer separate tokens for development, staging and production.

## 5. Additional CLI environment configuration

| Variable | Effect |
| --- | --- |
| `CF_SEND_TELEMETRY=false` or `DO_NOT_TRACK=1` | Disable CLI telemetry; `DO_NOT_TRACK` takes precedence |
| `CF_QUIET=1` | Disable animated progress, not command JSON results |
| `CF_NO_OSC_PROGRESS=1` | No OSC progress title/taskbar integration |
| `CI=true` | Noninteractive behavior/prompt defaults |
| `DEBUG=...` | Verbose diagnostic/stack traces; avoid with credentials in logs |
| `CLOUDFLARE_API_BASE_URL` | Override target API endpoint; **never set to an untrusted host**: credentials are sent to it |
| `CLOUDFLARE_COMPLIANCE_REGION` | `public`, `fedramp-high`, `fedramp_high` |
| `CLOUDFLARE_REGISTRY_PATH` | Local development registry path shared with toolchain |
| `CLOUDFLARE_DEPENDENCIES_INSTRUMENTATION=false` | Beta.15+ turn off dependency metadata uploads on deploy/version creation |

Before saying telemetry is disabled, check effective environment and CLI settings. The command `cf telemetry disable` persists a preference locally.

## 6. Unattended agents

- Don't automate interactive OAuth by reading one-time codes; user approves the login.
- Supply **only** `CLOUDFLARE_API_TOKEN` + exact `CLOUDFLARE_ACCOUNT_ID` and sometimes `CLOUDFLARE_ZONE_ID`, via secure CI secret environment.
- Confirm that credentials are for the intended account with read-only calls before any mutation.
- Avoid printing `env`, `printenv`, raw auth files, tokens or API request headers to a shared log.

Sources: https://developers.cloudflare.com/cf/get-started/ ; https://developers.cloudflare.com/cf/ci/ ; https://developers.cloudflare.com/cf/environment-variables/
