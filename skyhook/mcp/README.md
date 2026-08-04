# Jules MCP (skyhook)

## Goal

HOME agents call Jules via MCP. Keys only in env / secret stores.

```json
{
  "mcpServers": {
    "jules": {
      "command": "npx",
      "args": ["-y", "@google/jules-mcp"],
      "env": { "JULES_API_KEY": "${JULES_API_KEY}" }
    }
  }
}
```

Prefer patterns scavenged from `jules-mcp-server_fork` + `jules-dispatch-cli_fork` once private repos are verified.

Termux MCP (device control) stays on monorepo PR #7 track — complements Jules, does not replace it.
