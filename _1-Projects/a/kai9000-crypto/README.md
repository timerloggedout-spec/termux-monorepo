# kai9000-crypto (reference only)

**Crypto-facing slice of KAI-9000.**  
This directory is a **pointer / sparse-checkout target**, not the live ADE tree.

## Why separate?

The Fully Automated Agentic Development Environment (ADE) must stay clean of:

- Hermes trading agents
- Binance / Polymarket / Bybit MCP servers
- crypto-portfolio-monitor skill
- morning_crypto_brief / tdd_crypto_loop workflows
- CRYPTO ORACLE layers in the system prompt

Those live upstream and are pulled here only when needed for isolated experiments.

## Upstream

See `SOURCE.txt`.

Primary upstream (as of this split):

- https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator

## Sparse checkout recipe

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator.git \
  kai9000-crypto-src
cd kai9000-crypto-src
git sparse-checkout set \
  skills/custom \
  integrations/hermes \
  workflows \
  system_prompts \
  mcp_config
# then copy or symlink only the crypto-relevant pieces into this folder
```

## ADE side

Development skills, generic MCP, product/research workflows, and the llm-api-hub live in the main monorepo.  
NexusCLI routes all model calls through `multi-ai-cli` or `llm-api-hub` — never direct keys.
