# Task: hygiene-watchdog 24h review

Dispatched automatically after 24h of hygiene-watchdog observation.
Owner: timerloggedout-spec. Execution context: Termux-local only.

## Input

`~/.deepcli/logs/hygiene/watchdog.jsonl` — one JSON object per line:

    {"ts": <epoch>, "iso": "<utc>", "event": "<heartbeat|reboot_detected|mem_low|dup_procs|cpu_peg>", ...}

## Required output

`~/.deepcli/logs/hygiene/24h-review.json` with these keys:

    {
      "window_start":     "<iso>",
      "window_end":       "<iso>",
      "sample_count":     <int>,
      "boot_count":       <int>,
      "min_mem_mb":       <int>,
      "p50_mem_mb":       <int>,
      "max_mem_mb":       <int>,
      "reboots":          [ { "ts": <int>, "boot_id": "<>" } ],
      "cpu_pegs":         [ { "ts": <int>, "pid": <int>, "comm": "<>", "pct": <int> } ],
      "dup_procs":        [ { "ts": <int>, "name": "<>", "count": <int> } ],
      "mem_low_events":   [ { "ts": <int>, "mem_mb": <int> } ],
      "hour_histogram":   { "<0-23>": <int> },   # events per hour UTC
      "recommended": {
        "mem_floor_mb":      <int>,   # ~min_mem - 50, clamped to [80, 300]
        "cpu_peg_pct":       <int>,   # p95 of observed pegs, clamped [60, 95]
        "soft_protector":    <bool>,  # true if any dup_procs or cpu_peg seen
        "notes":             [ "<string>" ]
      }
    }

## Decision rules

- If `reboot_detected` count >= 3 in 24h: flag `recommended.soft_protector=true`
  and add note `"cyclic reboots — investigate LMK vs boot-script overlap"`.
- If any `cpu_peg` on `python3`, `git`, or `node`: add the (comm, pct) to notes.
- If `min_mem_mb` < 150: add note `"memory pressure severe — floor raised to 180"`.

## Notify

On start:  `hygiene-notify "hygiene-24h" "analysis started" 9001`
On success: `hygiene-notify "hygiene-24h" "analysis complete: <N> reboots, min_mem <X>MB" 9002`
On failure: `hygiene-notify "hygiene-24h" "analysis failed: <reason>" 9003`

## Then

Open a PR to `feat/dashboard-lanes-v2` with the review JSON committed at
`docs/ops/hygiene/24h-review.json` and a one-paragraph summary in
`docs/ops/hygiene/24h-review.md`.
