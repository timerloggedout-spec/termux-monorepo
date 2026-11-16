# VM workspace backup (`muse-vm-workspace-backup`)

Tiered, scrub-gated export of this Muse VM's home/workspace state to
the **private** GitHub repo `timerloggedout-spec/muse-vm-workspace-backup`.
Design of record: `docs/ops/VM-WORKSPACE-BACKUP-SCOPING-2026-11-01.md`
(scoping PR #3522). The VM home has no `.git` and persists only on the
platform home-volume; this backup is the off-VM copy.

## Tools

| Script | Job |
|---|---|
| `export_vm_workspace.py` | Build the inventory, stage T0, run the scrub gates, publish one commit per export via the Git Data API. |
| `state_hash.py` | Stat-only T0 fingerprint vs the last-export marker. Exit 0 = unchanged, exit 3 = changed. |
| `restore_vm_workspace.py` | Restore drill: restore T0, verify hashes, assert excluded paths absent, check T1 manifest consistency. Emits `DRILL.json`. |

Runtime copies live in `~/workspace/vm-backup/bin/` (the lane-state dir,
excluded from the backup itself); this repo directory is the source of
truth. Auth reuses the fleet PAT helper's mechanism
(`dynamic_credentials.add_surrogate_to_request`, connection
`custom.github-pat`) — the credential is a surrogate exchanged by the
platform proxy for `api.github.com` only; it is never printed, logged,
committed, or placed in argv/env. git-over-HTTPS transport cannot use
the surrogate in this sandbox, so publishing is a Git Data API batch
commit (blobs → trees → commit → ref), with unchanged blobs skipped by
git-blob-SHA comparison against the previous export's tree.

## Tiers

- **T0 — full content.** `~/CLAUDE.md`, `~/MEMORY.md`, `~/USER.md`,
  `~/IDENTITY.md`, `~/SOUL.md`, `~/PROACTIVE_PREFERENCES.md`,
  `~/AGENTS.md`, `~/TOOLS.md`, `~/memory/**`, `~/workspace/goals/**`,
  `~/workspace/custom-connectors/**`, `~/workspace/custom-skills/**`,
  `~/hooks/**`, `~/workspace/user/**`. Staged as `t0/<source-relative>`.
- **T1 — manifest-only in phase 1.** Every other top-level
  `~/workspace` entry: git clones contribute their dirty-tracked +
  untracked files; plain dirs contribute their files minus regenerable
  subtrees (`node_modules`, `.venv`, `venv`, `.venvs`, `__pycache__`,
  `.cache`, `dist`, `build`, `target`, `.next`, `.git`). Entries are
  recorded in `MANIFEST.json` with path + sha256 + size + tier,
  `exported=false`, `reason=phase1-manifest-only`. No T1 content is
  staged or published in this build.
- **Manifest-only by size.** Any file over 25 MB (either tier) is a
  `t0-manifest`/`t1-manifest` entry with `reason=size`.
- **Split band (large-blob repair, 2026-11-04).** A T0 file in
  (8 MB, 25 MB] stages as byte-bounded 8 MB parts
  (`<path>.part-0000`, …) plus a `<path>.split.json` sidecar
  (parts, part size, total size, whole-file sha256); the manifest
  entry keeps the logical path and whole-file sha256 with a `split`
  record. Publish uploads parts as ordinary small blobs (a single
  ~15.5 MB base64 blob body 400s on the surrogate publish path even
  though the endpoint accepts ≥15 MB via the PAT helper — probe
  2026-11-04); restore concatenates parts in order and verifies the
  whole-file sha256. The scrub gate scans split files as their
  reassembled whole, so a secret pattern straddling a part boundary
  still aborts the export.

**Excluded always:** `~/workspace/scratch/**`, `~/workspace/vm-backup/**`
(lane state), `~/.config/**` (never a source), any `keys/` directory,
`*.pem`, `*.key`, `*.env`, `tokens.env`, `client_secret*`, `*.pyc`,
symlinks, and two regenerable installs recorded as dir-level excluded
entries: `~/workspace/termux-monorepo` (public-repo mirror) and
`~/workspace/go` (Go toolchain distribution). Excluded files appear in
the manifest as `exported=false` records (no content, no hash) so the
inventory is honest about what was skipped.

## Scrub gate (hard abort, nothing published on any hit)

1. Staged inventory equals the allowlist-derived inventory (diff = ∅).
2. Filename denylist re-checked against the staged tree.
3. Content scan of every staged file for secret shapes:
   PEM key headers (`-----BEGIN … PRIVATE KEY-----` in its real
   header forms), `ghp_…`, `github_pat_…`, `AKIA…`, `sk-…`,
   `Bearer …`. Only offending **paths** are reported, never content.
   The PEM pattern deliberately requires a real header form so the
   fleet's own sensitivity-policy docs — which quote the pattern spec
   with an ellipsis — do not false-positive; every actual key block
   still aborts the export.

Gate results land in `EXPORT.json` next to `MANIFEST.json` at the repo
root of each export commit: `export <EXPORT_ID> t0=<n> t1=<n> gates=pass`.

## Cadence — event/state-gated, no cron, no daemon

The runtime hook **`vm-backup-state-watch`** polls
`~/hooks/scripts/vm-backup-state-watch.sh`, which runs `state_hash.py`:
unchanged → silent; changed (exit 3) → it wakes an agent, whose
instruction is to run the exporter with `--publish`. The exporter
rewrites the marker (`~/workspace/vm-backup/.last-export-state`) only
after a successful publish, so a failed export re-wakes on the next
poll instead of being forgotten.

## Restore

```sh
# obtain a local copy of the backup repo (clone or tarball extract)
python3 restore_vm_workspace.py --backup <backup-copy> \
    --target <restore-root> --source-home <original-home>
```

Restores T0 files to source-relative locations, verifies every sha256,
asserts no excluded path exists in the restored tree, re-hashes every
T1 manifest entry against the live source, and writes `DRILL.json`
(`{verdict, checked, mismatched, excluded_absent, t1_checked,
t1_consistent, t1_missing}`). Drill reports are committed to the backup
repo under `reports/`.

## Custody rule

**GitHub App private keys (any `keys/` dir, `*.pem`) NEVER enter the
backup** — they are excluded by name, by directory, and by the content
gate. Recovery of an App identity is **re-keying**: mint a new key on
the App, install it into a fresh `keys/` dir with 0600 perms. The
backup restores everything needed to know *which* Apps exist and how
they are wired (connector docs, custody metadata) — never the keys
themselves.
