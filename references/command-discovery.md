# Agent command discovery, schema, payloads and output

## Purpose and method

Generated CLI commands are derived from Cloudflare's public OpenAPI. A documentation example may predate a package release. On every nontrivial operation, inspect **the installed CLI** before you send a mutation request.

1. `cf --version`
2. `cf cli search "human task statement"` — entire task as **one quoted argument**. No credentials required. Returns up to 5 ranked JSON entries with `command`, `summary`.
3. `cf schema <group> <operation>` for generated API commands. The JSON object includes `operationId`, `httpMethod`, `path`, `pathParams`, `queryParams`, `hasRequestBody`, `requestBodyFields`; fields carry type/requiredness/descriptions.
4. `cf <group> ... <operation> --help` for real arguments and flags. For hand-written commands (`cf deploy`, `cf migrate`) use `--help` and product documentation, not `cf schema`.
5. `cf docs search "question"` (available as of beta.15) returns ranked live documentation titles/descriptions/URLs, no login required. Fetch a selected `https://developers.cloudflare.com/.../index.md` page as Markdown when connected browsing is available; do not confuse live doc search with static local command search. Searches may be recorded in anonymous telemetry; do not include secrets or sensitive values in the query.
6. For resource mutation commands, append `--dry-run` if current help lists it. Review the result; then execute deliberately, and read back the remote state.

## Generated command syntax

Typical shape: `cf <product> [subgroup ...] <operation> [positional-identifiers] [--flags]`.

Generated commands differ by API endpoint. Some API path parameters appear as positionals, some as flags (including optional defaults changed in beta.17). Never extrapolate from a different resource.

`cf dns records create --zone example.com --body '{"type":"A","name":"test","content":"192.0.2.1"}' --dry-run` is a documented concrete example. JSON `--body` may be necessary even when the schema lists some flags. Body flags and nested flattening can change across versions; enum fields can be constrained. `--body` is a *JSON string*, not an arbitrary shell fragment. Avoid interpolating untrusted external strings into a shell command; generate proper JSON and pass an argument array to a subprocess. Use a secure temporary file or interactive input for secrets when supported; never expose credential values in command histories/logs.

Do not assume all flags support `@file` syntax. Some generated enum flags accept file values in beta.14+, but confirm individual help. Do not assume `--dry-run` redacts every sensitive value: beta.13+ redacts schema-marked sensitive fields, but custom bodies and unmarked data may still be present. Treat previews as sensitive until reviewed.

## JSON / process contracts

- stdout: JSON results in most API operations, lists as arrays for one page; raw content (objects, media/protobuf) remains raw. Some successful mutations emit nothing.
- stderr: progress, warnings, account/zone selection status, errors. Never parse stderr as a structured result unless a command says to.
- exit status: nonzero means failure in ordinary commands, but some migrations intentionally return `1` after generating files with TODOs; older beta versions returned `0` for declined noninteractive deletes and beta.15+ returns `1`. Inspect actual postconditions.
- pagination: most list commands return **one page**. Help reveals `--page`, `--per-page`, cursor, token or other pagination shape; continue until complete. A single result is not an exhaustive inventory.
- data filtering: use `jq` or JSON parser; preserve IDs and distinguish stable identifiers from display names.
- retries: for 429/5xx, follow `Retry-After` and backoff; never blindly retry a non-idempotent create/delete/change if outcome is uncertain. Query current remote state before retrying.
- raw downloads: redirect stdout to a file, avoid JSON parsing for binary.

## Standard request preview checklist

- Is this the correct account, zone, environment, Worker/database/bucket and API endpoint? Check `method`, URL, path and resource ID.
- Did the body contain every intended field and **no unspecified defaults** that reset resource settings?
- Is a destructive action, cascade or propagation effect hidden behind `--force`, PUT vs PATCH, or a `--body` object?
- Does the token have only minimal permissions for this mutation?
- Do we understand whether `--dry-run` actually exercises build/bootstrap steps locally?
- Is a verified rollback or backup available?

Example:

```bash
cf cli search "create a DNS record"
cf schema dns records create
cf dns records create --help
cf zones list --name example.com
cf dns records list --zone example.com --name test.example.com
cf dns records create --zone ZONE_ID --body '{"type":"A","name":"test","content":"192.0.2.1","proxied":true}' --dry-run
# Only after explicit approval and preview review:
cf dns records create --zone example.com --body '{"type":"A","name":"test","content":"192.0.2.1","proxied":true}'
cf dns records list --zone example.com --name test.example.com
```

In this example, use the zone ID for dry runs. Dry runs do not look up a zone domain to resolve its ID, while the live command can.

## Introspection helper

`python scripts/cf_discover.py "list R2 buckets" --inspect` emits matched commands and read-only help/schema of top match. `--docs` invokes live docs search instead. It does not execute returned API operations and does not authenticate.

Sources: https://developers.cloudflare.com/cf/agents/ ; https://developers.cloudflare.com/cf/get-started/resources/ ; https://github.com/cloudflare/cf/blob/main/packages/cli/CHANGELOG.md
