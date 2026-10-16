# Zero Trust, Access, Tunnel, Gateway and private networking

Treat Zero Trust as an identity, device, application and network policy system; a Tunnel is transport, not authentication.

## 1. Choose the access pattern

| Use case | Recommended starting point | Review |
| --- | --- | --- |
| Private browser application | Access application with IdP, narrowed policy and MFA | Session lifetime, routes, public callbacks |
| Machine-to-machine private API | Access Service Auth + service token, optionally IP/mTLS | Secret rotation, audience, policy order |
| Private IP / DNS service | Tunnel private routes + WARP/Gateway rules | CIDRs, DNS resolution, split tunnel and routing |
| Internal SSH/RDP | Access-controlled transport / Zero Trust device policy | Authorization, logging, emergency access |
| Public webhook callback | Explicitly narrow callback path; authenticate payload cryptographically | Do not broadly Bypass entire application |
| CI deployment | Cloudflare API token scoped to resource, not Access service token | Account permissions and secret management |

Tunnel only needs outbound connector connectivity to Cloudflare; it does not by itself make the application private. Verify that all published hostnames are protected according to policy.

## 2. Access policy logic

- Evaluate exact application and path selection before reasoning about policies.
- Access Service Auth and Bypass policy evaluation can precede Allow/Block in special ways; consult current policy order docs rather than assuming list order.
- Bypass suppresses Access enforcement and related logs for matching requests. Scope exceptions narrowly and prefer Service Auth for machine traffic.
- Test identities permitted and denied, not just successful login.
- Avoid 'Everyone' Include or broad one-time PIN policies unless intentionally public.
- Protect IdP change paths and dashboard administrators against lockout; retain an audited break-glass procedure.

## 3. Tunnel hardening

- Run cloudflared with dedicated unprivileged identity and managed updates.
- Protect tunnel credentials and remote management tokens; do not store them in git.
- Scope ingress hostname/path/service mappings and enforce a terminal default 404 rule for locally-managed ingress.
- Prefer TLS verification to origin; do not disable verification to hide certificate defects.
- Restrict origin to connector reachability where practical; do not expose its admin port.
- Monitor connector replicas, uptime, DNS, origin health and tunnel route drift.
- Avoid confusing API tunnel configuration with the cloudflared daemon lifecycle; use separate tools.

## 4. Gateway, WARP and private access

- Decide device enrollment, posture enforcement, identity attributes, DNS policies, HTTP policies and network routing together.
- Model private networks, overlapping RFC1918 ranges, split-tunnel selectors, egress IP and NAT, and local DNS conflicts.
- Test protocol-specific behavior: websocket, SSH, long-lived connections, UDP/TCP, proxy, DNS, certificate pinning.
- Observe privacy and log retention when enabling content inspection or remote browser isolation.
- Test outage cases: IdP offline, connector dropped, policy control plane change, WARP client not enrolled.
- Do not open broad ingress to work around policy failures.

## 5. Security evidence checklist

Capture sanitized policy snapshots, identity test results, tunnel ingress route listing, connector status, last rotation, audit trail, negative-path tests and rollback.
Official: https://developers.cloudflare.com/cloudflare-one/access-controls/policies/ ; https://developers.cloudflare.com/cloudflare-one/networks/connectivity-options/ ; https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/.
