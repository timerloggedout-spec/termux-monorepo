# ade-kai9000 (development / ADE subset)

Development-only integration of KAI-9000 into the Fully Automated Agentic Development Environment.

**In scope:** coding skills, MCP templates for filesystem/github/sqlite/notion, product-builder workflows, system prompt layers that are *not* crypto-oracle.

**Out of scope:** Hermes trading agents, Binance/Polymarket MCP, morning_crypto_brief, CRYPTO ORACLE prompt layers — those live under `_1-Projects/a/kai9000-crypto/` (sparse pointer only).

All model calls from skills and workflows **must** go through `llm-api-hub` (or multi-ai-cli backends). No direct provider keys in ADE skills.

See `docs/ADE_KAI9000_SPLIT.md`.
