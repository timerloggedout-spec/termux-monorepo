# Live Termux bridge

The repository now has a **live-bridge compatibility lane** for the device-side Pinggy reverse-SSH transport.

## Runtime contract

The device publishes the current ephemeral endpoint to:

`ops/termux-bridge/current.json`

The file contains only connection metadata:

- Pinggy hostname
- forwarded TCP port
- Termux SSH username
- local target `127.0.0.1:8022`
- active status

It never contains an SSH private key, GitHub token, Pinggy account credential, OTP, or MCP secret.

Because Pinggy free TCP endpoints rotate/expire, the device must run:

`scripts/termux/publish-pinggy-endpoint.sh`

after every tunnel reconnect. The supplied installer schedules an idempotent five-minute refresh as Termux job **43109**, leaving existing jobs **43107** and **43108** untouched:

`scripts/termux/install-pinggy-publisher-job.sh`

## Collaborator connection

From a trusted workstation with the authorized SSH key:

```bash
./scripts/termux/connect-live-bridge.sh
```

The connector reads the current endpoint from GitHub using `gh`; it does not hard-code a Pinggy hostname or port.

Set the private key out of band:

```export TERMUX_MCP_SSH_KEY="$HOME/.ssh/termux_mcp_client"```

The key must correspond to a key authorized by the Termux `sshd`.

## GitHub Actions health lane

`.github/workflows/termux-bridge-connect.yml` provides an on-demand, fixed health check. Configure these repository secrets:

- `TERMUX_MCP_SSH_PRIVATE_KEY`
- `TERMUX_MCP_KNOWN_HOSTS`

The workflow refuses TOFU and does not accept arbitrary shell commands from workflow inputs.

## Activation on the device

After pulling the current repository:

```bash
cd "$HOME/termux-monorepo"
chmod 700 scripts/termux/*.sh
./scripts/termux/install-pinggy-publisher-job.sh
```

The first publish will fail harmlessly if the reverse tunnel has not established yet; the five-minute job retries automatically.

## Security boundary

This lane makes the **transport address discoverable**, not the credentials. A Pinggy endpoint is ephemeral public network metadata and must not be treated as an authentication mechanism. The Termux SSH server remains key-authenticated, and host-key verification must be pinned by clients.

The existing `hub_mcp` capability policy remains the authorization boundary for MCP operations; the reverse SSH transport must not become a free-form command router.
