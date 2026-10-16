# Production architecture recipes: start points, not copy-paste guarantees

Use decision-framework.md and security-baseline.md to adapt each design.

## 1. Public marketing or documentation site

Client -> DNS/TLS -> Cloudflare Workers Static Assets (or Pages) -> optional Worker SSR/API.
- Prefer immutable versioned assets, safe cache headers, previews and simple deployment.
- Add analytics with consent/privacy rules and error monitoring.
- Never cache personalized preview/Admin pages as public.
- If a CMS exists, segregate editing/authentication from public rendering; protect webhook credentials and purge precisely.
- Decide whether Workers or Pages based on existing framework, operations and product direction, not blanket superiority.

## 2. Authenticated multi-tenant SaaS

Client -> Worker API -> authn/authz -> D1/Hyperdrive/Postgres; R2 for uploads; Queue for jobs; DO for per-tenant coordination when justified.
- Authenticate requests and authorize resource access on every path.
- Use tenant_id in schema/queries and storage keys, validate signed object URLs and minimize privileged service bindings.
- Protect sessions, secrets, CORS/CSRF and caches.
- Use migration and load tests, separate tenants in observability without recording personal data.
- For complex SQL and transactions prefer tested relational model over KV.

## 3. Event ingestion/webhook processor

Provider -> Worker -> verify raw-body signature+timestamp -> dedupe ID -> Queue -> idempotent consumer -> store.
- Return 2xx only after safely accepting work under documented guarantees.
- Backpressure, poison messages, retries, DLQ and replays must be designed.
- Bound payload size, reject replay and use secret rotation windows.
- Do not assume Queue delivery is exactly once.

## 4. Realtime shared room

Client/WebSocket -> Worker routing -> Durable Object per room -> SQLite/DO storage -> optional Queue event fan-out.
- Define room ID/tenant isolation, message ordering and reconnect protocol.
- Avoid cross-room global coordination bottlenecks.
- Plan hibernation, connection closure, object failures and reconnect replay.
- Authenticate upgrades and every privileged message, not just socket establishment.

## 5. Private admin application

Authorized user/WARP client -> Cloudflare Access -> public hostname or private Tunnel route -> internal admin server.
- Restrict Access policy to intended identity/device and service account.
- Do not treat Tunnel as an auth layer or open debug routes.
- Keep origin non-public, hardened and instrumented.
- Test IdP outage, service tokens, connector HA and break-glass access.

## 6. AI/RAG app

Request -> Worker auth/quota -> AI Gateway/Workers AI -> retrieval Vectorize/R2/D1 -> response with observability.
- Validate prompt/input and document outputs; model content is untrusted.
- Avoid tool use from raw model output without authorization/validation.
- Separate tenant indexes and encrypt/private documents; obey retention/deletion.
- Define token budget, rate limiting, caching safety, fallback and content risks.
- Evaluate provider routing and geography, prompt cost and output quality, not only latency.

## 7. Modern CMS-backed frontend on Cloudflare

Worker/Pages frontend -> authenticated CMS API (possibly separate Worker) -> D1/R2/media.
- SSR and build-time regeneration need different caching/invalidation approaches.
- Secure CMS admin behind authentication with an independent authorization model.
- Protect schema migrations, preview tokens, uploads and published routes.
- Audit D1 database access vs CMS compatibility; no assumption any Node CMS deploys unmodified.

## 8. Site and origin migration

- Inventory DNS, route rules, TLS, redirects, cache, WAF, service bindings and external dependencies.
- Deploy and measure in parallel; stage traffic gradually.
- Maintain rollback at DNS/route layer and schema compatibility.
- Detect origin IP bypass and incorrect host headers.
- Roll back in documented order, considering caches and TTL.
