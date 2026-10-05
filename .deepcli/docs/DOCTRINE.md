# Termux Continuity Doctrine

Canonical operating procedure for the timerloggedout-spec/termux-monorepo
agent stack on Android (BLU B160V).  Every claim in this file traces to a
measured fact.

## Non-negotiables

1. session_store is a permanent database — never trimmed, never pruned.
2. HTTP 200 is the sole success signal for probes.  `000` = failure.
3. Recon runs before any clone; cap = 200 MB.
4. Write → ast.parse → ruff → execute.  Never execute before lint.
5. Every destructive action requires a backup and a reversible artifact.
6. Notifications: one owner per event.  Duplicates are bugs.

## Facts measured on BLU B160V (2026-10-05)

| Item | Value | Source |
|---|---|---|
| Bare `python3` VSZ | ~10,658 MiB | `ps -o vsz` §measure_child |
| Bare `python3` RSS | ~11 MiB | same |
| Hub VSZ / RSS | 10,791 / 56.8 MiB | same |
| Hub top memory growth | None observed in 20s window | same |
| RLIMIT_AS 384 MiB effect | Kills any python child at import | RLIMIT_AS counts VSZ |
| Correct child cap | RLIMIT_DATA 512 MiB | Derived from bare Python RSS |
| Pillow memory budget | 384 MiB insufficient on this class of device | §task note |
| session_store size | 445.7 MB / 1154 files | session manifest |
| .git size | 249 MiB pack, 1 pack (post-gc) | `count-objects` |

## The chain

```

GitHub Actions Workflow
↓ gh workflow run  -f task="…"
↓ POST $DEEPSEEK_AGENT_URL/v1/agent  {"task": "…", "source": "…"}
↓ (Pinggy HTTP tunnel: pinggy-free.link)
↓ Hub (deepcli/server.py :8800)
↓ subprocess.Popen  deepagent-dispatch <task-file> <source>
↓ deepagent.py  --task-file  (fires termux-notification: start/finish)
↓ Device notification "Agent starting" / "Agent done"

```

## Endpoint surface (`/v1/agent` family)

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/agent` | Start a run. Returns `{invocation_id, status}` |
| GET | `/v1/agent` | Index (methods + fields) |
| GET | `/v1/agent/list` | Last 20 runs |
| GET | `/v1/agent/status/{inv}` | Status of one run |
| POST | `/v1/agent/{inv}/pause` | SIGSTOP the child |
| POST | `/v1/agent/{inv}/resume` | SIGCONT the child |
| POST | `/v1/agent/{inv}/stop` | SIGTERM, graceful |
| POST | `/v1/agent/{inv}/cancel` | SIGKILL, immediate |

Child PID file: `~/.deepcli/watchdog/dispatch-<inv>.pid` (legacy
`dispatch.pid` used as fallback for old runs).

## Tunnel lanes (four parallel routes)

| Lane | Pattern | Purpose |
|---|---|---|
| Pinggy TCP | `ssh -R0:localhost:8022 tcp@free.pinggy.io` | SSH bridge |
| Serveo | `ssh -R <pinned>:8022:localhost:8022 serveo.net` | Durable SSH failsafe |
| Pinggy HTTP | `ssh -R0:localhost:8800 qr@free.pinggy.io` | Agent HTTP lane |
| Keeper loop | `tunnel-keeper-loop` | Rotates `DEEPSEEK_AGENT_URL` on host change |

All four supervised by one orchestrator: `~/.termux/boot/50-tunnel-lanes.sh`.
Flock-guarded, single process tree, one log.

## Reusable toolkits

### scripts/bridge — health probes
```

scripts/bridge/bridge_health.sh all

```
Strict 200-only.  Local + external.  `/v1/models`, `/health`, and the
Hindsight plane.

### scripts/tribute — worktree + hygiene
```

scripts/tribute/tribute_lane.sh recon <owner/repo>            # metadata, no clone
scripts/tribute/tribute_lane.sh run <owner/repo> <cmd...>     # shallow + sparse
scripts/tribute/tribute_lane.sh hygiene                       # .git + bloat report

