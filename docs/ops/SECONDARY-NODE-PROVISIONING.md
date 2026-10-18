# Secondary node provisioning (new BLU View 5 B160V)

Brings a second B160V online as an **observer** node `tmx-node-55619bd5`: its own Termux, boot scripts, git guard and a live status notification about the origin (`tmx-node-primary`, broken screen, ADB-only).

Additive lane. Nothing here edits existing files, the origin's jobs 43107–43109, or `ops/termux-bridge/current.json`. **Never run `publish-pinggy-endpoint.sh` on the secondary**: it would overwrite the origin's bridge manifest.

## What gets installed

| Piece | Where | Notes |
|---|---|---|
| Packages | `git gh openssh python termux-api jq age curl procps` | |
| Identity | `~/.config/tmx-device/identity.env` | opaque id, role, origin id |
| Git guard | `~/.local/bin/git` + global `core.hooksPath` pre-push | blocks reset --hard, clean -f, force/delete push, branch -D, rm, mv, checkout ., restore, stash drop/clear, filter-*, gc --prune=now, reflog expire, update-ref -d. Exit 97. Only an interactive TTY can bypass by typing the phrase; agents/jobs cannot |
| Boot | `~/.termux/boot/00-tmx-wake-lock.sh`, `10-tmx-sshd.sh`, `20-tmx-device-jobs.sh` | wake lock, key-only sshd, re-assert jobs after network is up |
| Job 43110 | `publish-device-heartbeat.sh` | every 15 min -> `ops/devices/heartbeat/<id>.json` on branch `device-heartbeat`, `[skip ci]` |
| Job 43111 | `origin-status-notify.sh` | every 15 min; ongoing notification 43111, alert 43112 |

## Origin status notification

Reads the origin heartbeat (branch `device-heartbeat`) and the bridge manifest (master), then TCP-probes the Pinggy endpoint.

* **OK** — heartbeat < 45 min, tunnel active and probe succeeds, battery fine.
* **DEGRADED** — battery < 20 % and not charging, ≥ 45 °C, Pinggy process down, manifest stale/expired/unknown, probe fails, or manifest claimed by another id.
* **DOWN** — no heartbeat, or heartbeat older than 45 min.
* **UNKNOWN** — this phone cannot reach GitHub.

Card shows `origin battery · tunnel state · heartbeat age | this phone battery`, with buttons **Refresh**, **Copy SSH** (copies `ssh -p PORT user@host`), **Mute 2h**. A high-priority alert (vibrate, red LED) fires only on a transition into DEGRADED/DOWN and clears itself on recovery. Thresholds: `TMX_ORIGIN_STALE_MINUTES`, `TMX_ORIGIN_LOW_BATTERY`, `TMX_ORIGIN_HOT_CELSIUS`.

Android's JobScheduler minimum is 15 minutes, so the card is at most ~15 min behind; tap Refresh for now.

## Runbook

### A. New phone (working screen), Termux from F-Droid

Install **Termux**, **Termux:API**, **Termux:Boot** from the same source (F-Droid). Open Termux:Boot once. Then in Termux:

```bash
pkg update -y && pkg install -y git gh
gh auth login --hostname github.com --git-protocol https --web
gh repo clone timerloggedout-spec/termux-monorepo ~/termux-monorepo -- --filter=blob:none
cd ~/termux-monorepo
bash scripts/termux/devices/provision-secondary.sh --device-id tmx-node-55619bd5
```

Optional, from a computer with the new phone on USB/wireless debugging (keeps Termux alive with the screen off):

```bash
adb shell dumpsys deviceidle whitelist +com.termux
adb shell dumpsys deviceidle whitelist +com.termux.api
adb shell cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow
adb shell pm grant com.termux.api android.permission.POST_NOTIFICATIONS   # Android 13+; ignore error on older
```

### B. Origin (broken screen) over ADB

```bash
adb connect <origin-ip>:<port>          # wireless debugging
adb forward tcp:8022 tcp:8022
ssh -p 8022 localhost                   # Termux sshd on the origin
# then, inside the origin's Termux:
cd ~/termux-monorepo && git fetch origin && git pull --ff-only
bash scripts/termux/devices/device-identity.sh init --id tmx-node-primary --role bridge
bash scripts/termux/devices/install-device-jobs.sh --role origin     # adds job 43110 only
termux-job-scheduler --pending                                       # 43107-43110 listed
```

### C. Verify

```bash
# on the new phone
bash scripts/termux/devices/origin-status-notify.sh --print
git -C ~/termux-monorepo reset --hard        # expect: BLOCKED by tmx-git-guard (exit 97)
bash scripts/termux/devices/device-identity.sh verify
```

### D. Seal fingerprints (after `age-recipients.txt` exists, see DEVICE-IDENTITY.md)

```bash
bash scripts/termux/devices/device-identity.sh seal --secret     # on each phone
```
