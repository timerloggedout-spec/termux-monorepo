# Pinecone recon — 2026-10-28

Lane: `[MUSEai]@{role:{pinecone-research}}`. Scope: recon only. No signup, no card, no account created.

## 0. Current fleet state (verified firsthand, master @ 2026-10-28)

**Pinecone has NO entry in this repo.** Owner note "Pinecone is in our list" does not map to a repo record:

| Surface checked | Result |
|---|---|
| GitHub code search `pinecone` / `PINECONE` / `pinecone.io` (default branch) | 0 hits each |
| Issue search `pinecone` | 0 |
| `ops/quota/registry.json` | 90 records, 47 provider strings — no pinecone. Nearest: `neon.*` (data lane), `supabase.*` (data), `render.postgres_free` (data) |
| `ops/quota/allocations.json`, `.github/connectors/llm_providers.yaml`, `ops/delphi/surfaces.json`, `ops/delphi/research-sources.json`, free-tier value board/feed, `provider-recon.json` | no pinecone |

So pg_pinecone (feed item 2026-10-27) maps onto the existing **Postgres/pgvector lane**, not a Pinecone provider entry. Any future adoption starts with a registry record — none exists to update.

Existing pgvector consumer of record: **HindSight** (`docs/ops/sessions/HINDSIGHT.md`) — agent memory over PostgreSQL + pgvector, HNSW index, `recall(bank_id, …)` scoped retrieval; currently run remote (`api.hindsight.vectorize.io`), fork `timerloggedout-spec/hindsight`.

## 1. pg_pinecone

Vendor sources: docs.pinecone.io/guides/pg-pinecone/{overview,quickstart}, docs.pinecone.io/release-notes/2026, github.com/pinecone-io/pg_pinecone.

- **What:** open-source Postgres extension; brings Pinecone's search engine to existing pgvector columns/tables. Queries unchanged (`ORDER BY embedding <=> $1` works on every engine).
- **Engines:** `pgvector` (stock index) · `native` (default; IVF+RaBitQ, runs inside Postgres, **no account, no network**) · `remote` (search served by a Pinecone cloud index; Postgres keeps all rows; switch native↔remote = one SQL call, reversible).
- **Filtered search (headline):** with a filter column, `native` applies the filter **during** search — a narrow tenant/user scope still returns a full `LIMIT` set, where graph indexes (HNSW post-filtering) can return fewer rows.
- **Extras:** BM25 full-text + vector/hybrid from SQL; `embed()` / `rerank()` SQL functions call Pinecone Inference (optional, needs API key).
- **Requirements:** PostgreSQL **17 or 18**, **superuser**, **pgvector installed** (uses its `vector` type/operators); self-managed server only. `remote` + full-text also need a server setting (`shared_preload_libraries` class). Install: prebuilt release archives (Linux x86_64 [x86-64-v3, glibc ≥2.39] / arm64, macOS arm64), Docker image, or source build.
- **Version / maturity:** released **2026-10-27** (vendor changelog); quickstart archive = **0.11.0** — pre-1.0, first release, 1 day old at recon. Treat as evaluate-only.
- **License:** **Apache 2.0** (repo LICENSE).
- **Benchmarks:** vendor-reported only (1M×768d: native index 136 MB vs HNSW 2.0 GB halfvec / 4.1 GB full; build 45 s vs 62/79 s). No independent benchmark found. NOT VERIFIED independently.
- **Repo blocker:** repo Postgres lanes are managed (Neon / Supabase / Render) — superuser + PG17/18 + preload control on those = **NOT ESTABLISHED**. `native` pilot requires a self-managed PG17/18 (or a managed tier proven to allow it).

## 2. Pinecone proper (managed)