```
Clone: `--depth=1 --filter=blob:none --sparse`.  Cap 200 MB.  Measured
0.1 MB worktree for zsh-autosuggestions vs ~3 MB full.

### scripts/diagnostics — session tooling
`~/.cache/tunnel-doctor/*.py` — reusable probes, sampled per session.
Mirrored into `scripts/diagnostics/` when this doctrine commits.

## Notification ownership (post-2026-10-05)

| Event | Owner | `--id` |
|---|---|---|
| Tunnel rotation | `tunnel-keeper-loop` | `tunnel-rot` |
| Agent start | `deepagent-notify` | `deepagent-run` |
| Agent finish | `deepagent-notify` | `deepagent-run` |
| Resource pressure | `precheck` | `resource` |
| Hub down | `50-tunnel-lanes.sh` | `hub` |

`tunnel-up` and `termux-pinggy-status` no longer fire rotation alerts —
they were the duplicate source.  `--id` collapses repeats into one row.

## Reversal artifacts

Every write to `deepcli/server.py` produces
`server.py.bak.<YYYYMMDDTHHMMSS>`.  Every git ref state is snapshotted to
`~/.cache/tribute/git-refs-<ts>.txt`.  Every session appends to
`.deepcli/docs/sessions/session-<ts>.md`.  Nothing destroyed without a
reversible copy.

## Boot sequence (on device power-on)

1. `1-wake_lock.sh` — acquire `termux-wake-lock`, flock guard.
2. `50-tunnel-lanes.sh` — start hub if down, launch all four tunnel lanes.
3. `95..99-hs-*` — Hindsight quota, stack, codespace cron (independent).
4. `symlink_to_nix.sh` — Nix-on-Droid bin bridge.

The orchestrator runs forever, `flock`-guarded, log-capped at 1 MiB
rotated every 256 KiB.

## DO

DO Commit every fix prior to executing a workflow.
DO Measure system metrics (`RSS`, `VSZ`, `exit code`, `log tail`) prior to declaring outcome.
DO Apply `RLIMIT_DATA` for child memory caps, maintaining native Python execution alignment.
DO Maintain `session_store` in a `synced` state{`git-LFS` any selected removals→pointer archive}.
DO Recognize `status` `200` as valid success, processing `000` as requiring resolution.
DO Configure Android `Python` `child` `processes` using 'target-appropriate' memory bounds.
DO Collapse notifications by `owner` and `--id` to preserve signal clarity.
DO Verify agent `logs` directly to confirm workflow health.
DO Validate every root cause with a complete `traceback` && empirical measurement.

## Process-group control (added 2026-10-05)

The `/v1/agent/{inv}/{pause,resume,stop,cancel}` endpoints signal the
**process group**, not a single PID.  Facts that make this necessary:

- `deepagent-dispatch` runs as `bash -c` wrapping `python3 deepagent.py`.
- Signalling the bash wrapper leaves the python worker running.
- `Popen(start_new_session=True)` makes the wrapper a session leader; its
  PID becomes the PGID of the whole tree.
- The per-invocation pid file stores the **PGID**, not the wrapper PID.
- Control endpoints call `os.killpg(pgid, sig)`.

Verified on BLU B160V (2026-10-05, inv `9bf7893f17a1`):

| Action | bash state | python state |
|---|---|---|
| baseline | `Ss` | `R` |
| after `/pause` | `Ts` | `T` |
| after `/resume` | `Ss` | `R` |
| after `/stop` | gone | gone |

Exit code from clean SIGTERM: `rc = -15`.

## Expansion points

- Add new endpoint → same pattern as `/v1/agent/{inv}/pause`: guard `ast.parse`,
  write PID file per invocation, respond JSON.
- Add new tunnel lane → add a `lane_<name>()` function to
  `50-tunnel-lanes.sh`, call from the 45s loop.
- Add new tribute target → `tribute_lane.sh run <owner/repo> <cmd>` — no
  new code path needed.
- Add new health probe → extend `PATHS` in `scripts/bridge/health_probe.py`.
