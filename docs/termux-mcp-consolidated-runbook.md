# Termux MCP, Pinggy, GitHub, and DeepCLI Consolidated Runbook

**Scope:** BLU B160V Android/Termux environment, the `termux-mcp_fork` lane, Pinggy reverse SSH transport, the `timerloggedout-spec/termux-monorepo` project, and the local DeepCLI/DeepSeek work. Vercel, Render, Tailscale, submodules, and unrelated MCP build lanes remain separate unless explicitly activated later.

**Status at consolidation:** The B160V MCP server is reachable through the fallback Pinggy allocation `johhj-73-41-238-183.run.pinggy-free.link:41095`. MCP initialization identifies `termux-control` version `1.29.0` using protocol `2024-11-05`. The endpoint is temporary and must not be committed or treated as a credential.

## Operating architecture

The B160V owns tunnel lifecycle. Termux:Boot launches one idempotent keeper, and Android JobScheduler invokes the keeper every 15 minutes. The keeper starts a single `ssh -R0:localhost:8022 tcp@free.pinggy.io` process, records the dynamic allocation in the existing reverse-SSH log, publishes endpoint metadata when GitHub authentication is valid, and sends a notification only when the Pinggy state changes.

The existing six-hour resource sentinel remains independent. It reports memory, swap, and storage pressure through Termux:API and notifies only when pressure is detected. The Pinggy notifier uses a separate notification ID so tunnel state and resource pressure remain distinguishable.

GitHub Actions is a validation and coordination plane, not the tunnel owner. A future approved outbound job flow is:

```text
B160V boot / JobScheduler
  -> one Pinggy keeper
  -> optional endpoint metadata publication

GitHub Actions
  -> validates endpoint freshness and reviewed job/result schemas

Termux outbound worker
  -> fetches approved structured jobs
  -> validates named capabilities and approval level
  -> runs one bounded local operation
  -> returns a redacted result envelope
```

The archived structured-job process in the repository is marked stale and explicitly says not to execute it. No arbitrary shell proxy, automatic DeepCLI execution, or GitHub-triggered device operation is enabled by this runbook.

## Device resources and selected components

| Resource or component | Role | State or boundary |
|---|---|---|
| BLU B160V Android phone | Local execution host | Connected through Termux; resource-constrained |
| Termux | Shell, Python, SSH, Git, local MCP runtime | Active |
| Termux:API | Notifications, battery/Wi-Fi and resource-related Android integration | Existing resource sentinel uses notifications |
| Termux:Boot | Starts the keeper at device boot | `~/.termux/boot/00-manus-termux-mcp` |
| Android JobScheduler | Periodic deterministic checks | Job `43108` every 15 minutes; job `43107` every six hours |
| Shizuku Plus+ | Android privileged bridge | Installed and Wi-Fi setup reported; not required by the current MCP transport |
| Tasker | Android automation option | Installed; not required by the current keeper |
| Pinggy SSH reverse tunnel | Temporary recovery/debug transport to Termux port 8022 | Free tunnel expires after 60 minutes and changes endpoint |
| Dedicated SSH identity | Manus-to-Termux client authentication | `/home/ubuntu/.ssh/termux_mcp_manus`; never print or transfer through GitHub |
| `termux-mcp-server_fork` | Canonical MCP server | Runs from the Termux worktree virtual environment |
| `termux_mcp_server.py` | MCP stdio entry point | Reports `termux-control` v1.29.0 |
| `term_mcp_deepseek` | Local DeepSeek/MCP-related checkout | Existing device resource; not automatically executed |
| `deepcli` | Local DeepCLI client and session store | Existing device resource; no blanket updater or daemon enabled |
| GitHub CLI (`gh`) | Device-side endpoint publisher and future outbound coordination | Current B160V token was invalid; re-authentication required |
| GitHub Actions | Validation, freshness reporting, reviewed coordination | Feature branch contains the freshness workflow; default branch does not yet include it |
| Tailscale | Candidate private production transport | Not activated in this lane; preferred over free Pinggy for durable access |
| Vercel and Render | Separate MCP/build portals | Deliberately untouched |
| Termux home checkout | User workspace | Dirty with unrelated modifications; do not run `git add .`, `git clean`, reset, or blanket pulls |

## Installed device automation

### Boot

`~/.termux/boot/00-manus-termux-mcp` runs:

```sh
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
exec "$HOME/.local/bin/termux-pinggy-keeper"
```

### Keeper