Vendor sources: pinecone.io/pricing (read 2026-10-28), docs.pinecone.io/guides/operations/mcp-server, docs.pinecone.io/admin/billing/*, docs.pinecone.io/guides/manage-cost/understanding-cost.

- **API:** managed vector DB, API-key auth, official SDKs; serverless on-demand indexes (dense/sparse/full-text), namespaces, integrated embedding + reranking (Inference), Assistant.
- **Official MCP server: YES.** `@pinecone-database/mcp` (stdio, Node/npx, `PINECONE_API_KEY` env). 9 tools: `search-docs` (works without a key), `list-indexes`, `describe-index`, `describe-index-stats`, `create-index-for-model`, `upsert-records`, `search-records`, `cascading-search`, `rerank-documents`. Separate per-Assistant MCP (remote endpoint or self-hosted Docker) also exists.
- **Free tier — Starter, vendor pricing page:** $0; 2 GB storage; 2M write units/mo; 1M read units/mo; 1 GB egress/mo; ≤5 indexes; 100 namespaces/index; 1 project; 2 users; AWS `us-east-1` only; Inference incl. 5M embed tokens/mo (listed models), 500 bge-reranker requests/mo; Assistant incl. 1 GB / 500k in / 300k out tokens/mo.
- **Paid floors:** Builder $20/mo flat (10 GB, 5M WU, 2M RU, 10 indexes); Standard $50/mo min (PAYG $0.33/GB, $4–4.50/M WU, $16–18/M RU; 21-day / $300 trial); Enterprise $500/mo min.
- **Card gate:** vendor docs show card entry **only at upgrade** to a paid plan (Billing > Plans > enter card); Standard trial = "$300 / 21 days, without any up-front payment". An explicit vendor statement "no credit card required for Starter signup" was **NOT FOUND** → card-free Starter = NOT ESTABLISHED vendor-explicit; no card step is documented before paid upgrade.

## 3. Fit for THIS repo

| Candidate consumer | Verdict |
|---|---|
| **HindSight memory recall** (PG+pgvector, HNSW, per-`bank_id` scoped recall) | **Only concrete fit.** `native` filtered search targets exactly bank-scoped recall returning full result sets. Gated: HindSight currently runs as remote cloud API; benefit lands only if/when a self-hosted PG17/18 HindSight store exists (see §1 blocker). No action now. |
| Delphi / research-silo retrieval | **None yet.** Retrieval today = JSON feeds (`delphi-rfp-feed.json`, segments) + grep; no embedding pipeline, no vector store. Candidate only after the known Delphi ingestion build exists. |
| Memory / knowledge search (docs, ICM) | **None yet.** No embeddings infra in repo (code search: embeddings appear only in HindSight + proposals). |
| Code search | **None.** GitHub code search + grep only; no vector code index, no named consumer. |
| Pinecone cloud (`remote` engine / managed indexes) | **No consumer justifies a new managed dependency today.** It is the documented escalation path if a self-hosted pg_pinecone `native` table outgrows one server — that precondition does not exist yet. |

**Bottom line:** adopt-nothing now. Watch item = pg_pinecone maturity (pre-1.0, day-old) + a self-managed PG17/18 surface appearing (e.g. a self-hosted HindSight store). If that surface lands, `native` is a no-account, no-card, Apache-2.0 drop-in over the existing pgvector columns — re-run this recon then. Pinecone cloud signup is not needed for that path.

---

## State update — 2026-10-28 (account-creation lane, owner-ordered Starter init)

The §5 "adopt-nothing / no signup" verdict was superseded by owner order 2026-10-28 for cloud Starter only. Outcome:

- **Account PRE-EXISTED** — existence recon via fleet Gmail returned no vendor mail (false negative); firsthand console evidence: organization "LoggedOut's Org", project "Default", a `default` API key created 2025-09-28, and an existing serverless index `swaying-dogwood` (1024-dim, cosine, AWS us-east-1, Ready). No new org/project created.
- **Plan: Starter, marked Current + Free** (console Settings → Subscription plans, verified 2026-10-28). Usage at init: 0/1M RU, 0/2M WU, 0GB/2GB storage, 0GB/1GB egress. **No payment method added or requested at any step** — the card-at-Starter question is now answered firsthand for this account: none demanded.
- **Key:** new `fleet` key (All permissions, project Default) harvested via the sealed-box PAT route into the Actions secret store as `PINECONE_API_KEY` (store count 52, 2026-10-28T13:21:09Z). **Verified live:** `GET api.pinecone.io/indexes` with the key = HTTP 200, returned `swaying-dogwood`. Names only in records; value lives only in the secret store.
- **Registry:** v3 derive for platform `pinecone` = `GentleWalnut50` — derived per protocol but **not consumed** (no signup form forced a name; the account predates it). Flagged for the registry lane to record.
- **Quota registry:** `pinecone.*` records (storage, write_units, read_units, indexes, egress) added in the same PR as this update, live-check = list-indexes with PINECONE_API_KEY.

## 4. Integration — LANDED (2026-10-28, owner order "Integrate")

State change supersedes §3's "no consumer yet" for knowledge search:

- **Client:** `scripts/pinecone/pinecone_client.py` — stdlib-only REST client (control + data plane), API version `2025-10`, key from `PINECONE_API_KEY` env only, never printed.
- **Consumer:** `scripts/pinecone/knowledge_sync.py` — semantic search over the repo knowledge base (`docs/ops/*.md`). Index `termux-knowledge` (integrated inference, `llama-text-embed-v2`, aws/us-east-1 = Starter region), namespace `repo-docs`. Chunk ids are content hashes → re-sync is idempotent. Modes: `sync` (ensure index + upsert + smoke searches), `search "<query>"`, `observe` (quota reading: indexes + record counts).
- **Runner:** `.github/workflows/pinecone-knowledge.yml` — workflow_dispatch + monthly schedule (1st 05:37Z) + push on the integration paths. Runs on GitHub (our-account surface); the VM hosts nothing. Evidence = run step summary + artifact.
- **Tests:** `tests/test_pinecone_knowledge.py` — fake transport, no network (create-once, NDJSON batching, search parse, content-addressed chunk ids, corpus build).
- **Unchanged:** HindSight remains the pg_pinecone candidate (still gated on a self-managed PG17/18 store); Delphi ledger store rejection stands; the pre-existing `swaying-dogwood` index is untouched by this integration.
