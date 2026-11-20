# ADE vs Crypto — kai9000 split

Upstream: https://github.com/romanyukzhenya82-sketch/kai9000-orchestrator  
Fork: https://github.com/timerloggedout-spec/kai9000-orchestrator_fork

## Principle

| Slice | Where | What |
|-------|--------|------|
| **ADE (dev)** | Monorepo root | Skills useful for coding agents, MCP templates (github/filesystem/sqlite), system prompt core (Zero Law, RED TEAM, subagents without crypto oracle), workflows mapped to Linear/archwiz |
| **Crypto product** | `_1-Projects/a/kai9000-crypto/` | Hermes integrations, crypto-portfolio-monitor, Binance/Polymarket MCP, morning_crypto_brief, tdd_crypto_loop, CRYPTO ORACLE layers |

`_1-q_f/` is **not** used for this pointer (reserved / other work). Use **`_1-Projects/a/`**.

## ADE import set (into monorepo)

From kai9000, **in**:

- skills: `mcp-builder`, `skill-creator`, `agent-architect`, `product-builder-loop`, docx/pdf/pptx/xlsx (if not already covered by local skills)
- `system_prompts/` stripped of mandatory crypto monitoring
- `mcp_config` templates for github, filesystem, sqlite only (paths Termux-aware)
- generic workflow: deep_research → Linear/TER research issues

**Out** (crypto track only):

- `integrations/hermes/**`
- crypto-portfolio-monitor skill
- binance/polymarket MCP entries
- morning_crypto_brief, tdd_crypto_loop as-is

## Crypto pointer layout

```
_1-Projects/a/kai9000-crypto/
  README.md          # how to clone/sparse upstream
  SOURCE.txt         # upstream URL + SHA
  # optional: submodule or sparse-checkout of hermes + crypto skills
```

Do **not** full-recursive submodule the entire orchestrator into monorepo root.

## Model plane

Both tracks call **`llm-api-hub` / `multi-ai-cli`**, not raw keys in skill env.

## Status

- [x] Split documented
- [ ] `_1-Projects/a/kai9000-crypto/README.md` + SOURCE.txt
- [ ] ADE skill import PR (selective)
- [ ] NexusCLI retarget to hub/multi-ai-cli (block merge of DeepSeek-only PR #40 as final architecture)