`~/.local/bin/termux-pinggy-keeper` uses a lock directory, validates the stored PID, starts a single tunnel when needed, invokes the endpoint publisher, and invokes the status notifier. It does not kill unrelated processes and does not print credentials.

### Endpoint publisher

`~/.local/bin/termux-pinggy-publisher` derives the newest `tcp://host:port` line from the reverse-SSH log. When `gh auth status` succeeds, it writes:

- `TERMUX_MCP_ENDPOINT`
- `TERMUX_MCP_ENDPOINT_UPDATED_AT`

to repository Actions variables. When authentication is invalid or the endpoint is unchanged, it exits without changing anything.

### Pinggy status notifier

`~/.local/bin/termux-pinggy-status` stores the last state in:

```text
~/.local/state/termux-mcp/pinggy-status
```

It uses notification ID `43109` and sends only state changes:

- **Pinggy connected** with the active endpoint.
- **Pinggy disconnected** when no active process and endpoint are available.
- A new endpoint produces a new connected-state notification.

This is intentionally analogous to the existing `Termux resource pressure` notification, but it does not repeat every 15 minutes while the state is unchanged.

## Current scheduled jobs

```text
Job 43108: ~/.local/bin/termux-pinggy-keeper
Interval: 900000 ms (15 minutes)
Persisted: yes
Battery not low: yes

Job 43107: ~/.local/bin/termux-resource-sentinel
Interval: 21600000 ms (6 hours)
Persisted: yes
Battery not low: yes
```

## GitHub work

The isolated feature branch `feat/termux-endpoint-refresh` contains commit `b2eea8f61cbe5a7fb2e3a8ae93805c2bab97940c` with:

- `docs/termux-endpoint-refresh.md`
- `.github/workflows/termux-endpoint-status.yml`
- this consolidated runbook

The workflow validates endpoint variable presence, format, and age. It does not receive private keys, start tunnels, or execute arbitrary device commands. The workflow is not on the default branch yet, so its scheduled checks are not active until the branch is reviewed and merged.

The sandbox GitHub identity can clone and push repository contents, but its integration token returned HTTP 403 for the Actions-variable API. The B160V `gh` token returned HTTP 401. Therefore automatic endpoint publication is installed but currently inert until the B160V is re-authenticated.

Re-authenticate locally on the B160V with the device flow:

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status
gh api user --jq .login
```

The account must be allowed to manage Actions variables in `timerloggedout-spec/termux-monorepo`. Do not put a token in an issue, commit, shell history, GitHub variable, or chat transcript.

## Recovery and validation

Inspect the device without printing secrets:

```sh
ps -ef | grep -E '[p]inggy|[s]sh.*free\.pinggy'
tail -30 "$HOME/.local/state/termux-mcp/reverse-ssh.log"
cat "$HOME/.local/state/termux-mcp/pinggy-status"
termux-job-scheduler --pending
gh auth status
```

From the trusted client, extract the newest endpoint from the log, resolve it, test TCP reachability, then validate MCP initialization using the dedicated SSH key and the canonical virtual environment. Never reuse a historical hostname or port without testing it.

A successful MCP initialization returns a result containing:

```json
{
  "protocolVersion": "2024-11-05",
  "serverInfo": {"name": "termux-control", "version": "1.29.0"}
}
```

## Credentials and 2FA material

Issue #184 was reported as containing credentials. Do not retrieve, copy, or use credentials from an issue. Treat any credential posted there as exposed and rotate it through the provider. GitHub tokens, Pinggy tokens, SSH private keys, GPG private keys, and TOTP seeds do not belong in issues, repository variables, logs, or chat.

The supplied project notes listed these possible local 2FA resources for future review:

- `pass` with `pass-otp` and GnuPG.
- Russ Cox’s `rsc/2fa` command-line tool.
- `open2fa`.
- Aegis Authenticator.
- Clockwork: 2FA.
- Tokn MFA.
- Termux:API fingerprint checks.
- Hermes Agent and Droid MCP references.

These are documented as candidate resources only. None is automatically installed or selected by this runbook. A future 2FA implementation must use a local encrypted store, explicit biometric/user approval for critical actions, and no secret transmission through GitHub Actions.

## Security and change boundaries

Do not run a blanket repository update on the dirty Termux home checkout. Use a clean worktree for repository changes. Do not enable arbitrary shell execution through GitHub. Keep the legacy DeepSeek/Flask service out of the MCP path unless separately approved. Prefer a private Tailscale route for durable production access; treat free Pinggy as temporary recovery transport. Never commit endpoint, port, host key, private key, Pinggy token, GitHub token, TOTP seed, or user-specific device identifiers.
