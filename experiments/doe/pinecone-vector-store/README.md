# Pinecone Vector-Store DoE

**State:** admitted_design_only · 0 runs · no results

The primary comparison uses the three pg_pinecone engines over the same frozen ops corpus and identical precomputed vectors:

1. pgvector HNSW — control.
2. pg_pinecone native — local Pinecone engine inside PostgreSQL.
3. pg_pinecone remote — Pinecone serverless engine.

The existing managed Pinecone integration remains the incumbent end-to-end reference: index termux-knowledge, namespace repo-docs, integrated model llama-text-embed-v2, region aws/us-east-1. It is reported separately because the existing client sends text through integrated inference, not the shared vector matrix used by the storage-only arms.

## Run gates

- PostgreSQL 17, pgvector, pg_pinecone, and immutable image/source provenance.
- Frozen corpus manifest, embedding model@version, vector dimensions, distance metric, and query/gold-evidence set.
- Isolated disposable database and remote namespace/index, with current account quota and explicit spend ceiling.
- Database-instance identity contract compatible with the canonical EXPERIMENT schema.

The campaign has no run records. Dispatch, index creation, external writes, and production routing changes remain disabled until every preflight gate is closed.
