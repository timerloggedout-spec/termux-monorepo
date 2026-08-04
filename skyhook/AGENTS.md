# Agents — skyhook

**Primary agent:** [Grok](https://x.com/grok) · [grok.com](https://grok.com) · xAI
**Co-agent:** Jules (Google) for cloud coding sessions
**Device:** BLU B160V Termux — `research/DEVICE_B160V.md`

## Signature

See `SIGNATURE.md`. All Grok-authored pushes include:

```
Agent: Grok
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
```

GitHub committer may be `timerloggedout-spec` (PAT). Semantic author is Grok.

## Ownership

- **Grok | Jules** own implementation. Devin/Vercel out of credit — do not block on them.
- Operator is **not** assignee except temporary `termux-smoke` cherry-picks until automated.
- Grok is not a Linear teammate → `**Agent: Grok | Jules**` at top of issue bodies.

## Gate spine

`feature/*` → **master-staging** (repo-gate) → **termux-smoke** → **master**

## Templates

Forks are **templates**: use directly (CI/host) **or rewrite** into HOME Python/stdlib systems. Do not install Bun/Node/cargo as on-device doctor dependencies.

## Jules-first

Antigravity deferred. Prefer MCP protocol + thin `bridge/http_client.py` over shipping Bun CLI on the phone.

## Claim tasks

Edit `tasks/queue/*.yaml` status/owner; PR with `Implements: SKYHOOK-N` / `TER-N`.
