# Jules surface (active)

```text
Termux / agent orchestrator
  → skyhook plan (YAML / bridge.plan_task)
    → Jules MCP or dispatch CLI
      → Jules API (JULES_API_KEY)
        → cloud VM + GitHub source
          → PR (prefer master-staging)
```

## Official

- SDK: `@google/jules-sdk` — `session()`, `all()` fleet
- MCP: `@google/jules-mcp` — create/list/state/reply/diff tools
- Product MCP allowlist (Linear, etc.) — separate from our server
- Free tier often ~15 tasks/day (verify current limits in product settings)

## Env (never commit values)

```text
JULES_API_KEY=
# some community servers also read:
GOOGLE_JULES_API_KEY=
```

## HOME targets

- Default source: `timerloggedout-spec/termux-monorepo`
- Default branch: `master-staging` (skyhook bridge rewrites bare `master`)
