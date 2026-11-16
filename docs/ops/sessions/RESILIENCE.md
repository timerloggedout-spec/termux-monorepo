# Resilience policy

## Self-recovery layers (bottom → top)

1. **File integrity** — `agent-self-heal` parses every core file.
   Broken → restore from master → fallback to last-good snapshot.
   Wired: servers-up, keeper (every 100 runs).

2. **Precheck gates** — every heavy op asserts ≥500MB free + estimated×2 headroom.
   Wired: servers-up, agent-keeper, tunnel-keeper.

3. **Network interrupt** — per-step run checkpoint in session_store.
   Wired: deepagent loop. Resumes on next launch.

4. **Transport resilience** — burst + rest retry policy.
   Wired: _chat_once, _post, _post_sse.

5. **Session continuity** — task-hash keyed persistence.
   Wired: session_store.load/save.

6. **Hindsight reachability gate** — tools only appear if `/health` returns 200.
   Wired: deepagent loop start.

7. **Tunnel keepers** — watchdog + keeper + boot trio with --id notifications.

8. **GitHub Actions canaries** — deploy-hindsight, fly-diag, tunnel-canary.

## Failure → response matrix

| Symptom | Layer that catches | Recovery |
|---|---|---|
| deepagent.py syntax broken | self-heal (parse gate) | restore from master/snapshot |
| Disk < 500MB | precheck | deny operation, notify |
| Network drop mid-step | run checkpoint | resume from last step |
| DeepSeek rate limit | retry policy | burst+rest, then give up |
| Session lost | session_store | fresh session w/ same task key |
| Hindsight endpoint down | reachability gate | tools silently hidden |
| Tunnel rotated | keeper + watchdog | rotate + update GH secret |
| Fly app crashes | fly-hindsight-config workflow | reapply secrets + restart |

## Redundancy principle

Every critical service has ≥2 producers/consumers:
- Tunnel: pinggy + cloudflare (parallel)
- Snapshot: master + local last-good
- Keeper: watchdog + boot + self-heal
- Logs: local + `logs/history` branch
- Memory (once live): Hindsight + local session_store

## Non-negotiable invariants

- No file deletion without `.broken.<ts>` backup
- No `git push --force` on master
- No `rm -rf` outside `.cache`, `worktrees`, `/tmp` (which doesn't exist)
- Every notification uses `--id` (replace in place)
