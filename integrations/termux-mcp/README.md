# Termux MCP integration

This integration exposes the fork's 45+ Termux/Android control tools through
MCP. The server must run on the phone in Termux because its tools shell out to
Android, `adb`, and `termux-api`; it cannot run in Devin's cloud VM. Run it
locally on the phone, then connect Devin to it.

## Prerequisites on the phone

Install the required Termux packages:

```bash
pkg install python termux-api android-tools cloudflared openssh
```

Also install the Termux:API app from F-Droid, grant storage access, and
configure device connectivity:

```bash
termux-setup-storage
```

For Android 12+, enable wireless debugging and pair `adb` with the phone as
described by the fork's setup instructions.

## Option A: STDIO over SSH

Start the SSH server in Termux (the default port is 8022):

```bash
sshd
```

In Devin, add a custom MCP using
`devin-custom-mcp.stdio-ssh.json`. Fill in `<PHONE_SSH_USER>`,
`<PHONE_HOST>`, and `<PHONE_TERMUX_DIR>` first. Devin's runtime must be able
to reach the phone over SSH, such as through a publicly reachable host or
tunnel, and SSH key authentication should be configured.

## Option B: HTTP via cloudflared tunnel (recommended)

On the phone, start the SSE server and then the quick tunnel:

```bash
TERMUX_MCP_TRANSPORT=sse ./run.sh
./tunnel.sh
```

Take the `https://*.trycloudflare.com` URL printed by cloudflared and add a
custom MCP in Devin using `devin-custom-mcp.http.json`, replacing
`<TUNNEL_URL>` so the URL is `<tunnel>/sse`.

## Pull-to-local command execution

Pull this monorepo onto the phone, then run the integration locally:

```bash
cd integrations/termux-mcp
export TERMUX_MCP_DIR=/path/to/termux-mcp-server-fork
./run.sh
```

`run.sh` creates `.venv`, installs the MCP dependency, and installs the fork
in editable mode when `TERMUX_MCP_DIR` is set. Override
`TERMUX_MCP_TRANSPORT`, `TERMUX_MCP_HOST`, and `TERMUX_MCP_PORT` as needed.

To add the connection, open Devin → Settings → Connections → Add a custom MCP
(`/settings/connections/custom-mcp`), or use one of the prefilled JSON files
in this directory.
