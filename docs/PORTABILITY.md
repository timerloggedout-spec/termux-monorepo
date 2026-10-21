# Portability: why a fresh clone of this monorepo does not work yet

Measured on `master` @ `0d314d7e` (live tip). Current ratchet counters from `scripts/ci/baseline.json`:

| Symptom | Count | Class |
|---|---:|---|
| device_absolute_symlinks | 34 | A / B |
| tracked_backup_files | 116 | D |
| tracked_session_artifacts | 423 | E |
| paths_with_spaces | 452 | F |
| tracked_browser_credential_stores | 115 | — |
| tracked_browser_profile_files | 607 | — |

This is the single highest-leverage finding in the current repo state, and it is
upstream of almost every open PR: **the tree on `master` cannot be reproduced from a
clone.** Not because of missing docs, but because a large share of what looks like
source is either a dangling symlink into one specific Android device, a captured
process-runtime artifact, or an editor backup.

`scripts/ci/repo_gate.py` turns each row into a ratchet counter, so the numbers can
only go down. Nothing below has to be fixed in one pass. Every permanent reduction multiplies future clone, CI, and agent success on free capacity.

---

## Class A — device links to real code and state

These are legitimate on-device wiring. They are just stored in the wrong medium.

```
archwiz/agent_shell.py      -> ~/workspace/llm_map/agent_shell.py
archwiz/archaeologist.py    -> ~/workspace/llm_map/archaeologist.py
archwiz/dispatch_task.py    -> ~/workspace/llm_map/dispatch_task.py
archwiz/impact_oracle.py    -> ~/workspace/llm_map/impact_oracle.py
archwiz/promote.py          -> ~/workspace/llm_map/promote.py
bin/aicli                   -> ~/multi-ai-cli/cli.py
harmony_hub/bin/deepcli     -> ~/deepcli/deepcli.py
…
```

**Why this matters more than it looks.** `README.md`'s Navigation SSOT tells a new
agent or contributor to start with:

| command | resolves to |
|---|---|
| `archaeo <file>` | `archwiz/archaeologist.py` — dangling |
| `oracle <file>` | `archwiz/impact_oracle.py` — dangling |
| `dispatch <task>` / `agent-shell run` | `archwiz/dispatch_task.py`, `archwiz/agent_shell.py` — dangling |
| `validate_promotion.py` → promote | `archwiz/promote.py` — dangling |

So the documented entry path into the cockpit is 100% unreachable from a clone,
while `git ls-files` reports all five as present. That is worse than absent: tooling,
CI, and code review all silently see a file.

Note also that `archwiz/dispatch_pipeline.py` — the file PR #5 and PR #6 both patch —
is a **real** file, while its sibling entrypoints are links. The dispatch fix is
therefore reviewable, but not runnable from a clone.

### Remediation

1. **Now (this PR):** `scripts/links.manifest` declares every Class A link and
   `scripts/link_local.sh` rebuilds them on-device:

   ```bash
   bash scripts/link_local.sh --check   # audit
   bash scripts/link_local.sh           # create/repair
   ```

   Declarative, re-runnable, and `$HOME`-relative via `TERMUX_HOME`/`PREFIX`, so it
   also works on a second phone or a laptop mirror.

2. **Next:** decide per link whether the canonical copy belongs *in* the repo.
   - `archwiz/{agent_shell,archaeologist,dispatch_task,impact_oracle,promote}.py`
     are source. Vendor the real bytes at `workspace/llm_map/` (already a tracked
     directory) and make `archwiz/` hold **relative** links, which survive cloning.
   - `archwiz/{HANDOFF,foresight_state,master_tasks}.json`, `metrics_log.jsonl`,
     `archwiz/synthegration_exports` are mutable state. Keep them out of git and
     leave them to `link_local.sh`.
   - `colab-cli/lib/*` point into `refTemplates/`, which `.gitignore` excludes by
     policy — keep them link-only and document the `refTemplates` prerequisite (see
     `recreate/refTemplates-skeleton`, which is the metadata-only restore policy).

3. **Then:** `git rm --cached` the Class A links whose real content got vendored, and
   lower the `device_absolute_symlinks` counter in `scripts/ci/baseline.json`.

## Class B — process-runtime junk (remove outright)

```
deepcli/browser-data/Singleton{Cookie,Lock,Socket}
deepseek-cli/browser-data-account2{,-clean,-fresh}/Singleton{Cookie,Lock,Socket}
.config/pulse/ea15058254cf2f73285e4f3e6a0a21a2-runtime
.termux/shell
```

Chromium singleton locks encode a **live PID and hostname** (`localhost-28175`) and a
per-launch tmp socket path. PulseAudio's is a dead tmp dir. `.termux/shell` is a
per-install preference. None of these are meaningful in any other checkout, and the
`browser-data*` trees are already gitignored — the links predate those rules.

```bash
git rm --cached -- \
  'deepcli/browser-data/Singleton*' \
  'deepseek-cli/browser-data-account2*/Singleton*' \
  '.config/pulse/*-runtime' \
  '.termux/shell'
```

## Class C — relative links, already fine

`workspace/llm_map/4_51GH7_collect.py`, `4_51GH7_state.json`, and
`_TOOL_TAXONOMY/delta/latest.json` are intra-repo relative links. Leave them. They
are the pattern Class A should be migrated toward.

## Class D — tracked backup copies (current: 116)

Git already is the backup. The gate blocks *new* ones
(`no-committed-backups`) and counts the existing pile. Sample retirement previously reduced 120→116.

## Class E — tracked session-store artifacts (current: 423)

Already the subject of **PR #3** (`agent/repository-hygiene`, draft).
That PR is correct and should land. Two things to fix first:

- `.gitignore` lists `.deepcli/session_store/`, but ignore rules never untrack
  already-tracked files — which is exactly why 423 remain.
- Untracking only fixes the tip. The blobs stay reachable in history, so **credential
  rotation comes first**, then a separately reviewed history rewrite. PR #3's own
  follow-up section says this; it should be a hard gate on merge, not a note.

## Class F — paths containing spaces (current: 452)

Almost entirely session filenames. These break every unquoted `for f in $(...)` loop in `*.sh`. Class E's removal takes most of this with it; that is why the two counters
are tracked separately.

---

## Local gate

Same code CI runs, no installs, no network, no device access:

```bash
python3 scripts/ci/repo_gate.py                 # hard checks + ratchet
python3 scripts/ci/repo_gate.py --ratchet-only  # just the debt counters
python3 scripts/ci/repo_gate.py --write-baseline
```

The gate reads the git **index** and `git cat-file`, never the working tree, so it
behaves identically in a sparse checkout, with submodules uninitialised, and in the
presence of dangling links.

**Next highest-leverage opportunity:** retire a small batch of Class D `.bak` files (e.g. `deepcli-tui/tui.py.bak`, `workspace/maxc/*.bak`) to lower the tracked_backup_files counter permanently. Every reduction compounds clone and CI success on free-tier capacity.
