# Agents — skyhook

**Device:** BLU B160V Termux ground station (`research/DEVICE_B160V.md`).

## Ownership

- **Agent: Jules | Grok** own implementation. Devin/Vercel out of credit — do not block on them.
- Operator is **not** assignee except temporary `termux-smoke` cherry-picks until automated.
- Grok is not a Linear teammate → put `Agent: Grok|Jules` at top of issue bodies.

## Gate spine

`feature/*` → **master-staging** (repo-gate) → **termux-smoke** → **master**

## Templates

Forks are **templates**: use directly (CI/host) **or rewrite** into HOME Python/stdlib systems. Do not install Bun/Node/cargo as on-device doctor dependencies.

## Jules-first

Antigravity deferred. Prefer MCP protocol + thin `bridge/http_client.py` over shipping Bun CLI on the phone.

## Claim tasks

Edit `tasks/queue/*.yaml` status/owner; PR with `Implements: SKYHOOK-N` / `TER-N`.
