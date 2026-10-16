# Workers and application security engineering

Use with references/security-baseline.md and references/workers/. This is a secure-coding review framework, not a declaration that any code is secure.

## 1. Untrusted request boundary

For each handler, establish a request schema and limits before side effects:
- Validate method, normalized path, Host, content type and maximum bytes (bounded streaming for large uploads).
- Parse JSON defensively; validate shape, length, range, encoding and enum values at runtime. A TypeScript cast does not validate hostile JSON.
- Authenticate the caller and authorize the specific account, object and operation. Test cross-tenant ID guessing, role escalation, missing subject and revoked sessions.
- Reject private/internal outbound destinations derived from client input. Use a fixed upstream allowlist, URL parser, scheme restriction, explicit ports and redirect validation to prevent SSRF.
- Treat Client-IP headers as trustworthy only in the expected proxied/controlled edge path; don't allow arbitrary callers to spoof trusted forwarding headers.
- Prefer service bindings to public admin API calls for service-to-service traffic, but still enforce authorization and object scope.

## 2. Safe outbound calls

- Set bounded timeouts, retry budgets and concurrency limits. Never retry non-idempotent requests without an idempotency strategy.
- Do not forward inbound Authorization, Cookie or Access tokens to an external host by default.
- Bound redirects and response bodies; validate final destination and content type.
- Use service-specific tokens with minimum scope; separate test and production credentials.
- For payments, email, webhook delivery and queue consumers: include idempotency key, dedupe storage and auditable result state.

## 3. Cookies, sessions, CORS, CSRF

- For cookie sessions use Secure, HttpOnly, appropriate SameSite, expiry, rotation on privilege change and server-side validation.
- Apply CSRF tokens or another defensible anti-CSRF pattern to cookie-authenticated state changes; SameSite alone may be insufficient.
- CORS does not replace authentication. Allow only explicit origins for credentialed APIs; don't use wildcard origin with credentials.
- Responses containing customer/user data: Cache-Control private/no-store as appropriate; avoid setting edge cache or custom cache keys that mix tenants.
- Verify response security headers (CSP, frame-ancestors, referrer and MIME sniffing) according to the application threat model.

## 4. Secrets, crypto and signatures

- Keep secrets out of source and public vars. Access via bindings and avoid serialization or logging.
- Compare signed payloads against the provider's exact raw body bytes; validate algorithm, timestamp window, nonce/replay identifier and key rotation.
- Use Web Crypto primitives and cryptographically secure random values; do not invent cryptographic protocols or trust unverified JWT claims.
- Never make security decisions on a Turnstile browser result without Siteverify validation on the server.

## 5. Runtime and lifecycle

- Workers run in isolates; execution contexts are not a database and may be reused or evicted. Do not use module globals to persist mutable user state.
- Avoid large unbounded response.text()/arrayBuffer() calls. Stream large content while bounding size, memory and processing time.
- await necessary tasks; use ctx.waitUntil for best-effort tasks after response, with platform limits. For durability, use Queues/Workflows.
- Handle errors without leaking internal stack traces, secrets, resource identifiers or sensitive input.
- Set compatibility dates deliberately. For existing projects update after tests; new projects can use a current date. For dates on/after 2026-08-04, Node.js compatibility is enabled by default; verify current docs.
- Only use APIs supported by the deployed runtime and configured compatibility date; inspect bindings and generated types.

## 6. Review test matrix

| Risk | Required negative test |
| --- | --- |
| Auth bypass | Anonymous and expired token denied |
| Broken object authorization | User A cannot read/update user B or tenant B |
| CSRF | Cross-site state-changing request rejected |
| CORS | Unknown Origin never receives credentialed access |
| SSRF | Loopback, private IP, metadata service, redirects blocked |
| Webhooks | Wrong signature, stale timestamp and replay rejected |
| Input | Oversized, invalid encoding, unknown fields handled safely |
| Cache | Authorization/cookie data never publicly cached |
| Rate limit | Bots/bursts rejected without breaking normal clients |
| Secrets | Logs, errors and asset bundles contain no secrets |
| Failure | Upstream timeout, queue duplicate, database outage safe |
| Tenant isolation | Binding, key, index and storage partitioning verified |

Use official guidance: https://developers.cloudflare.com/workers/best-practices/workers-best-practices/ ; https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/turnstile/get-started/server-side-validation/.
