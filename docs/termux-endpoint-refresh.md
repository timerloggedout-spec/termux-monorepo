# Termux MCP Endpoint Refresh

The BLU B160V owns the Pinggy tunnel lifecycle. The device starts one idempotent tunnel keeper from Termux:Boot and checks it with Android JobScheduler every 15 minutes. The existing six-hour resource sentinel remains independent.

Pinggy free TCP tunnels are temporary: they expire after 60 minutes and receive a new public endpoint after reconnecting. Therefore, the endpoint is treated as runtime metadata, never committed to Git, and never used as a credential.

## GitHub publication

The device publisher writes two repository Actions variables in `timerloggedout-spec/termux-monorepo`:

- `TERMUX_MCP_ENDPOINT`, containing the current `tcp://host:port` value.
- `TERMUX_MCP_ENDPOINT_UPDATED_AT`, containing an ISO-8601 timestamp.

Publication is skipped when the endpoint has not changed or when GitHub CLI authentication is unavailable. The publisher never prints or sends a private key, token, `.env` value, or shell command containing credentials.

The B160V must have GitHub CLI authentication with permission to manage repository Actions variables. Authenticate locally on the device with the GitHub device flow; do not paste a token into chat or commit it:

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status
gh variable set TERMUX_MCP_ENDPOINT --repo timerloggedout-spec/termux-monorepo --body tcp://example.invalid:1
```

The last command is only a syntax test and should not be run with a placeholder in production. The installed publisher derives the real endpoint from the local reverse-SSH log.

## GitHub Actions role

GitHub Actions reads the variables and reports freshness. It does not start, stop, or discover the phone tunnel, and it does not receive an SSH private key. The device remains the single writer for endpoint state. A stale or missing variable is a health signal, not permission to execute arbitrary commands on the device.

## Recovery

Inspect the device without restarting a live tunnel:

```sh
ps -ef | grep -E '[p]inggy|[s]sh.*free\.pinggy'
tail -20 "$HOME/.local/state/termux-mcp/reverse-ssh.log"
termux-job-scheduler --pending
gh auth status
```

Only one Pinggy SSH process should be present. If the endpoint changes, the publisher updates the repository variable automatically after valid GitHub authentication is restored. The Manus connector remains a separate client configuration and must be refreshed through its supported connector-update confirmation flow; GitHub variables do not silently alter that connector.

## Security boundaries

The endpoint is public routing metadata. It is not a substitute for a private transport. Do not publish private keys, Pinggy tokens, GitHub tokens, or arbitrary command text. The structured Termux job protocol must use named capabilities, schema validation, replay protection, bounded execution, and redacted result envelopes before any GitHub-triggered device operation is activated.
