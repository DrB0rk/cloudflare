# Performance engineering and cost control

Never supply static prices or limits as guaranteed current values. Re-verify current plan, pricing, region and release on the day of decision.

## 1. Performance budget

Budget separately:
- Client to edge: DNS, TLS, congestion, cache hit/miss and response streaming.
- Edge execution: startup, CPU, memory, subrequests and serialization.
- Downstream: per-hop latency, DB/DO access, third-party API and connection pooling.
- Queue/Workflow: enqueue latency, throughput, retry and end-to-end completion time.
- Browser: JS/hydration, rendering, web vitals and asset delivery.

Measure p50/p95/p99 under realistic concurrency, global regions and cache states. Account for large-body streaming vs buffering and SSL/TLS origin overhead. Compare cache hit rate, origin throughput and cold paths.

## 2. Optimization priorities

1. Establish baseline and SLO before optimizing.
2. Remove unnecessary upstream hops and sequential network calls.
3. Use bindings where appropriate, not privileged REST API calls from Worker runtime.
4. Stream large bodies with bounded memory; avoid JSON/string copies of unbounded payloads.
5. Use HTTP cache/Static Assets for public immutable resources with safe cache keys.
6. Batch and parallelize independent requests within concurrency, rate and connection budgets.
7. Place computation relative to dominant backend data path (Smart Placement only after profiling).
8. Reduce costly database reads using indexes, prepared statements, sane query patterns, caching where consistency permits.
9. Separate interactive from background jobs (Queues/Workflows), with concurrency and retry budgets.
10. Rebenchmark after every significant change.

## 3. FinOps model

Estimate total monthly run rate as:
- Workers: requests + billable CPU or applicable pricing basis + observability
- Storage: capacity + Class A/B operations + writes + egress where relevant (service-specific)
- D1/DO: read/write operations, stored data, compute/storage and data growth
- Queues/Workflows: messages, operations, steps and retries
- AI: inference tokens/model usage, embeddings, cache behavior, provider egress
- Networking: load balancing, Argo, Spectrum/Tunnel/Zero Trust seats, domain and certificate plan
- Logs: ingestion, sampling, exports, storage and retention
- Business continuity: backups, standby, restore testing

Build best/expected/worst cases with request volume, peak factor, traffic mix, retries and attack amplification. Monitor unit cost per successful transaction and alert on rapid changes.

## 4. Resource limits

Current docs, not repository constants, govern CPU/memory, number of subrequests, payload size, worker bundle size, build output and account quotas. A high-level rule may be wrong on a different plan or in 2027. For each limit include source URL, date and entitlement.

Primary references: https://developers.cloudflare.com/workers/platform/limits/ ; https://developers.cloudflare.com/workers/platform/pricing/ ; https://developers.cloudflare.com/r2/pricing/ ; https://developers.cloudflare.com/changelog/.
