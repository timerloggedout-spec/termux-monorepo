# Pinecone Vector Database and PostgreSQL comparison sources

Pinecone is the managed vector-database treatment already integrated into this repository through scripts/pinecone/. The related pg_pinecone project is an Apache-2.0 PostgreSQL extension with native and Pinecone-remote engines; pgvector is the PostgreSQL baseline. The official Pinecone Developer MCP is an optional developer interface, separate from the existing database adapter.

## Source pins

| Component | Source | Reviewed revision | License / state |
|---|---|---|---|
| Managed Pinecone | https://docs.pinecone.io/ | vendor-managed documentation surface | vendor service |
| pg_pinecone | https://github.com/pinecone-io/pg_pinecone | d860f6fd3a21733d75ed2cde2b5b5e71e79bd3ac | Apache-2.0; custom-fork smod pending |
| pgvector | https://github.com/pgvector/pgvector | 1d56580cda45d20b6b197fbe325fb0f6301e33cd | PostgreSQL License; comparison baseline |
| Pinecone Developer MCP | https://github.com/pinecone-io/pinecone-mcp | 275aa5cb8b4dc7fb6471f3483cb05191c338b61c | Apache-2.0; optional reference |

## Repository consumer

- REST client: scripts/pinecone/pinecone_client.py
- Corpus/chunk sync: scripts/pinecone/knowledge_sync.py
- Workflow: .github/workflows/pinecone-knowledge.yml
- Tests: tests/test_pinecone_knowledge.py
- Current index target in code: termux-knowledge

The Pinecone account/index state and current live usage remain runtime observations; this metadata records references while account refreshes and mutations remain separate operations.

## Experiment

The controlled comparison is pre-registered at experiments/doe/pinecone-vector-store/DESIGN.json. Its offline evaluator lives at scripts/doe/pinecone_vector_store_metrics.py, with synthetic ranking fixtures under tests/fixtures/. The storage-only comparison requires identical precomputed vectors and query vectors across Pinecone serverless, pgvector HNSW, pg_pinecone native, and pg_pinecone remote. The integrated-inference path is a separately labeled end-to-end arm.
