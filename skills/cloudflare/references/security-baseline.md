# Cloudflare platform security baseline

Applies to all deployments and account/zone administration. Prefer verifiable controls over enabling a product and assuming the app is secure.

## 1. Threat-model first

Document assets, attacker capabilities, data flows and trust boundaries:
- Internet client -> Cloudflare edge -> Worker/Access/WAF -> origin -> database.
- CI system / coding agent -> Cloudflare API -> account/zone settings.
- Admin and workforce identity -> Zero Trust dashboard or protected internal app.
- Third-party webhooks -> worker -> queue/storage.
- Model or retrieval output -> agent tool call, where untrusted text must never become privileged instructions.

Map controls to threats (credential theft, origin bypass, SSRF, cache poisoning, auth bypass, data leakage, supply-chain compromise, DDoS, mistaken agent writes), owner and verification procedure.

## 2. Account & automation identity

- Require phishing-resistant MFA for privileged human administrators where supported, review role assignments and remove dormant members.
- Prefer scoped account-owned API tokens for unattended jobs where appropriate; use user-scoped tokens when ownership and permission semantics require them. Avoid global API keys.
- Scope each token to minimum permissions, explicitly selected accounts/zones, expiry and optional client IP conditions. Separate read, deploy and admin credentials.
- Use secret manager/CI secret store, not source, CI YAML literals, shell history or logs. Rotate on incident and on lifecycle changes; record owner and expiry.
- Do not let an agent create high-privilege API tokens or change MFA, memberships, billing or account ownership without specific operator authorization.
- Set explicit account, zone and environment in every change plan. Check active cf profile, CLOUDFLARE_API_TOKEN override and directory bindings; env token can take precedence over login.
- Enable and review audit logs (where available); log who/what/when, target, diff, job or ticket ID; redact token values.

Official: https://developers.cloudflare.com/fundamentals/api/get-started/ ; https://developers.cloudflare.com/fundamentals/api/reference/permissions/.

## 3. DNS, TLS, origin

- Prefer proxied records where Cloudflare features are needed. Review DNS-only records and historical records that expose origin addresses.
- Use Full (strict) with an appropriate valid origin certificate for normal HTTPS origins, and enforce HTTPS to clients. Do not use Flexible to work around origin issues.
- Consider certificate expiry, SNI, hostnames, chain, renewal and downgrade consequences.
- Protect origin from direct access using appropriate firewall/routing and optionally Authenticated Origin Pulls (AOP). Global AOP only proves traffic came from the Cloudflare network, not a particular account; for stricter separation use zone/per-hostname certificates.
- AOP is not compatible with Tunnel origins. For Tunnel, outbound-only connector, Access policies and private origin network segmentation serve a different protection model.
- Never blindly IP-allowlist Cloudflare ranges without considering shared-network origin spoofing/host-header risks and your application layer's authentication.
- Protect administrative and origin debugging endpoints separately; neither WAF nor orange-cloud alone authenticates them.
- DNSSEC, CAA, HSTS and cert management can increase protection but can also cause outages when deployed incorrectly; inspect registrars, issuance, rollback and browser HSTS permanence before changes.

Official: https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/ ; https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/ ; https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/.

## 4. Application and API protection

- Authentication and authorization happen at the application/service boundary even when WAF or Access is present. Verify object-level access, method permissions and tenant separation.
- WAF managed rules, custom rules and rate limiting are defense in depth. Stage new rules in logging/challenge/low-impact modes if supported, measure false positives, and maintain break-glass recovery.
- For machine APIs, enforce schema validation, content limits, signed webhooks, replay protection and quotas. API Shield features may add mTLS/JWT/schema controls where available.
- Turnstile must be verified with the server-side Siteverify API, not merely embedded in a browser. Verify expected hostname/action when applicable and reject expired/reused tokens.
- Cache controls must prevent authenticated responses or cookies from being cached publicly. Never treat the cache as a secure isolation boundary.
- Implement CSRF protection for cookie-authenticated state-changing requests, robust CORS allowlisting, output encoding, secure headers and transport security.
- Test path normalization, host headers, origin rules, URL redirects, missing auth and unexpected HTTP methods.

Official: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/ ; https://developers.cloudflare.com/waf/ ; https://developers.cloudflare.com/api-shield/.

## 5. Zero Trust

- Deny by default; grant least privilege to applications, identities, devices, service tokens and routes.
- Review policy precedence and narrow Bypass exceptions: a broad Bypass disables Access enforcement and logging for matching traffic.
- For service-to-service authentication, use Service Auth policies with narrowly scoped Access service tokens and consider an additional network condition. Rotate secrets with controlled overlap and revoke compromised tokens.
- Avoid relying only on IP ranges, client headers or possession of an easily copied URL.
- Restrict private routes and split tunneling to intended networks; avoid unintended broad CIDR access or overlapping route domains.
- Use device posture when justified; write access runbooks for IdP or device-agent outage and break-glass accounts.

Official: https://developers.cloudflare.com/cloudflare-one/access-controls/policies/ ; https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/.

## 6. Secrets & data governance

- Separate public binding vars from secrets. Prefer per-Worker secrets or Secrets Store bindings as appropriate; ensure read access is minimum.
- Encrypt data in transit and verify service-specific encryption at rest and key management. Check retention, backups, access logging and deletion obligations.
- Do not log authorization headers, sessions, Access/JWT tokens, PII, payment details, raw prompts or responses that contain customer content.
- Validate whether a product's location, replication, analytics and logging satisfy applicable residency and processing agreements; do not promise single-region storage just because compute is edge-located.
- Limit third-party model and log export access; secrets can leak via error traces, debugger output or prompt injection.

## 7. Secure-change gate (mandatory)

For any production WAF, TLS, DNS, Access, Tunnel routing, token or cache-policy change:
1. Read current configuration and identify authoritative owner (IaC or console).
2. Record target ID, exact resource, diff, affected clients and blast radius.
3. Verify rollback and break-glass access.
4. Preview, stage or simulate in non-production where possible.
5. Request explicit approval for destructive or high-impact change.
6. Apply in bounded increments and monitor 4xx/5xx, WAF actions, TLS errors and business KPIs.
7. Verify remote state and external path end-to-end; maintain incident record.

No single product switch constitutes a completed security review.
