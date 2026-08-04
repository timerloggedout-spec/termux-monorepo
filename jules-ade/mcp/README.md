# MCP wiring (notes only — no secrets)

## Goals

1. Let HOME agents call **Jules** via MCP (`@google/jules-mcp` or scavenged server).
2. Let cloud agents call **Termux** via on-device MCP (see monorepo PR #7).
3. Keep API keys in environment / secret stores — never in git.

## Jules MCP (cloud)

```json
{
  "mcpServers": {
    "jules": {
      "command": "npx",
      "args": ["-y", "@google/jules-mcp"],
      "env": {
        "JULES_API_KEY": "${JULES_API_KEY}"
      }
    }
  }
}
```

On Termux, prefer a local install if `npx` cold-start is painful; still env-only keys.

## Termux MCP (device)

Track PR #7 (`devin/1785650368-termux-mcp-integration`) retargeted to `master-staging`.
When live, cloud orchestrators can reach device FS/shell without Operator babysitting.

## Security

- Jules product-side MCP allowlists third-party servers; our bridge must assume least privilege.
- Doctor must not print key material — only presence booleans.
