# Device access directory

The one table of every way to reach the origin Termux node (`tmx-node-primary`) and the secondary node (`tmx-node-55619bd5`).
The origin node has a **damaged screen**. Clipboard does not cross the screen-share session, so any path that needs typing on the device is marked **typing**. Prefer the **no-typing** paths.

Related: `BRIDGE-REDUNDANCY.md` (execution order), `TERMUX-LIVE-BRIDGE.md` (Pinggy contract), `DEVICE-IDENTITY.md` (opaque ids).
No secrets, IPs, or hardware identifiers belong in this file.

## Device checkout layout (observed 2026-10-21)

On both B160V nodes the repository checkout **is `$HOME`** (`~`), not `~/termux-monorepo`. The origin node is on branch `feat/dashboard-lanes-v2` with local changes, and its `~/scripts/` holds only `ci/`, `commit-msg.sh`, `entropy_scan.py` and `model_router.py`. **`scripts/termux/` (the Pinggy publisher, the diagnosis, the job installers) is absent on the device**, which explains why job 43109 never published. To bring those scripts in without switching branches or touching local changes:

```bash
cd ~ && git fetch origin master && git checkout origin/master -- scripts/termux
```

## Directory

| Method | Direction | Who drives it | Device input | Identity / credential (names only) | Publishes / proves | Status (2026-10-21) | Failure signal |
|---|---|---|---|---|---|---|---|
| ADB via BugJaeger (secondary B160V → origin, wireless debugging) | operator → device | Operator on the secondary phone | Taps via mirroring; **typing** for shell | ADB pairing on device | Screenshots, notifications | Working | BugJaeger disconnects |
| Pinggy free TCP (reverse SSH to `127.0.0.1:8022`) | device → internet | Device keeper; publisher job **43109** | none once installed | No Pinggy token (free, unauthenticated); device `gh` login to publish | `ops/termux-bridge/current.json` | Tunnel up (Termux:API "Pinggy connected"); **manifest not published since 2026-10-17** | Manifest `status` not `active` / expired; host does not resolve |
| Tailscale, GitHub-identity tailnet (`timerloggedout-spec.github`) | mesh | Tailscale Android app | Taps only | GitHub login | Peers `termux-hub`, `aperture` | Origin **connected** | Peer offline in app |
| Tailscale, Google tailnet (`tailf2ee94.ts.net`) | mesh | Tailscale Android app; Actions runner via workload identity (`tag:ci`) | Taps only (account switch) | Google login; GitHub OIDC trust credential (no stored secret) | `ops/termux-bridge/tailscale.json` (runner-written) | Origin node `b160v` **offline since 2026-08-14**; admin managed by Hark | `tailscale ping b160v` fails |
| Cloudflare tunnel | device → internet | cloudflared on device | **typing** to install | Cloudflare account | Stable hostname | **Blocked**: cfapi.net consent | — |
| GitHub Actions → SSH (`deepcli-agent-bridge.yml`, `termux-bridge-connect.yml`, `deepagent-task.yml`) | runner → device | Actions | none | `TERMUX_MCP_SSH_PRIVATE_KEY`, `TERMUX_MCP_KNOWN_HOSTS`, `MANUS_SSH_*` | Run receipts | **Skips and reports green** while the manifest is not active | Run green with "skipped" notice |
| termux-job-scheduler jobs 43107 / 43108 / 43109 | on device | Termux | **typing** to (re)install | — | Publisher, sentinel | Unverified: likely lost (no manifest, no pressure alerts) | `termux-job-scheduler --pending` empty |
| Termux:API notifications (`termux-resource-sentinel.sh`) | device → operator | Sentinel job | none | — | "Termux resource pressure" | Silent (only fires on pressure, or job missing) | No notification for >1 day |
| Hark queue (`hark:queue` issues via `hark-enqueue.yml`) | Actions → Hark | Hark poller (2h) | none | GitHub connector | Issue comments, `hark:done` | Working | Issue stays `hark:queue` |

## No-typing recovery order

1. Taps in the Tailscale app to put the origin on whichever tailnet the runner can join.
2. The runner joins the tailnet (`tag:ci`), proves TCP to `:8022`, and writes `tailscale.json`.
3. If the `TERMUX_MCP_SSH_PRIVATE_KEY` key is authorized by the device's sshd, then over that path the runner (re)installs jobs 43107–43109 and refreshes `gh` auth. Nothing is typed on the device.
4. Pinggy and the manifest resume. Cloudflare comes in later as the third path.
