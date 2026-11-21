# Design decisions — Pinecone vector-store comparison

## D1 — Existing Pinecone integration is the incumbent

**Evidence:** scripts/pinecone/pinecone_client.py, scripts/pinecone/knowledge_sync.py, .github/workflows/pinecone-knowledge.yml, and historical successful workflow runs 40825414482 / 40825424150.

**Decision:** Extend and measure the existing integration. Preserve its API key boundary and current index. A new client or duplicate sync workflow is out of scope.

## D2 — Separate managed Pinecone from pg_pinecone

**Evidence:** pinecone-io/pg_pinecone is an Apache-2.0 PostgreSQL extension with pgvector-compatible columns and native / remote engine choices. It is a distinct open-source project alongside the managed Pinecone service.

**Decision:** Catalogue both as related but distinct capabilities. Include pgvector as the PostgreSQL baseline. Pin exact source commits in the metadata.

## D3 — Compare storage engines with identical vectors

**Decision:** Use a frozen corpus, deterministic chunk IDs, fixed embedding model/version, fixed vector dimensions/metric, frozen query set and gold evidence. Use paired query blocks and randomized arm order. Report the integrated-inference end-to-end path separately when its embedding path differs.

## D4 — Smods requires a custom fork

**Evidence:** refTemplates index and consolidation policy require custom-adapted forks, immutable reviewed pins, compatibility evidence, and passing gates.

**Decision:** Record pg_pinecone as the intended smod candidate and hold the gitlink until the custom fork exists. Direct upstream pinning would violate the current smods contract.

## D5 — Runtime evidence follows observed runs

**Decision:** This change registers a design-only campaign. The campaign currently has 0 experiment run records, 0 index allocations, 0 namespace allocations, 0 database instances, and 0 billing mutations. The feed shows admitted_design_only, zero runs, and null results until real EXPERIMENT records exist.
