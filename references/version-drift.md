# Beta compatibility and documentation drift

Snapshot verified **2026-10-16**. The current inspected GitHub release list shows **`cf@1.0.0-beta.17`**, released 2026-10-14. Re-check https://github.com/cloudflare/cf/releases and `cf --version` for each new environment. Treat this file as a version-aware watchlist, not as proof that beta.17 is eternally latest.

## Changes that materially affect coding agents

| Release | Change | Agent implication |
| --- | --- | --- |
| beta.17 | Path parameter defaults, requiredness and positional placement now reflect `x-forge-params`. | Re-discover and inspect help/schema; don't rely on memorized positional ordering. |
| beta.16 | New Forge/WASM generator; ~42 commands change camelCase/snake_case to kebab-case, including `analytics-engine` and billing. | Syntax copied from older docs can fail. Always search. |
| beta.16 | Some formerly `--body`-only fields gained named flags and several enum constraints changed. | Inspect actual schema/help and dry-run. |
| beta.15 | `cf docs search "query"` added. Returns ranked live docs results without Cloudflare login. | Use doc search for product syntax/design; keep queries free of sensitive info. |
| beta.15 | **Noninteractive destructive commands now exit `1` when `--force` is missing**, rather than exiting successfully after abort. | Official September documentation still describes exit `0`. Version-aware; readback required regardless. |
| beta.15 | `CLOUDFLARE_DEPENDENCIES_INSTRUMENTATION=false` disables dependency metadata upload. | Use when deployment metadata collection must be disabled. |
| beta.15 | `cf dev --persist-to` explicitly rejected. | Avoid advice based solely on an advertised help flag. |
| beta.14 | `--dry-run` support for hand-written commands; request behavior may vary. | Confirm dry-run strategy rather than assuming one generic JSON schema. |
| beta.13 | `cf deploy --no-provision` prevents auto-creating resources from missing binding IDs. | Prefer for strictly managed infra/predictable production changes. |
| beta.13 | `cf tunnels quick-start --allowed-mail` email-restricted temporary tunnels; `cloudflared` >=2026.9.2 required. | Useful for safe temporary dev sharing. |
| beta.13 | `cf --version` writes parseable version to stdout. | Scripts can inspect version reliably on modern betas. |
| beta.13 | `cf deploy --dry-run` avoids unwanted project setup changes in setup-needed cases; local build/setup interactions remain possible. | Review local repository state even on dry-runs. |
| beta.13 | Sensitive fields marked in schema are redacted from generated dry-run previews. | Do not assume all custom values are redacted; keep output private. |
| beta.7 | Preserve existing Worker secrets on redeploy. | Do not assume behavior across older betas; verify before upgrading. |

## Explicit source conflict

As retrieved on 2026-10-16, Cloudflare's **Use cf with coding agents** (updated 2026-09-29) and **Use cf in CI** docs say a noninteractive destructive command without `--force` can print `Aborted.` and exit **0**. The GitHub `cf@1.0.0-beta.15` changelog explicitly says this was changed to exit **1**. **The versioned code changelog is newer**; the agent must not use `exit == 0` or `exit == 1` as evidence of a deletion. It must verify remote state after the mutation and inspect the installed version.

## Maintenance protocol

At the start of any Cloudflare maintenance request:

1. Capture `cf --version` and local Node version.
2. Check GitHub releases for changes since installed version.
3. Run `cf cli search "task"`; run `cf docs search "topic"` where available; inspect schema/help.
4. Revise playbooks only if verified. Distinguish docs/changelog facts from locally executed/tested behaviors.
5. For migrations and large deployments, pin the project version and test a staging release before upgrading to latest beta.

Official changelog: https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md ; releases: https://github.com/cloudflare/cf/releases ; docs: https://developers.cloudflare.com/cf/agents/ and https://developers.cloudflare.com/cf/ci/
