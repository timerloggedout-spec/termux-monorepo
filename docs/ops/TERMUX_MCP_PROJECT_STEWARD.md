# Termux MCP Project Steward

> **Purpose:** Provide a repeatable, low-footprint operational routine for a GitHub repository that is actively developed from an Android Termux environment.

## Default Operating Model

The project uses two complementary routines.

| Routine | Cadence | Execution location | Default behavior |
|---|---:|---|---|
| Local Resource Sentinel | Every six hours and after reboot | BLU B160V Termux | Deterministic, read-only snapshot; sends a notification only on pressure |
| Daily Project Steward | Once each day | MCP-enabled project task | Read-only device, repository, PR, and issue review; reports priorities |

The local routine must remain minimal. It must not run an LLM, clone repositories, write rolling logs, download packages, start a model, modify swap, or perform GitHub operations.

## Install the Local Sentinel

From a clean checkout containing this script:

```bash
chmod 700 scripts/termux-resource-sentinel.sh
termux-job-scheduler \
  --job-id 43107 \
  --script "$PWD/scripts/termux-resource-sentinel.sh" \
  --period-ms 21600000 \
  --battery-not-low true \
  --storage-not-low false \
  --persisted true
```

Use the fixed job ID to replace the project sentinel cleanly. Inspect current jobs before changing it:

```bash
termux-job-scheduler --pending
```

The job runs approximately every six hours. Android may defer background work under battery and device policy; it is a pressure detector, not a real-time monitor.

## Pressure Policy

The tracked snapshot marks `PRESSURE` when storage use is at least 95%, available memory is below 150 MiB, or free swap is below 128 MiB. On pressure, the sentinel displays a Termux notification and takes no corrective action.

> Do not create swap automatically. Check existing swap and storage first. A swapfile can consume critical flash space, increase device wear, and may not be permitted by Android policy.

## Daily Steward Protocol

The daily project review should collect only the information needed to prioritize work:

1. Device snapshot and MCP/tunnel reachability.
2. Active target repository status, requested base branch, and isolated worktrees.
3. Open PRs, review requests, failed checks, and relevant issues.
4. At most five ordered actions.

By default, a daily review must not create branches, commits, PRs, comments, package changes, service restarts, file removals, or swap changes. Those actions require an explicit apply request.

## Lean Worktree Rule

Do not use a dirty Termux home checkout for a change. Fetch the requested base branch and create an isolated Git worktree outside the home checkout. Keep virtual environments, upstream MCP source, public tunnel state, keys, models, caches, exports, and generated logs out of the tracked repository.
