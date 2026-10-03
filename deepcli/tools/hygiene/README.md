# hygiene/ — Termux resource loop detection & protection

Tools for detecting and surviving the Android LMK cycle that kills
Termux under memory pressure.

## What's here

| File | Purpose |
|---|---|
| `hygiene-watchdog` | Sampler. Logs heartbeats + reboot/cpu/dup events to JSONL. |
| `install.sh` | Idempotent installer. Stages the sv service. |
| `sv/run` | runsvdir run-script for the watchdog. |
| `sv/log/run` | svlogd config. |

## What it detects

- **`reboot_detected`** — `/proc/sys/kernel/random/boot_id` changed
  since last sample. On Termux this fires when the *app process* is
  restarted, not just when the device reboots.
- **`mem_low`** — `MemAvailable < HYGIENE_WD_MEM_FLOOR` (default 200 MB).
- **`dup_procs`** — process name count exceeds limit (python3 > 5, etc.).
- **`cpu_peg`** — any process pegged above `HYGIENE_WD_CPU_PEG` (85%)
  across a 5-second sample window.
- **`heartbeat`** — every cycle. Confirms liveness.

## Log format

`~/.deepcli/logs/hygiene/watchdog.jsonl`, one JSON object per line:

    {"ts":1790988204,"iso":"2026-10-03T00:43:24Z","event":"heartbeat","mem_mb":402,...}

Rotated at 5 MB.

## Enable / disable

    # enable (once)
    bash deepcli/tools/hygiene/install.sh

    # manually
    sv up hygiene-watchdog
    sv status hygiene-watchdog

    # disable
    sv down hygiene-watchdog
    touch $PREFIX/var/service/hygiene-watchdog/down

## Tunables

Set in `~/.zshrc` or `sv` service env:

    HYGIENE_WD_INTERVAL=30        # seconds between samples
    HYGIENE_WD_MEM_FLOOR=200      # MB
    HYGIENE_WD_CPU_PEG=85         # percent
    HYGIENE_WD_DUP_LIMIT=3        # legacy knob, per-name limits are baked in

## Why not cron

`crontab` is not installed by default on Termux. termux-services
(runsvdir) is already running for sshd and manus-termux-reverse-ssh,
so we piggyback on it rather than add a second supervisor.

## Why not cgroups / rlimit

Stock Android grants Termux no cgroup control over its children. The
protection has to live in userspace. `sv` is the only primitive on
Termux that restarts-with-backoff.
