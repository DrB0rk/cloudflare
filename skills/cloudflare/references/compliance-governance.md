# Governance, privacy and operational compliance

This guide supplies engineering considerations, not legal certification or an assertion that Cloudflare products automatically fulfill regulatory obligations.

## 1. Data inventory and processing map

For each flow identify: data controller/processor, input, destination, classification, secrets/PII, storage regions if known, retention, subprocessor, access scope, lawful basis where applicable, backup, deletion and audit owner.

Distinguish:
- Request processing at globally distributed edge.
- Persistent data location in D1, R2, KV, DO, logs and third-party systems.
- Optional model inference, telemetry, analytics and Logpush destinations.
- Developer preview or debugging data and local emulator data.
- Support, backups, disaster recovery and operational access.

Do not equate global edge execution with region-locked storage or legal residency.

## 2. Controls and evidence

- Minimal collection and retention; PII masking, pseudonymization, expiry and deletion workflows.
- Tenant boundaries in application authorization and partitioning, not only naming conventions.
- Key/token lifecycle, privileged access reviews, periodic rotation and break-glass documentation.
- Security audit log availability, retention and tamper resistance aligned to policy.
- Incident response ownership, breach reporting escalation and customer notification process.
- Document Cloudflare service terms, DPA and product-specific data localization guarantees when relevant; verify plan-specific contract conditions.
- Supply-chain SBOM/dependency scanning for Workers applications, with patch cadence and deployment attestations appropriate to risk.
- Where GDPR applies, verify actual processing activities and transfer safeguards with responsible privacy/legal stakeholders.

## 3. Sensitive/regulated workload decision

Before launching healthcare, financial, payment or government workloads:
1. Record specific legal/control requirements (not generic badge claims).
2. Obtain product-level contractual documentation and plan entitlements.
3. Confirm logging/backup/region architecture with external data flows.
4. Execute a documented threat model and privacy impact assessment if required.
5. Validate retention and deletion in primary and backup stores.
6. Verify least privilege and independent audit evidence.
7. Do not claim compliance until qualified owners have approved.

Official starting points: https://www.cloudflare.com/trust-hub/ ; https://developers.cloudflare.com/ ; https://www.cloudflare.com/cloudflare-customer-dpa/.
