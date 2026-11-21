# Context Relationship and Historical Corpus

**Sources:** Git tree/files at pinned SHA; GitHub issues, PRs, commits, reviews, comments and workflow metadata; prior canonical nodes/edges and coverage checkpoints.

**Pipeline:** source_collector.py + github_collector.py → seed_merger.py → compiler.py → build_index.py → canonical JSONL nodes/edges, manifest, reports and checkpoint. Temporal helpers build snapshots, lineage and comparisons.

**Consumers:** ArchWiz context query, bounded agent context deltas, temporal views, Mermaid projections and SHE reducers.

**Findings:** Git/GitHub collectors → compiler → canonical index is connected. COMPLETE requires contiguous page windows from page one; otherwise preserve PARTIAL_CONTINUATION_REQUIRED or UNVERIFIED. Confidence labels verified/derived/inferred/candidate remain distinct. Mermaid graphs are projections, not source evidence. Freshness depends on source SHA, observed_at, checkpoint and coverage.

**Sources:** [CRG contract](../../ops/CONTEXT-RELATIONSHIP-INDEX.md) · [build_index.py](../../../archwiz/context_relationships/build_index.py) · [Temporal evidence](../../ops/CONTEXT-RELATIONSHIP-TEMPORAL-EVIDENCE.md)
