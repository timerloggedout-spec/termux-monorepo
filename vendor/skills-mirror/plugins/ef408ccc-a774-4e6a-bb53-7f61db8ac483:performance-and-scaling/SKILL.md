---
name: performance-and-scaling
description: Use when building or modifying any backend component, BEFORE making perf or scaling choices. Forces the question "at what load" up front, names the bottleneck axis, and pushes vertical scaling and indexes before distributed anything. Apply this whenever you are tempted to "make it fast" without numbers, or to "make it scale" before measuring.
---

# Performance and Scaling

Performance is a design decision, not a property you bolt on. Most "the app is slow" stories are not about clever code, they are about not knowing the load, not sizing the boring layer, and making N calls when one would do.

## The Discipline

Before writing anything non-trivial, answer:

1. **At what load?** Requests per second, concurrent users, payload size, data volume now, data volume in 18 months.
2. **What is the latency budget?** Total, and how is it spent across DB, CPU, network, third parties.
3. **What is the bottleneck axis?** CPU, memory, DB connections, IOPS, network bandwidth, third-party rate limit. Name one.
4. **What is "good enough"?** A number, not a feeling. If you do not have a target, you cannot say "done".
5. **Boring lever first.** Index, query rewrite, connection pool, vertical resize. Distribution and caching are levers 4 and 5, not 1 and 2.

If the user has not given you load numbers, ask. "How many of these per minute, peak?" is one question. The answer changes the design.

## The Load Question

Before you propose anything, classify the load. The same component looks completely different at these scales:

| Tier | Rough numbers | What changes |
|------|---------------|--------------|
| Trickle | < 1 req/s, < 100 jobs/day | Boring monolith, single DB, no cache needed |
| Steady | tens to hundreds req/s | Pool the DB, index every hot query, read replicas if reporting bites |
| Heavy | thousands req/s | Hot-path budgeting, careful allocation, cache the expensive reads, partition the queue |
| Big | tens of thousands+ req/s | You will have measured your way here. Sharding, regional, edge caching, custom protocols |

Most teams are at Trickle or Steady and design for Heavy. That is how a Friday afternoon endpoint becomes a Tuesday outage in a different way: too much complexity for too little gain.

## Bottlenecks by Layer

Know which one is yours, do not over-fix the others.

- **DB connections.** Each app instance holds a pool. 100 instances at 20 connections each is 2000 connections, and Postgres falls over around a few hundred. Use PgBouncer (transaction pooling for typical web workloads). See [[query-discipline]] for query cost; this is about concurrency cost.
- **Query plan.** Most "slow" is here. Run `EXPLAIN ANALYZE`. See [[query-discipline]].
- **Allocations on the hot path.** In compiled languages, look at allocations per request. In JS / Python, look at GC pressure. Profile before guessing.
- **Sync where async would do.** A handler that blocks on a third-party call holds a worker the whole time. Push to a job. See [[idempotency-and-side-effects]].
- **Lock contention.** Row locks held longer than needed, advisory locks across a hot path. Profile lock waits in pg_stat_activity.
- **Cache stampede.** Cache expires, 100 requests miss at once, all of them hit the DB. Use single-flight, jittered TTL, or stale-while-revalidate.

The wrong cure for the wrong bottleneck is worse than no cure.

## The Scaling Ladder

Climb in order. Skip rungs and you pay the operational tax twice.

1. **Make the query fast.** Index, rewrite, or denormalize. Free orders of magnitude before any infra change.
2. **Pool the connections.** PgBouncer in transaction mode for most web apps. Sized to `<DB max_connections> / <app instances>`.
3. **Resize the boring layer.** Bigger Postgres instance. More CPU on the app. This is shockingly often the right answer up to surprising sizes.
4. **Add a read replica** for read-heavy reporting and analytics. Routes long queries off the primary.
5. **Cache the expensive read** with explicit invalidation. See "Cache Discipline" below.
6. **Partition the work.** Queue partitioned by tenant. Tables partitioned by time. This is where complexity starts to bite.
7. **Distribute.** Sharding, multi-region, eventual consistency. You are here because you have numbers, not because it sounds cool. See [[boring-by-default]].

A single Postgres at 8 cores serves more apps than people admit. Climb the ladder honestly.

## Cache Discipline

Most apps do not need a cache, they need an index. When you do need one:

- **Cache what is expensive to compute and slow to change.** Aggregations, fan-out reads, third-party responses. Not "every row from the DB".
- **Pick the invalidation story before the cache.** "TTL-only" is acceptable for stale-tolerant reads. Event-driven invalidation for the rest. Cache without an invalidation story rots fast.
- **Guard against the stampede.** Single-flight per key (one DB call satisfies all concurrent misses), jittered TTL, or stale-while-revalidate.
- **Never cache PII without a redaction story** and a deletion story (GDPR / equivalent).

Default position: do not cache yet. Add it when a specific hot path has a measured latency cost.

## Async Where It Pays Rent

If the operation takes longer than the user's patience (~200ms), or it calls a third party, push it to a background job. See [[idempotency-and-side-effects]] for the discipline.

Async is not free: it adds a queue, a worker, retry logic, observability work. Use it when sync costs more.

## Anti-Patterns

- **Premature distribution.** Three microservices solving a monolith problem. You pay coordination cost forever to save imagined eng-years.
- **"We will just add more pods."** Doubling app pods often doubles DB connections too, which is how outages happen at peak. Scale the boring layer first.
- **Caching to fix a query.** A 200ms query cached for 5 minutes is still 200ms when the cache expires under load. Fix the query.
- **Optimizing the wrong axis.** Tuning GC on a CPU-bound app. Tuning indexes on a memory-bound app. Profile before guessing.
- **Sync I/O on the hot path.** Reading from disk, hitting a third party, doing CPU-heavy work inside the request thread. Pushes p99 off a cliff.
- **`SELECT COUNT(*)` everywhere.** Counting a growing table on every page load is a future incident. Use approximate counts or counter tables.
- **Connection-per-request frameworks at scale.** A spike doubles open connections. Use a pool, with sensible upper bounds.
- **Designing for the Heavy tier from day one.** You pay the complexity now, you may never need it.

## Quick Decision Guide

| Question | Default | Deviate when |
|----------|---------|--------------|
| First lever for "slow" | Run EXPLAIN, then index or rewrite | DB is verifiably not the bottleneck |
| Connection pool | PgBouncer, transaction mode | Sticky sessions or prepared statements forbid it |
| Cache before measuring? | No | Latency target documented, query already as fast as it gets |
| Read replica? | When reporting starts to hurt the primary | Always, when the workload is read-skewed and stale-tolerant |
| Vertical vs horizontal | Vertical first | A single instance is already maxed and the workload shards naturally |
| Sync vs async on the hot path | Async over 200ms or if it calls a third party | Read-only, in-process, fast |
| Microservices | No | Two clear pain points: deploy independence and team-of-teams |

## See also

- [[query-discipline]] for plans, indexes, and N+1
- [[observability-by-default]] for the metrics that tell you the bottleneck axis
- [[idempotency-and-side-effects]] for pushing work to the background
- [[boring-by-default]] for the scaling ladder rungs and what NOT to adopt
- [[think-before-coding]] Step 1 and Step 6 for the load classification and observability hooks
