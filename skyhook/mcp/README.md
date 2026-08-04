# Jules MCP (skyhook)

**Agent: Grok | Jules** — prefer this path when Devin is out of credit.

## Primary scavenge source (public)

https://github.com/timerloggedout-spec/jules-mcp-server_fork
See `skyhook/research/TIER1_DISPATCH_MCP.md`.

## Host config (secrets in env only)

```json
{
  "mcpServers": {
    "jules": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "jules_mcp/jules_mcp.py:mcp"],
      "cwd": "/path/to/jules-mcp-server_fork",
      "env": { "JULES_API_KEY": "${JULES_API_KEY}" }
    }
  }
}
```

Alternate official npm surface: `npx -y @google/jules-mcp` with the same env key.

## Tools to map from skyhook.bridge

| skyhook plan field | MCP tool arg |
|--------------------|--------------|
| prompt | create_session.prompt |
| source_repo → Jules source id | create_session.source |
| starting_branch | create_session.starting_branch |
| require_plan_approval | create_session.require_plan_approval |

Follow with `approve_session_plan` / `wait_for_session_completion` / activity list tools as needed.

## CLI alternative (no Bun required on Termux CI)

`jules-dispatch-cli_fork` is agent-first (`--json`, session state machine). Prefer MCP on Python hosts; use dispatch CLI where Bun is available.

Termux on-device control remains PR #7 (separate from Jules cloud MCP).
