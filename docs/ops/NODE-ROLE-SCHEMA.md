# Node role schema: observer|controller 🎮

Machine-readable twin: `ops/devices/role-schema.json`. Collaborator agents verifying #1254 should check the diff against this file.

## Roles

| Node | Role | Owns | Never |
|---|---|---|---|
| `tmx-node-primary` (origin, broken screen) | `bridge` | Pinggy tunnel (43109), DeepAgent / DeepCLI / `Agent.py` via `core.py`, resource sentinel (43107), the canonical account sessions + OAuth callbacks | Taking orders other than the `tmx-ctl.sh` verbs |
| `tmx-node-55619bd5` (new phone) | `observer-controller` | Its own heartbeat, the two-pane notification, the controller key | Running Pinggy, importing origin cookies/sessions, git writes on origin |

**Observer** = reads origin state (heartbeat branch, bridge manifest, TCP probe) and alerts.
**Controller 🎮** = may *ask* the origin to do a short allowlist of read-only or idempotent things. It cannot change what the origin runs.

## Two-pane notification (group `tmx-origin`)

Android has no split notification. The closest native equivalent is a bundled pair in one group:

| id | Pane | Controls |
|---|---|---|
| 43111 | Observer | Refresh · Copy SSH (this phone's clipboard only) · Mute 2h |
| 43114 | Controller 🎮 (`--type media`) | ⏮ / ⏭ pick a verb, ▶ run it on the origin, ⏸ mute; buttons Heartbeat · Wake · Agent? |

Results are written into the card. Nothing travels through the clipboard.

## Controller verbs (`scripts/termux/devices/tmx-ctl.sh` on the origin)

`status`, `agent`, `tunnel`, `jobs`, `disk` (read) · `heartbeat-now`, `wake-lock` (idempotent).
Transport: ssh over the published Pinggy endpoint. The controller key is pinned in the origin's `authorized_keys` with `command="bash …/tmx-ctl.sh",no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding`. Any other verb exits 2, and only the first word is read, so `disk; rm -rf /` is refused.

Forbidden by design: restarting/killing Pinggy (it would cut its own transport), touching `core.py` agents, git writes, editing `termux-job-scheduler`, reusing 43107–43109.

## Connectivity from any network

- **Today:** controller → origin rides the origin's Pinggy TCP endpoint (works from any network while 43109 publishes `current.json`). ADB is still LAN or USB-C.
- **ADB anywhere (decision pending):** install the Tailscale app on both phones, then `adb connect <origin-tailnet-ip>:5555` from the controller's Termux `android-tools`. `adb tcpip 5555` resets on reboot; re-arm it from the origin itself through Shizuku/`rish` (e.g. `rish -c 'settings put global adb_wifi_enabled 1'`; the exact path depends on the Android version that `inventory.sh` records) instead of a cable. Until that's decided, Pinggy SSH is the any-network path.

## Clipboard and Bugjaeger

Typing or pasting commands across a Bugjaeger screen-share is the last option. Preferred order:
1. `git pull --ff-only` on the target, then run a script by path (one short line to type).
2. `adb push file /sdcard/Download/` from the controller, then `bash` it on the target.
3. Bugjaeger's own shell / file push.
4. Manual entry.

Secrets and tokens never cross via the clipboard. Android clipboard history and keyboard apps keep copies.

## Accounts, cookies, sessions

Both phones share one Google account (`<operator Google account>`). Running the same cookies or OAuth refresh tokens from a second device is a common revocation trigger. Rules:
- The controller never imports origin cookie jars, browser profiles or `DEEPSEEK_COOKIES*` style material.
- A new login on the controller goes through the capture-login OAuth callback flow, giving it its own session. It never reuses one.
- Identity stays opaque (`tmx-node-*`). Fingerprints exist only in the age-sealed `TMX_FPMAP_*` secrets.

## Origin workload and worktrees

Origin keeps running DeepAgent / DeepCLI / `Agent.py` via `core.py`. Full `git worktree`s are too heavy for its storage. The safe alternative, recommended and not yet enforced:
```bash
# one light, separate object store per lane; no second full checkout
git clone --filter=blob:none --no-checkout --depth 50 https://github.com/timerloggedout-spec/termux-monorepo ~/lanes/<lane>
git -C ~/lanes/<lane> sparse-checkout set --cone <paths the lane needs>
git -C ~/lanes/<lane> switch -c lane/<lane> origin/master
```
Branch and stash per lane inside that clone, never in `~/termux-monorepo`. `tmx-ctl.sh disk` reports `.git` size so the controller can watch storage pressure.

## RECON first

`scripts/termux/devices/inventory.sh` runs read-only on any node before provisioning. It records the Termux version, the add-on apps (Termux:API/Boot/Widget, Shizuku, Bugjaeger, Tailscale…), the CLI tools and free space into `~/.local/state/tmx-device/inventory.json`. The file stays local and is never committed. Run it on **both** phones: the new phone has a newer Termux, and the scripts must work on the older one.
