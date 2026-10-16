# Production delivery, IaC, migration and rollback

## 1. Choose control plane consciously

- New typed cf projects: use cf if project and framework are supported and the CLI contract has been checked.
- Existing wrangler.jsonc/toml projects: keep Wrangler for build/dev/deploy until an intentional tested migration. cf can still administer account resources where suitable.
- Shared/prod infrastructure with lifecycle ownership: prefer Terraform/Pulumi or approved IaC process as source of truth. Avoid permanent undocumented imperative drift.
- cloudflared runs connector tunnels; cf manages APIs and project tasks. Neither replaces the other.
- Use the Cloudflare API connector if locally executing CLI isn't possible and the tool supports the exact action; verify identity and account before mutation.

## 2. Promotion model

1. Pin toolchain versions and dependencies, validate lockfile. For cf beta, validate major/minor contract and breaking changes before promotion.
2. Static checks: lint/types, bundler check, dependency audit, secret scanning, policy-as-code, license review.
3. Integration tests: Worker runtime behavior, bindings, authz, invalid input, migrations, queues, failure modes.
4. Non-prod environment with distinct accounts/resources/secrets where possible, realistic data and privacy controls.
5. Deploy preview/canary and measure SLOs, error rate and correctness against baseline; do not assume preview routing replicates full prod access/WAF/cache.
6. Approval gate for production or high-impact mutations; record account, zone and diff.
7. Release with bounded traffic, migration sequencing and operational supervision.
8. Verify deployment ID/version/routing, expected endpoints and storage/schema; capture evidence.
9. Roll back code or routing only when compatible with data changes; some migrations are not reversible.

## 3. CI/CD hardening

- Prefer least-privilege API tokens stored in provider secret manager, short-lived where supported. Never echo credentials.
- Restrict workflow write permissions and execution on untrusted pull requests or forks.
- Protect deployment environments with required reviewers, branch conditions and secret scopes.
- Pin third-party actions by immutable revision in high-assurance repositories and scan transitive dependencies.
- Avoid executing repository-supplied scripts with production tokens when accepting untrusted contributions.
- Fail safely when preflight cannot identify target account, environment, required permissions or changed resources.
- Capture deployments and approvals in audit trail; watch for configuration drift after manual incidents.

## 4. Drift & ownership

For every resource specify IaC owner, state lock, account and environment. Import existing resources into state before management; never parallel-manage the same setting with Terraform and ad-hoc cf without a reconciliation plan. A dry-run/API preview is not a full IaC plan and does not demonstrate cross-resource safety.

## 5. Production preflight checklist

- [ ] Intended account/zone/project confirmed
- [ ] Read current state, resource IDs and ownership
- [ ] Official API/CLI schema validated
- [ ] Current limits/entitlements checked
- [ ] Security/privacy review and secrets redaction complete
- [ ] Diff and blast radius reviewed
- [ ] Migration/backup/RTO plan tested where needed
- [ ] Staging tests + negative paths pass
- [ ] Explicit operator approval where high impact
- [ ] Rollback and on-call owner ready
- [ ] Deploy, independent verification, monitoring documented

Useful: https://developers.cloudflare.com/cf/agents/ ; https://developers.cloudflare.com/cf/wrangler/ ; https://developers.cloudflare.com/terraform/.
