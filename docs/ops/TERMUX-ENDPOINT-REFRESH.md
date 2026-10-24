# Termux MCP endpoint refresh (GitHub plane)

**Status:** thin extract — validation only.  
**Device owner:** BLU B160V Termux keeper (`termux-pinggy-keeper`).  
**Transport:** free Pinggy reverse SSH to `localhost:8022` (temporary; prefer Tailscale for production).  
**Protocol:** MCP `termux-control` v1.29.0 / `2024-11-05` when the tunnel is live.

## Boundaries (hard)

- GitHub Actions **does not** start tunnels, hold SSH private keys, or execute arbitrary device commands.
- Endpoint host:port is **public routing metadata**, published as repository Variables:
  - `TERMUX_MCP_ENDPOINT` (`tcp://host:port`)
  - `TERMUX_MCP_ENDPOINT_UPDATED_AT` (ISO-8601)
- Never commit live endpoints, private keys, Pinggy tokens, GitHub tokens, TOTP seeds, or device identifiers.
- Free Pinggy expires ~60 minutes and changes allocation; treat as recovery/debug only.
- Dirty Termux home checkouts: use clean worktrees; never `git add .` / blanket clean/reset.

## Architecture (summary)

```text
B160V boot / JobScheduler (15m)
  -> termux-pinggy-keeper (single ssh -R0:localhost:8022)
  -> termux-pinggy-publisher  (gh variable set when auth valid)
  -> termux-pinggy-status     (notification ID 43109, state-change only)

GitHub Actions (this workflow)
  -> validate format + freshness of published variables
  -> report; do not control the device
```

Resource sentinel (6h, notification separate from Pinggy) remains independent.

## Workflow

`.github/workflows/termux-endpoint-status.yml`

- Schedule: every 30 minutes + `workflow_dispatch` + `repository_dispatch` type `termux-endpoint-refresh`.
- Soft-pass when variables are unset (publisher inert until B160V `gh auth` is valid).
- Format fail if endpoint does not match `tcp://host:port`.
- Stale warning if `UPDATED_AT` older than 90 minutes.

## Device scripts (reference copies)

Canonical install location on device: `~/.local/bin/`.

| Script | Role |
|--------|------|
| `scripts/termux/termux-pinggy-keeper.sh` | Lock, single tunnel, invoke publisher + status |
| `scripts/termux/termux-pinggy-publisher.sh` | Parse log → set repo variables when `gh auth` OK |
| `scripts/termux/termux-pinggy-status.sh` | State-change notifications only (ID 43109) |

Boot hook (device): `~/.termux/boot/00-manus-termux-mcp` → wake-lock + keeper.

## Re-auth on B160V (required for publisher)

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status
gh api user --jq .login
```

Account must be allowed to manage Actions variables on `timerloggedout-spec/termux-monorepo`.  
Do **not** put tokens in issues, commits, history, variables, or chat.

## Recovery checklist (device)

```sh
ps -ef | grep -E '[p]inggy|[s]sh.*free\.pinggy'
tail -30 "$HOME/.local/state/termux-mcp/reverse-ssh.log"
cat "$HOME/.local/state/termux-mcp/pinggy-status"
termux-job-scheduler --pending
gh auth status
```

Successful MCP init (from trusted client with dedicated key) returns:

```json
{
  "protocolVersion": "2024-11-05",
  "serverInfo": {"name": "termux-control", "version": "1.29.0"}
}
```

## 2FA / credentials

Issue #184 is notes-only. Do not retrieve credentials from issues. Rotate anything previously exposed.  
Candidate local 2FA tooling (pass+pass-otp, rsc/2fa, open2fa, Aegis, Clockwork, Tokn, termux-fingerprint) is documented elsewhere; none is auto-installed by this lane.

## Related

- Full consolidation runbook: `docs/ops/TERMUX-MCP-PINGGY-RUNBOOK.md`
- Codespace agent lane (support plane): `docs/ops/CODESPACE-AGENT-LANE.md`
- Credential policy: issue #184 + `docs/mafe/keys/` matrix

Implements: termux-endpoint-refresh  
BIUDL · AVOID HITL YOLO YEET AUTOAPPROVE · dual-gate before promote
