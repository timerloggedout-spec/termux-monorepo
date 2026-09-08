# kai9000-crypto (product track)

Crypto-facing orchestrator + Hermes — **not** the ADE core.

## Upstream

- https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator
- Fork: https://github.com/timerloggedout-spec/kai9000-orchestrator_fork

See `SOURCE.txt` for pin policy.

## What belongs here

- `integrations/hermes/` (Bybit/Binance agents, scoring, risk)
- Crypto skills (portfolio monitor, oracle workflows)
- MCP: binance, polymarket
- Workflows: morning_crypto_brief, tdd_crypto_loop

## What does **not** belong here

- Generic coding skills → monorepo `.agents/skills/` / archwiz
- LLM HTTP unification → monorepo `llm-api-hub/`
- NexusCLI / multi-ai-cli → monorepo root packages

## Checkout (sparse, depth-1)

```bash
# example — adjust paths
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/timerloggedout-spec/kai9000-orchestrator_fork.git /tmp/kai9000
cd /tmp/kai9000
git sparse-checkout set integrations/hermes skills/custom/crypto-portfolio-monitor \
  workflows/morning_crypto_brief.yaml workflows/tdd_crypto_loop.yaml
```

Or add as optional submodule later under this directory only.

## Model calls

Still route through monorepo **llm-api-hub** / **multi-ai-cli** so OpenRouter + wrappers stay one plane.
