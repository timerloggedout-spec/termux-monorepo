# Pipeline Mesh — Plan v1 (2026-10-02)

**Author:** session 0d3639e8 successor
**Status:** active
**Supersedes:** none
**Related:** docs/STANDARDS/PROCESS/SCRIPT-EVOLUTION.md

## 0 · Doctrine shift

Previous framing: *consolidate all pipelines onto one manifest substrate*.
**Rejected.** Termux is intermittently offline. A central substrate is a
dependency, not a consolidation.

Adopted framing: **mesh**. Every pipeline reads from any peer, appends to any
peer, backfills cross-wise, and falls back to its own last snapshot on read
failure. No peer is authoritative. The corpus lives in Git.

```

```

Rules:
1. Any peer may read from any other peer.
2. Any peer must be able to answer from its own last snapshot if peers unreachable.
3. Cross-backfill is bidirectional; no peer owns the write.
4. The manifest is a *seed* for Provenance once (post-ChapitoAI), not the permanent source.

## 1 · Substrate inventory (8 currently scattered)

| # | Substrate | Path | Reader(s) |
|---|---|---|---|
| 1 | session_store | `~/.deepcli/session_store/primary/*.json` | DeepCLI TUI, `session-export-txt` |
| 2 | synthegration exports | `~/synthegration_exports/{primary,...}/<sid>/session.json` | `forensic_toolchain` (patched), `xref_exports` |
| 3 | harvest manifest | `~/deepseek_harvest_work/code_harvest/manifest.json` | **none live** |
| 4 | provenance | `~/cli-synthegration/workspace/provenance/*.json` | `restore_version.py` |
| 5 | run history | `~/termux-multi-agent/run_history.jsonl` | `restore_version.py`, `scout` |
| 6 | legacy DeepSeek exports | `~/storage/downloads/_doing/_1-build/DeepSeek/exports/*` | `forensic_toolchain` (stale) |
| 7 | staging | `~/archwiz/staging_blocks.json` | ArchWiz menu [11] |
| 8 | local FTS5 | `~/.deepcli/bank-local.db` | Hindsight router tier-3 |

## 2 · Account 2 — resolved

Account 2 is a **DeepSeek browser profile**, not a GitHub identity.

Locations:
- `~/deepseek-cli/browser-data-account2/`          (base)
- `~/deepseek-cli/browser-data-account2-clean/`    (post-purge)
- `~/deepseek-cli/browser-data-account2-fresh/`    (post-signup)
- `~/deepseek-cli/browser-data-account2-v2/`       (current, referenced by DATA_FLOW_MANIFEST)
- `~/deepseek-cli/browser-data/`                    (primary)

Capture toolchain (all `.cjs`):
- `capture-account2-final.cjs`
- `capture-fresh-account2.cjs`
- `capture-token-account2.cjs`
- `capture-upload-account2.cjs` and `-v2`
- `capture-pow-solver.js`
- `capture-via-proxy.sh`

Wiring: TBD — likely through `deepcli/deepcli/core.py::get_token()` reading a
profile-specific token file, or through a `--account` flag on the CLI. Grep
next session.

## 3 · Resource Pressure — found, current

Three live tools, all read-only, all deterministic, no state:

- `~/.local/bin/termux-resource-snapshot.sh` — emits `key=value` lines:
  `timestamp`, `memory_total_mib`, `memory_available_mib`, `swap_total_mib`,
  `swap_free_mib`, `storage_total_mib`, `storage_used_mib`,
  `storage_available_mib`, `storage_used_percent`, `top_processes_rss_kib`,
  `status={OK|PRESSURE}`.
  Thresholds: mem <150 MiB, swap free <128 MiB, storage <1 GiB free or ≥95%.

- `~/.local/bin/termux-resource-sentinel` — wraps snapshot; if `status=PRESSURE`
  fires a Termux notification. No logs. JOB_ID=43107.

- `~/.local/bin/worktree-gc` — dry-run by default; inventory of worktrees with
  size + age; **`--apply` mode not yet automated**.

Origin session: `e563d013-1eb6-43ff-8dc2-668870d15128` (2026-07-16, 1.2 MB).
Harvest blocks: `i=14450`, `i=14452` (the routing.yaml spec), `i=14464`
(the 48 GB storage diagnostic).

**Gap:** sentinel is passive. It notifies; it does not gate. Any heavy op
should read `status=` and refuse to proceed on PRESSURE.

## 4 · Classifier runtime — discovered in a misnamed worktree

