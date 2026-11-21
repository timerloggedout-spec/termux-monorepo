# Pinecone Vector-Store Comparison

**Status:** executing · pre-registration and reference integration  
**Owner direction:** 2026-11-21 — add Pinecone to refTemplates and smods; compare it as a DoE treatment.

## Objective

Bring the existing managed Pinecone vector-database integration into the reference-template and capability registries, then compare retrieval engines under one frozen corpus, one query cohort, and identical vector inputs.

The experiment separates two questions:

1. **Storage-engine effect:** Pinecone serverless, PostgreSQL pgvector, pg_pinecone native, and pg_pinecone remote using the same precomputed embeddings and query vectors.
2. **End-to-end embedding path:** the existing Pinecone integrated-inference index (termux-knowledge, model configuration recorded by the current integration) as a distinct system treatment. This path does not get mixed into the storage-only causal estimate unless the same embedding model/version is used for every arm.

## Existing implementation

The repository already contains:
- scripts/pinecone/pinecone_client.py — standard-library REST client, API key from PINECONE_API_KEY only.
- scripts/pinecone/knowledge_sync.py — deterministic content-hash chunk IDs and sync/search/observe modes for termux-knowledge.
- .github/workflows/pinecone-knowledge.yml — dispatch/monthly/path-triggered workflow with fake-transport tests and a run artifact.
- tests/test_pinecone_knowledge.py — five fake-transport tests.

Historical live proof is recorded in the Pinecone integration history: successful runs 40825414482 and 40825424150 on source SHA 5fb203a8. This is historical evidence, not a claim that the current master head has been freshly exercised.

## Reference sources

- Managed service: https://docs.pinecone.io/
- PostgreSQL extension: https://github.com/pinecone-io/pg_pinecone at d860f6fd3a21733d75ed2cde2b5b5e71e79bd3ac (Apache-2.0).
- PostgreSQL baseline: https://github.com/pgvector/pgvector at 1d56580cda45d20b6b197fbe325fb0f6301e33cd.
- Official developer MCP reference: https://github.com/pinecone-io/pinecone-mcp at 275aa5cb8b4dc7fb6471f3483cb05191c338b61c (Apache-2.0).

## Smods decision

The repository's smods policy requires a real custom fork, immutable reviewed pin, compatibility evidence, and passing gates. No timerloggedout-spec/pg_pinecone_fork repository exists at the inspected snapshot, and this session's GitHub connector exposes no fork-creation action. The source is therefore catalogued and its exact upstream revision recorded; the live gitlink remains a gated follow-on. The implementation uses the existing managed Pinecone REST adapter and does not introduce a direct-upstream gitlink.

## Safety and execution boundaries

- Keep all credential values outside source, metadata, experiment records, and artifacts.
- Preserve PINECONE_API_KEY as the existing Actions secret name; no secret read or rotation occurs in this change.
- Keep the existing termux-knowledge index as the incumbent. Use a dedicated namespace and explicit budget approval for any experiment writes.
- Treat PostgreSQL 17/18, superuser access, pgvector installation, Docker image compatibility, and Pinecone remote-index allocation as preflight gates.
- Keep production routing, existing namespaces, index deletion, and account/billing mutations outside this proposal.
- Record skipped, unavailable, censored, and failed arms as observations; do not turn admission failures into database-quality failures.

## Deliverables

See ITEMS.md, DEBATE.md, and MANIFEST.md. The DoE design is experiments/doe/pinecone-vector-store/DESIGN.json.
