# Bifrost Gateway Integration — RECON + Reconcile Plan

**Status:** RECON complete · proposal draft · dual-gate pending  
**Author:** Grok (Administrator)  
**Date:** 2026-09-18  
**Forks:**
- https://github.com/timerloggedout-spec/bifrost_fork (upstream: maximhq/bifrost)
- https://github.com/timerloggedout-spec/bifrost-benchmarking_fork (upstream: maximhq/bifrost-benchmarking)

## What Bifrost is

High-performance AI gateway (Go):
- Unified OpenAI-compatible API across 20+ providers
- Claimed ~11 µs overhead @ 5k RPS (vs LiteLLM etc.)
- Native **MCP gateway** (tool calling, agent loop, Starlark code-mode)
- Semantic caching, governance (virtual keys / budgets), plugins, UI
- Drop-in for OpenAI / Anthropic / GenAI / LiteLLM / LangChain SDKs
- Apache-2.0

Benchmarking companion:
- `benchmark.go` (Vegeta rate + concurrent-users modes)
- `mocker/` (fasthttp mock providers — free, reproducible)
- `hitter/` (realistic Bifrost load)
- `mcp-code-mode-benchmark/` (token/latency/pass-rate for MCP code mode)

## Fit to termux-monorepo

| Monorepo surface | Bifrost value |
|------------------|---------------|
| mcp-hub / mcp-docker | Bifrost is itself an MCP gateway + hosts MCP servers; catalog candidate |
| rate-limit-rotation / OpenRouter / OX Alpha | Alternative/failover gateway path; multi-provider + budget governance |
| provider-capabilities.md | Concrete implementation of identity + streaming + tools + health |
| Moneyball / #337 continuous eval | Independent gate for latency/throughput/success evidence |
| Termux / Android agents | Lightweight binary / Docker / NPX; URL-only clients can hit remote gateway |
| help-wanted / external eval | Upstream maximhq/bifrost is active FOSS; our forks are evaluation surface |

**Not a fit for:** wholesale submodule of the entire multi-module Go workspace into master (size + dual-gate risk). Prefer thin integration.

## Harmonious reconciliation (preferred)

1. **Registry row** — add `bifrost-gateway-integration` to `docs/proposals/registry.yaml` (this PR / follow-up).
2. **Catalog entry** — extend `mcp-hub/catalog.json` with a `bifrost` host (self-host Docker / NPX or future Vercel/edge note). Status starts `evaluation`.
3. **Provider-capabilities** — document Bifrost as a capability-bearing gateway (streaming, tools/MCP, failover, budgets).
4. **Gitlink / pin (optional, later)** — if we need source-level reference, shallow pin under `refTemplates/` or `mcp-hub/` analogous to existing forks; never init in gates.
5. **Benchmarking lane** — keep `bifrost-benchmarking_fork` as external evidence tool. Run against:
   - Bifrost (self)
   - current OpenRouter / OX Alpha paths
   - mcp-hub relative endpoints
   Produce `results.json` → feed Moneyball / ACTION-EFFECTIVENESS style evidence. Use mocker for cost-free runs.
6. **No HITL YOLO** — any monorepo change stays small green PRs; dual-gate (`repo_gate.py` + `termux_smoke.py`) before merge. Upstream PRs to maximhq only via help-wanted-execute if we contribute fixes.

## Non-goals (this cycle)

- Replacing OpenRouter/OX Alpha routing wholesale
- Merging Bifrost UI or full enterprise cluster config into monorepo
- Force-pushing either fork’s default branch
- Comment-storm on upstream

## Evidence already gathered

- bifrost_fork default SHA: `246ff5698b4606d06fa0506584cb38db5f1b4923`
- bifrost-benchmarking_fork default SHA: `2c416fb234bf4abac25cf61f4470fc2528362afd`
- AGENTS.md present and high-signal (agent-oriented layout, pool/debug tags, BifrostContext rules)
- Go workspace requires modern Go (go.work notes 1.27 in fork AGENTS; go.mod in bench shows 1.24.1)
- Zero existing code hits for “bifrost” in termux-monorepo (search 2026-09-18)

## Next discrete actions

- [ ] Land this RECON + registry update (small PR)
- [ ] Catalog + provider-capabilities delta (follow-up PR)
- [ ] Optional: one mocker + benchmark smoke against local Bifrost in CI or Codespace (evidence artifact)
- [ ] Adaptive-wait: dual-gate green before any promote

BIUDL. Agent-Identity: Grok (Administrator)