Worktree `~/.deepcli/worktrees/fix-session-store-prune-expired` contains the
**classifier runtime the hand-off said did not exist**:

- `scripts/laya_decision_stub.py`  (3.6 KB) — Laya classifier stub
- `scripts/decision_engines.py`    (14 KB) — Jev/Kev/Laya/Mev decision engines
- `scripts/capability_spine.py`    (9.7 KB)
- `scripts/canny_completion_gate.py` (6.7 KB)
- `scripts/hex_moneyball_export.py` (5.3 KB)
- `scripts/scout_missions.py`      (2.8 KB)
- `scripts/scout_roster.py`        (2.6 KB)
- `scripts/bayesian_routing.py`    (4.1 KB)
- `scripts/model_router.py`        (18.7 KB)
- `scripts/model_router_bootstrap.py` (3.0 KB)
- `scripts/provider_model_catalog.py` (11.2 KB)
- `scripts/provider_availability_probe.py` (7.2 KB)
- `scripts/openrouter_free_catalog.py` + `poll_openrouter_free_catalog.py`
- `scripts/live_catalog_feed.py`   (9.9 KB)
- `scripts/model_performance_index.py` (6.8 KB)

**Action:** rename worktree to reflect scope OR cherry-pick scripts back to
`feat/dashboard-lanes-v2` under `deepcli/runtime/`. Decision deferred to P2.

## 5 · Backup method — canon

**Tool:** `hs-backup` v0.2.0 (`~/.local/bin/hs-backup`)
**Store:** `~/.cache/hs-backup/` — `data/` (content-addressed), `local/`
(tarballs), `manifest.jsonl` (append-only).
**Commit namespace:** `refs/backups/<tag>-<ts>` — outside `refs/heads/`,
invisible to `git branch`, non-mutating.

| Mode | Use for | Behavior |
|---|---|---|
| `data` | text, JSON, scripts | sha256 → dedup → single blob |
| `local` | binaries, perms-sensitive (`~/.gnupg/`) | tar.gz w/ arcname preserved |
| `track` | one file | commit via temp-index, HEAD untouched |
| `trackdir` | a tree | one commit, all files, HEAD untouched |

Restore: `hs-backup restore <hash-prefix>` — idempotent, saves `.pre-restore.<ts>` backup.

**Legacy backup systems** (read once, then retire):
- `~/archwiz/*.bak.*` (39 files, ad-hoc epochs) — leave in place, not authoritative
- `~/.deepcli/vault/snapshots/*` (13 snapshots, Sep 30–Oct 1) — read-only, superseded
- `~/.gnupg.bak.pre-restore/` — one-time source for Phase 3 gpg restore
- `git stash@{0..3}` — untouch until triaged

## 6 · Phases

Gate-green before next phase begins.

| # | Phase | Status | Gate |
|---|---|---|---|
| 0 | Baseline snapshot (read-only) | ✅ 2026-10-02 | all categories tracked |
| 0.5 | Ship hs-backup v0.2 + backfill | ✅ this commit | manifest verified |
| 1 | Wire `forensic_toolchain` → manifest | ⏳ | `fragment PRESET_PASSPHRASE` returns writer block |
| 2 | 2FA restore via extract + track | ⏳ | 6 scripts pass `bash -n`; `gpg-prime` runs |
| 3 | GPG identity restore from `.gnupg.bak.pre-restore/` | ⏳ | `gpg --list-secret-keys` shows ED76C8D85C3E731F |
| 4 | Git reconciliation vs origin | ⏳ | divergence enumerated, no force |
| 5 | Harvester patch decision (option b — move upstream) | ⏳ | origin tip fast-forwards |
| 6 | Account 2 wiring in Core.py | ⏳ | token swap works |
| 7 | ChapitoAI/MistralAI provenance seed | ⏳ | first provenance entry |
| 8 | Mesh pipelines (TQDS/MVT/DoE/MoneyBall/sweeps/lanes) | ⏳ | each reads any peer + offline fallback |
| 9 | Doctrine | ⏳ | this doc + retrospective committed |
| 10 | Ops cleanup (codespaces, budgets) | ⏳ | one codespace |
| 11 | Actions benchmark (gh run list aggregation) | ⏳ | top-5 workflows identified |

## 7 · Anti-patterns (inherited, non-negotiable)

Force-push. Token print. Wrong-layer patch. One-off extraction. "Likely" as
fact. Rename via PK update. Delete-before-archive. Multi-line Python at
prompt. Restart-without-capture-env. Action-before-read.
