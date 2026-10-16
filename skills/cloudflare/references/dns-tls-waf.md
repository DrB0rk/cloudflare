# DNS, certificates, WAF, CDN and origin protection operations

## 1. DNS zone-change plan

For a DNS mutation document: exact zone ID, record ID, name, type, content, proxied flag, TTL, existing wildcard/flattening behavior, dependent systems, owner, risk and rollback.
- Read current record and DNSSEC state first. Avoid overwriting rather than creating on conflicts.
- Validate nameserver delegation and registrar authority before proposing zone changes.
- AAAA, A, CNAME, MX, TXT, CAA, DKIM, SPF and DMARC have different proxy requirements. Mail records and verification records are not HTTP proxy targets.
- Test both recursive resolution and authoritative DNS; propagation can be affected by external caches/TTL.
- Account for DNS rebinding, dangling CNAMEs, subdomain takeover, and stale vendor verification records.
- Plan DNSSEC key rotation/delegation carefully to avoid SERVFAIL.

## 2. TLS & origin decision tree

- Terminate HTTPS at the edge with valid edge certificate.
- For HTTPS origin prefer Full (strict) and validate origin certificate/SNI/chain and hostnames.
- Configure HTTP-to-HTTPS redirects, HSTS and certificate renewal only after ensuring redirects and origin TLS work; HSTS preload is hard to reverse.
- To prevent origin bypass: restrict origin network exposure, avoid leaked IPs, and optionally configure Authenticated Origin Pulls with the appropriate trust model.
- Global AOP proves membership in the Cloudflare network, not uniquely your Cloudflare account. Per-zone or per-hostname AOP can provide tighter control.
- AOP and Tunnel origins are different mechanisms and not compatible; do not try to force AOP on a Tunnel.
- Verify security without lowering Full (strict) to Flexible as a permanent workaround.

## 3. WAF and bot changes

- Start with observed attack patterns: endpoint, request field, false-positive sample, upstream error rate.
- Use layered managed rules/custom rules/API Shield/rate limiting as defense in depth. Never treat WAF rules as fine-grained application authorization.
- Confirm evaluation phase and skip rule behavior; skip actions can unintentionally bypass later protections.
- Stage in log/challenge where possible; keep a control sample and measure impacts to good traffic.
- Exempt only specific verified paths and actors, not entire applications or broad geographies.
- Rate limiting at edge must still coexist with in-app quotas and per-customer authorization. Choose reliable keying strategies for NAT/mobile traffic.
- Bot scores and JA3/JA4 signals are heuristics; avoid single-signal irreversible decisions.

## 4. Cache safety

- Define cache key and cacheable status for public resources; ensure Vary, cookies and auth do not cross tenant/user boundaries.
- Protect mutation endpoints, Set-Cookie responses, private dashboards, personalized HTML and APIs from unintended caching.
- Set explicit edge and browser caching policies; verify CDN rule interactions and stale-while-revalidate behavior.
- Cache purges are production-affecting and can cause origin thundering herds; target URLs/tags/prefixes as appropriate instead of purging everything.
- Guard origin against post-purge spikes with layered caching and rate controls.

## 5. Validation/rollback

Use external HTTPS, DNSSEC and headers checks alongside dashboard/API state; test client regions and direct-origin access where authorized. Monitor 52x, 4xx, challenge rates, conversion/business metrics, DNS anomalies and certificate errors. Keep snapshot of original configuration for rollback.

Official: https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/ ; https://developers.cloudflare.com/ssl/origin-configuration/ ; https://developers.cloudflare.com/waf/ ; https://developers.cloudflare.com/cache/.
