# IIE Technology Evaluation Matrix

**Parent:** [Incremental Intelligence RFP](../superpowers/specs/2026-11-15-incremental-intelligence-queue-integration-rfp.md)  
**Purpose:** research and procurement shortlist; not an approved dependency manifest.

## Selection principles

1. Start with repository-native and standard-library baselines.
2. Optimize measured bottlenecks, not technology fashion.
3. Keep the Android/Termux core small and offline-capable.
4. Treat derived indexes as rebuildable projections.
5. Record license, maintenance, security, platform support and total operational cost before adoption.

## Technology matrix

| Layer | Candidates | Strong use case | Risks / constraints | Initial decision |
|---|---|---|---|---|
| Event sensing | GitHub events, webhooks, Actions workflow_run | Low-latency source change detection | Delivery gaps, trust validation | Existing CEEL contract |
| Conditional reads | ETag, If-Modified-Since, cursors | Avoid unchanged payload transfer | Provider-specific semantics | P0 |
| Local durable metadata | SQLite, FTS5, JSONL | Small local offline index | Write contention, migrations | Preferred baseline |
| Batch analytics | DuckDB | Join large JSONL/Parquet datasets | Memory footprint | CI/research only |
| Columnar interchange | Apache Arrow | Efficient analytics pipeline handoff | Dependency size | Evaluate only if needed |
| Historical projection | Parquet | Compression and scan efficiency | Not an append log | Derived snapshots only |
| Vector retrieval | Exact cosine, FAISS Flat/IVF/HNSW | Similar-item candidate retrieval | Native builds and memory | Benchmark |
| Clustering | Lloyd, MiniBatchKMeans, e-means, HDBSCAN | Topic/relationship candidate groups | Drift and cluster instability | Benchmark |
| Lexical retrieval | SQLite FTS5/BM25, Lucene | Exact term matching | Tokenization/versioning | Keep FTS baseline |
| Hybrid ranking | Reciprocal-rank fusion, rerankers | Combine lexical and semantic evidence | More latency and compute | Optional experiment |
| Deduplication | SHA-256, MinHash, SimHash, Bloom filters | Exact and near-duplicate detection | False positives for probabilistic methods | Hash first |
| Source parsing | Tree-sitter, language ASTs | Syntax-aware relationships | Parser drift and build costs | Targeted pilot |
| Telemetry | Existing ATES, OpenTelemetry SDK/exporters | Correlated spans/metrics | Avoid duplicate stores and cardinality explosion | Extend existing |
| Metrics | Prometheus exposition/textfile | Small service/device counters | Cardinality and scrape availability | Existing metrics first |
| Durable stream | NATS JetStream, Kafka, Redpanda | High fan-out, replay, independent consumers | Operational footprint | Deferred |
| Workflow engine | Existing dependency-phase engine; Temporal as research comparator | Long-running workflow state | Duplicate orchestration | Existing engine remains owner |
| Cache | Content-addressed files, SQLite; Redis comparator | Reuse deterministic source transforms | Invalidation and stale values | Local-first |
| Integrity | Merkle trees, signed manifests | Large corpus integrity and delta checks | Tree maintenance | Research |
| Security analysis | Semgrep, CodeQL, OSV-Scanner, Syft/Grype | Static/dependency/supply-chain findings | False positives, runtime cost, license | Reuse approved security lanes |
| Search service | OpenSearch/Elasticsearch | Large multi-user search workloads | RAM and operations | Not Termux-first |

## Technology discovery backlog

| Area | Explore | Question |
|---|---|---|
| Incremental computation | Build systems (Bazel/Buck2), materialized-view maintenance, content-addressed DAGs | Can deterministic transforms be cached by input fingerprint? |
| Stream processing | Benthos/Redpanda Connect, Apache Flink, Bytewax | Is event volume high enough to justify stream runtime? |
| Graph analysis | NetworkX, igraph, GraphBLAS, DuckDB recursive SQL | Which graph algorithms reveal actionable dependency clusters? |
| Search | Tantivy, Meilisearch, Typesense, Vespa | What is the smallest platform that meets retrieval SLOs? |
| Observability | OpenTelemetry Collector, Vector, Fluent Bit | Which collector mode minimizes CPU/syscalls on target devices? |
| Workflow orchestration | Temporal, Restate, Prefect, Dagster | Does the current phase engine lack a required durable primitive? |
| ML optimization | e-means, MiniBatchKMeans, Faiss, ScaNN, hnswlib | What is the actual recall/quality/resource tradeoff on this corpus? |
| Data formats | JSONL, SQLite, Parquet, Arrow IPC | Which representation is canonical vs derived at each scale? |
| Approximate summaries | HyperLogLog, Count-Min Sketch, Bloom filters | Can cardinality/frequency estimates avoid expensive scans safely? |

## Benchmark decision record template

For each candidate record:

- capability contract and owning consumer;
- source repository, exact version/tag/commit and retrieval date;
- license and transitive dependency inventory;
- supported OS/architecture, including Android/Termux;
- install size, runtime RSS, CPU, storage and cold-start;
- input corpus fingerprint and privacy classification;
- correctness, recall/precision, throughput and latency;
- failure behavior, rebuild/rollback and offline behavior;
- security posture, maintenance activity and bus factor;
- integration cost, operator burden and total cost of ownership;
- decision: reject / defer / prototype / integrate / promote;
- evidence references and approver.

No candidate becomes production dependency solely because it is popular, fast in a vendor benchmark, or available at zero price.
