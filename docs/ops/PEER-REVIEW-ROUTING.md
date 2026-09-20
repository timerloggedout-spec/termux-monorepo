# Peer Review Routing — Copilot is NOT primary

**Updated:** 2026-09-20 (operator correction)

## Primary operator route

**Grok Administrator + dual-gate evidence** (`termux-smoke` + repo/hygiene gate).

## Peer tier (optional / parallel)

| Peer | Use |
|------|-----|
| CodeRabbit | Default volume review + autofix (`.coderabbit.yaml`) |
| Qodo | Optional quality |
| Devin | Optional when trial/quota alive |
| Jules | continue-only summon via auto-resolve |
| **Copilot** | **Optional peer only** — never hardcode as required primary |

## Why this was wrong before

- `request_copilot_review` MCP convenience looked like a primary step in operator sessions.
- B3 agentic workflows use `copilot-requests: write` for **inference quota**, which is not the same as promote authority.
- `peer-review-orchestrator` waits on many bots including Copilot; wait ≠ primary.

## Rule for agents

Prefer CodeRabbit + dual-gate. Call Copilot review only when explicitly useful. Never block promote solely on Copilot.

Agent-Identity: Grok (Administrator)
