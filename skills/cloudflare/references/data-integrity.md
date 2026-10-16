# Data architecture, consistency and recovery

Never select a datastore solely because it has low-latency edge access. Establish consistency, ownership, recovery and failure guarantees.

## 1. Storage comparison

| Service | Primary fit | Consistency caveat | Recovery concern |
| --- | --- | --- | --- |
| KV | High-read config/lookup/cache | Eventually consistent; stale and negative cached reads | Source-of-truth and invalidation strategy |
| D1 | SQLite relational data | Follow sessions/bookmarks when replica freshness matters | Migrations, restore/time travel availability |
| Durable Objects / SQLite | Per-entity serialized state & coordination | Actor placement/hotspot and retry behavior | Backups, ID migration, schema changes |
| R2 | Durable objects/blobs | Strong object semantics do not imply multi-object atomicity | Lifecycle, retention, versions/backups |
| Hyperdrive + DB | Existing Postgres/MySQL | Source DB transaction semantics; caching implications | External DB snapshots, failover, region |
| Queues | At-least-once async messaging | Duplicate/out-of-order possible | DLQ, replay, poison events |
| Workflows | Durable multistep execution | Step retries may duplicate external effects | Checkpoint compatibility, paused/cancelled jobs |
| Vectorize | Approximate semantic retrieval | Indexing delays/ANN quality | Embedding version and reindex plan |

## 2. Correctness first

- Transactions: identify invariant, write participants and whether one transaction can enforce it.
- Idempotency: stable event ID; persist de-duplication before irreversible side effects where feasible.
- Read-after-write: test the exact D1 session and replication path. Do not assume every read hits primary.
- KV: never use as distributed lock, inventory counter or immediate-revocation authoritative policy store.
- DO: partition by entity and measure skew; avoid single hot actor as a global critical path.
- R2: use content hashes/ETags and conditional writes where available; segregate customer prefixes with application authorization.
- Queues: consumer errors must be observable and retryable; design DLQ replay and side-effect dedupe.
- Workflows: treat compensation as explicit logic; do not claim automated rollback of external effects.
- Avoid consistency claims about cross-product workflows; D1 + R2 + Queue is not an atomic transaction.

## 3. Schema change runbook

1. Inventory running versions, storage mappings, live traffic, and readers/writers.
2. Plan expand-and-contract for online upgrades and an application rollback that tolerates new schema.
3. Back up or snapshot where supported and verify restoration to test environment.
4. Apply migration to staging with representative data volume and concurrency.
5. Deploy compatible readers before writers where necessary.
6. Monitor latency, exceptions, schema drift and data validation; keep old fields until migration finishes.
7. Document forward-only migrations if rollback is unsafe.

## 4. Backup, RPO/RTO and incident review

- Define RPO and RTO explicitly. Cloudflare product redundancy is not identical to a customer-managed backup strategy.
- Test point-in-time recovery and object restore with measured timings; assess cross-account access and disaster recovery.
- Maintain deletion/retention workflows for customer data and exports.
- Investigate replication/consistency anomalies with request IDs, data keys, observed region and timestamps but without logging secrets or PII.
- Verify price and limits per service before proposing high-volume writes, bulk restore or cross-region replication.

Official: https://developers.cloudflare.com/kv/concepts/how-kv-works/ ; https://developers.cloudflare.com/d1/ ; https://developers.cloudflare.com/durable-objects/ ; https://developers.cloudflare.com/r2/ ; https://developers.cloudflare.com/queues/.
