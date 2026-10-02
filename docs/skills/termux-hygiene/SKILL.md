---
name: termux-hygiene
description: Termux resource + worktree hygiene. Sentinel-gated reclaim, push-before-remove worktrees, rm-safe staged deletes. Invoke when device is under storage or memory pressure, when pruning caches/worktrees, or when writing new heavy tools.
version: 0.1.0
---

# Termux Hygiene

Discipline for a 4-core ARM device with tight RAM and 50 GiB flash.
Every destructive op is gated, logged, and reversible.

## When to invoke

- Sentinel reports `status=PRESSURE` before any bulk write
- Worktree count grows or branches behind origin/master accumulate
- Caches (cargo, npm, pip, uv, whisper, cpan) exceed 200 MiB
- A new heavy tool is about to be written (gate ships in the same commit, not as follow-up)

## Sub-commands

```
hygiene status              # storage + memory + sentinel + worktrees + top home
hygiene audit <path>        # size, type, mtime of one path
hygiene reclaim caches      # clear npm/pip/uv/whisper/cpan caches
hygiene reclaim exports     # archive + delete non-primary synthegration_exports
hygiene worktree <path> <br>  # push to wip/, verify SHA, remove
hygiene doc                 # print session log path
```

## Sentinel thresholds (from termux-resource-snapshot.sh)

| Gate | Threshold | Notes |
|------|-----------|-------|
| memory_available_mib | < 150 | Termux swaps hard below this |
| swap_free_mib | < 128 | Only if swap exists |
| storage_available_mib | < 1024 | Absolute floor |
| storage_used_percent | >= 95 | Independent gate |

PRESSURE trips on **any** one. To return OK you must clear **both** 
`avail > 1024 MiB` **and** `used < 95%`. On a 49 GiB device, 95% = 
roughly 2500 MiB free required.

## Patterns

### Worktree: push-before-remove

```zsh
WT=<path>; BR=<branch>; WIP=wip/${BR//\//-}-$(date +%F)
git -C "$WT" submodule deinit --all --force
SHA=$(git -C "$WT" rev-parse HEAD)
git -C "$WT" push origin "HEAD:refs/heads/$WIP"
REM=$(git -C ~ ls-remote --heads origin "$WIP" | awk "{print \$1}")
[ "$SHA" = "$REM" ] || exit 1
git -C ~ worktree remove --force --force "$WT"
```

Submodules require `--force --force`. Single force fails with 
"working trees containing submodules cannot be moved or removed".
`submodule deinit --all --force` first clears the block.

### Reclaim: archive-then-delete

Never delete a set of directories without an archive created and verified 
in the same block. Pattern:

1. `tar -C <parent> --exclude=<keep> -czf <archive> .`
2. Count top-level entries expected vs. in archive
3. On mismatch, abort. On match, iterate `for d in */` and `rm-safe --confirm "$d"`.

Avoid `tar -T list` on directories with spaces — use `tar -C` + `--exclude`.

### Gate on write

Any new tool that writes > 10 MiB ships with a `_pressure_gate()` at the 
top of `main()`. Snippet (see `hs-pack` for the working copy):

```python
import subprocess as _sp
def _pressure_gate():
    snap = Path.home()/".local/bin/termux-resource-snapshot.sh"
    if not snap.is_file(): return
    out = _sp.run([str(snap)], capture_output=True, text=True, timeout=10).stdout
    if "status=PRESSURE" in out:
        sys.exit("refusing: Termux reports PRESSURE")
_pressure_gate()
```

## Anti-patterns burned

1. **Writing without a gate.** hs-pack chunked a 29 MB source into 124 parts, 
filling 100% of the device before any user-visible failure.
2. **Ignoring the sentinel that was already on disk.** It said PRESSURE 
before the write.
3. **`rm` at prompt without `rm-safe --confirm`.** Every refusal is a save.
4. **Trusting pipes.** `git ... | tail -1` masks exit codes. Verify by 
re-reading real state.
5. **Heredocs in interactive zsh.** Use `printf` with single-quoted args, 
or a file via `mv`.
6. **`mapfile` / `readarray`.** Bash-only. Use `for x in */` glob loops.
7. **`/tmp` writes.** Termux has no `/tmp`. Use `~/.cache/hs-research/`.
8. **Confusing paths.** `~/.cache/whisper` (Python pkg) vs 
`~/forensic-indexer/whisper.cpp` (source+models).

## Reserved for explicit owner approval

- `~/forensic-indexer/whisper.cpp/models` — pipeline input
- `~/CTranslate2` — active
- `~/.opencode` — active tool
- `~/.deepcli/session_store` — canonical
- Anything under `/storage/emulated/0/Android/{data,obb,media}`
- Any `am` / `pm` / intent fire
