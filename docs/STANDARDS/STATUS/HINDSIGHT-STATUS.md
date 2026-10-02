# Hindsight Stack — Status Alignment
Generated: 2026-10-02T00:45Z  |  Branch: feat/gh-actions/deepseek-integrates-itself

## LIVE — verified working

| Component | State | Evidence |
|---|---|---|
| Hindsight :8888 | UP | hs-verify PASS health=200 |
| Hindsight :8889 | UP | hs-verify PASS health=200 |
| Model :8888 | gemini-3.1-flash-lite | matches active.json (hs-verify PASS) |
| Model :8889 | meta-llama/llama-3.3-70b-instruct:free | hs-or-launch.sh |
| Rotator (hs-stack.py watch) | RUNNING | hs-verify PASS |
| Sovereign loop | RUNNING, 1 tick | hs-verify PASS |
| mvt-seed.py | RUNNING, 4 batches logged | hs-verify PASS |
| PG auth via instance.json | VERIFIED | hs-verify PASS |
| PG banks table | 3 rows | hs-verify PASS |
| DB-ACCESS doc | written | docs/STANDARDS/FLOWS/DB-ACCESS.md |
| Verification suite | 10 PASS / 0 FAIL | hs-verify |

## OPEN DEFECTS

| # | Defect | Severity | Evidence |
|---|---|---|---|
| D1 | CLOSED — memory_units.context, not banks.fact_count | — | dashboard shows facts |
| D2 | CLOSED — hs-db v0.3.0 reads SQL from stdin | — | — |
| D3 | DeepAgent Hindsight is a stub | HIGH | `if False else None  # Phase 3` in deepagent.py |
| D4 | cs-seed.py does not read active.json | MED | older seeder, superseded by mvt-seed |
| D5 | offload.sh missing from disk | MED | referenced, never shipped |
| D6 | hs-cadence harvest fails 4-6s since 09:00 | MED | hs-cadence.jsonl shows repeated fail |
| D7 | CLOSED — all scripts use TMPDIR | — | — |
| D8 | CLOSED — _active_role reads active.json, verified in mvt-seed.log | — | producer |
| D9 | CLOSED — DB TRUTH + QUOTA + OR QUOTA + PROVENANCE + ERRORS | — | live |
| D10 | Legacy bank rename — done via FK-aware txn | — | banks + children updated |

## STUBS — declared but not implemented

| # | Stub | Location | Required to |
|---|---|---|---|
| S1 | deepagent.py finish -> hindsight_retain | deepagent.py ~line 1040 | Auto-retain on task end |
| S2 | deepagent.py eager recall | deepagent.py loop() start | Seed context before run |
| S3 | Decision classifier runtime | observatory/{mev,jev,kev,laya}.py | Runtimes beyond role labels |
| S4 | observatory leaderboard live data | observatory/leaderboard.py | No campaigns have run |
| S5 | Colab batch offload pipeline | none | Batch-only ML compute |
| S6 | Fly.io / Koyeb cold-start deploy | none | Non-codespace Hindsight |

## MILESTONES

- [x] M1 Rotator live (hs-stack.py)
- [x] M2 Seed pipeline live (sovereign-run + mvt-seed)
- [x] M3 Multi-lane (gemini + openrouter)
- [x] M4 Live dashboard (hs-dash)
- [x] M5 DB truth access (hs-db v0.2.0)
- [x] M6 Verification suite (hs-verify 10/0)
- [ ] M7 Persistence verified — BLOCKED on D1
- [ ] M8 DeepAgent Hindsight integration — BLOCKED on S1, S2
- [ ] M9 Decision classifier runtime — BLOCKED on S3
- [ ] M10 Observatory leaderboard with real campaigns — BLOCKED on S4
- [ ] M11 Cold-start deploy (Fly/Koyeb) — NOT STARTED
- [ ] M12 Colab batch worker — NOT STARTED

## DOCS ON DISK

- docs/STANDARDS/FLOWS/HINDSIGHT-SUCCESS.md
- docs/STANDARDS/FLOWS/AVAILABILITY-TIERS.md
- docs/STANDARDS/FLOWS/HINDSIGHT-LIFECYCLE-LIB.md
- docs/STANDARDS/FLOWS/DB-ACCESS.md
- docs/STANDARDS/PROCESS/SCRIPT-EVOLUTION.md
- docs/STANDARDS/MODELS/DECISION-CLASSIFIERS.md
- docs/STANDARDS/MODELS/decision-record.schema.json
- docs/STANDARDS/SECRETS/FRAMEWORKS.md
- docs/STANDARDS/RETROSPECTIVES/2026-09-30-sweep-cascade.md

## LIFECYCLE SCRIPTS ON DISK (~/deepcli/tools/hindsight-lifecycle/)

boot-95-hs-stack.sh, boot-96-hs-quota-state.sh, boot-97-hs-quota.sh,
boot-98-hs-tunnel.sh, cs-seed.py, hs-cadence, hs-dash, hs-db, hs-down,
hs-drain, hs-lib, hs-or-launch.sh, hs-parity, hs-parity2,
hs-quota-state, hs-quota-watch, hs-recover.sh, hs-replay,
hs-sovereign-launch.sh, hs-stack, hs-stack-launch.sh, hs-stack-watchdog,
hs-stack.py, hs-status, hs-up, hs-verify, mvt-seed.py, mvt-watchdog,
provenance-harvest, sovereign-run.sh

## DOCTRINE PATTERNS ESTABLISHED THIS SESSION

1. No nested heredocs in shell blocks — app UI folds on `\`\`\`` inside heredocs.
   Use Python `write_text()` for anything multi-line.
2. `/tmp` exists on codespace, NOT on Termux. Use `TMPDIR` on Termux.
3. `gh codespace ssh` takes flags before `--`; nothing after `--` reaches local shell.
4. Quote nesting > 2 levels breaks in Termux zsh. Ship script, run script.
5. Rotator's `restart_hindsight` must read env from `/proc/<pid>/environ` of
   the running API (keys not in rotator's env).
6. mvt-seed is the single writer of `state.json` (RPD counters). Sovereign
   does not double-count.
7. `role` comes from active.json, not hardcoded.

## NEXT ACTION — in order

1. Write mvt_diag.sh via TMPDIR (D7), run it, resolve D1.
2. If D1 = writes dropped: read hs.log around each batch for silent 500s.
   If D1 = wrong table: adjust hs-verify + hs-dash queries.
3. Ship hs-dash-body DB TRUTH section (D9).
4. Fix hs-db argv path (D2) — already v0.2.0, verify.
5. Fix hs-cadence harvest (D6).
6. Wire DeepAgent Phase 3 (S1, S2): finish handler calls hindsight_retain.
7. Only then open S3 (classifier runtime) and S4 (leaderboard).


## Batch plan (2026-10-02)

- `hs-batch-plan.py` v0.3.0: size = min(by_in, by_out, by_window).
- by_in = inputTokenLimit / avg_item_tokens (live from Gemini models API).
- by_out = outputTokenLimit / out_per_item.
- by_window = HTTP_WINDOW_S / per_item_s (measured median, prior 9.4s until ≥3 samples).
- No fixed cap. Values recomputed on every sovereign tick.
