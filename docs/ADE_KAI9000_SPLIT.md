# ADE ↔ kai9000 Split

## Goal

Ship a **Fully Automated Agentic Development Environment** (coding skills, MCP templates, product/research workflows, NexusCLI) while keeping **crypto / trading / Hermes / portfolio / Binance / Polymarket** completely isolated.

## Placement rules

| Concern | Location | Notes |
|---------|----------|-------|
| ADE (development-only) | Monorepo root / `ade-kai9000/` or integrated into existing agent paths | Skills for coding, docs, MCP builder, frontend, testing, product-builder-loop (non-crypto), system prompts stripped of CRYPTO ORACLE |
| Crypto-facing kai9000 | `_1-Projects/a/kai9000-crypto/` (or `_qf-1/` if preferred) | **Reference / sparse checkout only** — not a full live copy of trading agents inside the ADE tree |
| llm-api-hub | `llm-api-hub/` at monorepo root | Shared model plane for ADE; crypto side may use its own keys/wrappers if needed |

## Upstream sources

- Development / orchestrator base: https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator  
  (KAI-9000 Multi-Agent Orchestrator — skills, MCP, workflows, Zero-Law prompt)
- Earlier fork reference: https://github.com/timerloggedout-spec/kai9000-orchestrator_fork

## What stays in ADE

- Anthropic + Manus coding/docs skills (pdf, docx, pptx, xlsx, frontend-design, mcp-builder, skill-creator, webapp-testing, …)
- MCP servers useful for development: filesystem, github, sqlite, brave, notion, gmail, gworkspace, …
- Workflows: deep_research, product-builder, TDD loops **without** crypto-specific cron
- System prompt: Zero Law + RED TEAM; **remove or gate** the 6-layer CRYPTO ORACLE
- Subagents: @Architect, @ResearchLead, @ProductBuilder, @MeetingExecutive

## What is referenced only (crypto)

- crypto-portfolio-monitor skill
- morning_crypto_brief / tdd_crypto_loop workflows
- Hermes trading agents, Binance / Polymarket / Bybit MCP
- CRYPTO ORACLE layers in the master prompt
- Obsidian templates that are crypto-brief specific

Pointer lives at `_1-Projects/a/kai9000-crypto/` with:

- `README.md` — purpose + sparse-checkout instructions
- `SOURCE.txt` — upstream URL + pin (commit / tag)

## Policy: sparse depth-1 checkout

When pulling crypto content for local experimentation:

```bash
git clone --depth 1 --filter=blob:none --sparse <upstream> kai9000-crypto
cd kai9000-crypto
git sparse-checkout set skills/custom/crypto-portfolio-monitor integrations/hermes workflows/morning_crypto_brief.yaml ...
```

Never merge trading secrets or live keys into the ADE monorepo.

## NexusCLI contract

NexusCLI **only** calls:

1. `multi-ai-cli/` backends, **or**
2. `llm-api-hub` (OpenAI Chat Completions on :8787)

No direct provider keys inside NexusCLI itself.
