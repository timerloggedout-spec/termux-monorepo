# Remote Termux MCP Template

> **Purpose:** Provide a minimal, reproducible template for running the [`xlisp/termux-mcp-server`](https://github.com/xlisp/termux-mcp-server) server in an Android Termux environment while an MCP client launches it through SSH. The template contains no device address, tunnel hostname, port, key, access token, model, virtual environment, cache, or session export.

## Design Decision: Configuration, Not a New Submodule

This template **must not add another submodule**. The repository already treats substantial third-party source as external or submodule-managed content, while this change contains only documentation and one small on-demand health script. A second checkout of the upstream MCP source would duplicate source and runtime state on the constrained device, conflict with the lean-monorepo rules, and add a moving dependency to an operational guide.

The active device environment may use a pinned fork under an isolated worktree when development changes are required. This template remains source-agnostic: it documents how a client should launch whichever reviewed, pinned MCP checkout is selected by the operator.

| Component | Keep in the repository | Keep outside the repository |
|---|---|---|
| Operating procedure | This document | — |
| Health monitoring | `scripts/termux-resource-snapshot.sh` | Optional generated logs |
| MCP source code | Refer to the reviewed upstream or pinned fork | Isolated worktree or existing managed submodule |
| Python runtime | — | Per-worktree virtual environment |
| SSH private key and known hosts | — | `~/.ssh/` |
| Temporary tunnel endpoint | — | Local state only; refresh after reconnect |

## Minimal Device Prerequisites

Install only the packages required by the selected MCP workflow:

```bash
pkg install python termux-api openssh
```

Install the companion **Termux:API** Android application and grant the permissions required by the tools you intend to use. Keep the MCP checkout and virtual environment in an isolated worktree location rather than the main monorepo checkout.

```bash
WORKTREE_BASE="/data/data/com.termux/files/termux-mcp-worktrees"
MCP_WORKTREE="$WORKTREE_BASE/termux-mcp-connector"
MCP_DIR="$MCP_WORKTREE/smods/termux-mcp-server_fork"
VENV_DIR="$WORKTREE_BASE/runtime/termux-mcp-connector/venv"

"$VENV_DIR/bin/python" "$MCP_DIR/termux_mcp_server.py"
```

## MCP Client Transport Contract

The upstream server uses standard input/output. A remote MCP client must therefore invoke the remote Python process through SSH rather than run the server in its own local sandbox. The values below are placeholders and must never be committed with live values.

```json
{
  "mcpServers": {
    "termux-mcp": {
      "command": "ssh",
      "args": [
        "-i", "~/.ssh/termux_mcp_client",
        "-o", "IdentitiesOnly=yes",
        "-p", "<TUNNEL_OR_SSH_PORT>",
        "<TERMUX_USER>@<TUNNEL_OR_LAN_HOST>",
        "<TERMUX_VENV>/bin/python",
        "<MCP_CHECKOUT>/termux_mcp_server.py"
      ]
    }
  }
}
```

Use a key-only Termux `sshd` configuration. If the phone is not on the same network as the client, use a separately approved SSH transport. Treat temporary public tunnel endpoints as ephemeral operational state; do not add them to Git, documentation examples, shell history, or long-lived configuration files.

## Resource Guardrails

Run the tracked, read-only snapshot before starting heavy agent, model, indexing, or export work.

```bash
./scripts/termux-resource-snapshot.sh
```

The script reports memory, swap, storage, and the largest resident processes. It emits warnings when available memory, free swap, or free storage is low. It does not start or stop services, modify swap, clear caches, terminate processes, or write logs.

> **Current Android swap policy:** do not create a new swapfile blindly. First inspect existing swap and storage headroom. On an Android device, `swapon`/`mkswap` availability does not imply that creating a new `/data/swapfile` is safe or permitted. A large swapfile consumes scarce flash storage, can increase wear, and may fail under Android storage policy. Use the snapshot to establish need before any separately approved remediation.

## Lean Operations Checklist

1. Keep the main checkout limited to source, tracked configuration, and active documentation.
2. Keep virtual environments, MCP checkouts, tunnels, keys, caches, models, session exports, and generated logs outside the tracked checkout.
3. Use an isolated Git worktree for changes. Do not branch from a dirty home checkout.
4. Run `./scripts/termux-resource-snapshot.sh` before a heavy task and after a significant session.
5. Archive large artifacts remotely, then clean ignored caches only after verifying they are not active dependencies.
6. Rotate or recreate temporary tunnel endpoints after reconnect; update the active connector out of band rather than committing them.

## References

[1]: https://github.com/xlisp/termux-mcp-server "xlisp/termux-mcp-server"
[2]: https://github.com/termux/termux-api "Termux:API"
[3]: https://github.com/termux/termux-services "Termux services"

[1]: https://github.com/xlisp/termux-mcp-server
[2]: https://github.com/termux/termux-api
[3]: https://github.com/termux/termux-services
