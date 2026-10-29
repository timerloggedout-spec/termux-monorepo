# Portability: why a fresh clone of this monorepo does not work yet

Measured on `master` after operator restore of Class D backups (2026-10-29).

**Portability (operator definition):** separation of files for **releases** —
what ships vs what stays in the full GitHub tree. It is **not** authority to
delete kept material (including `.bak`) from GitHub.

| Symptom | Count | Class |
|---|---:|---|
| Tracked symlinks | 45 | — |
| …dangling in this clone | 42 | — |
| …pointing at `/data/data/com.termux/...` | 34 | A / B |
| Tracked `.bak*` / `.old` / `.backup` copies | 100 | D (kept in full repo) |
| Tracked agent session-store artifacts | 423 | E |
| Tracked paths containing spaces | 451 | F |

`scripts/ci/repo_gate.py` tracks debt counters. Class D backups are **not**
tip-deleted. Release packaging may exclude them; the GitHub tree keeps them.

## Class D — tracked backup copies (kept in full repo)

Operator correction (2026-10-29): `.bak` / `.old` / `.backup` copies are
**kept material**. GitHub is the backup. Prior Class D tip-deletions under
“Git is the backup” were wrong relative to that rule and have been restored
from history onto the tip.

Portability means release separation (exclude from release packages if needed),
**not** deletion from the repository. The `no-committed-backups` hard fail is
disabled. Ratchet count records presence; it does not authorize purge.
