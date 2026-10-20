# Incident 2026-10-18: SKILL.md bodies clobbered by recon-stamp writes

**Status:** repaired; guarded; SHE known repair added (L1)
**Fingerprint:** `skill-clobber:<path>:<sha12>`
**Detected by:** `adaptive wait evidence skill contract` (runs 39189436452, 39189448876, 39198792231)

## What happened
Session-recon stamps are meant to append a few lines to a skill's session log. Eleven commits between 2026-10-14 and 2026-10-18 replaced a skill body with a stub instead, or "restored" it only partly.

| Commit | Date (PDT) | File | Body written | Path |
|---|---|---|---|---|
| a822546 | 10-14 09:21 | evidence-led-monorepo-ops | `append note here` (34.6 KB → 16 B) | direct commit (user identity) |
| f8a0b8b | 10-14 09:21 | evidence-led-monorepo-ops | 51-byte stub "restore" | direct commit |
| 1165cc5 | 10-16 20:15 | adaptive-wait, evidence-led, stepie | `PLACEHOLDER`, `PLACEHOLDER_TOO_LARGE` (25.5–68.4 KB → ≤21 B) | direct commit |
| 48ac643 | 10-16 20:15 | evidence-led-monorepo-ops | partial "restore": 466 → 108 lines | direct commit |
| d81927d | 10-18 19:19 | adaptive-wait | `PLACEHOLDER - full content too large for this call` | direct commit |
| 665cef7 | 10-18 19:19 | adaptive-wait | `$(cat /tmp/adaptive-wait.md)` | direct commit |
| 456416b | 10-18 21:18 | adaptive-wait | `$(cat /tmp/adaptive-wait-skill.md)` | direct commit |
| a5135e3 | 10-18 21:18 | adaptive-wait | partial "restore": 662 → 133 lines | direct commit |

Writes of the same files that **succeeded**: df4d059 (10-15, 68 KB, real `git` commit as Grok Administrator, +19 lines); #1238, #1262, #1263 (62–65 KB through PRs).

## Root cause (hypothesis tested)
- **Rejected: "the file got too big (65 KB)."** Clobbers hit files from 25 KB up, and a 68 KB direct git commit succeeded. There is no fixed size threshold.
- **Supported: a whole-file replace through a single tool-call argument.** Every clobber is a direct commit under the user identity (contents-API style write, not a git push or a PR). The writer must inline the full body in one call. When it doesn't, it emits a stub: a template line, a placeholder, or a shell expression that was never expanded because the body is passed as literal text rather than run through a shell. Size makes that choice more likely ("too large for this call") but isn't the mechanism.
- **Contributing: no pre-merge gate.** These commits went straight to master, so the contract check could only report after the fact. Two "restores" also passed or slipped through because they were judged against a stub parent.
- **Latent loss found while replaying history:** `evidence-led-monorepo-ops/SKILL.md` had been missing 357 lines since 48ac643 (10-16). It never failed CI, because its required sections survived.

## Repairs
- #1264 (761162c): adaptive-wait restored to 662 lines plus the 21:16 stamp; order-aware validator.
- This change: evidence-led-monorepo-ops restored from df4d059 (466 lines) plus 6 newer lines. Nothing was lost relative to master.

## Detection and evaluation (scripts/ci/skill_clobber.py)
- Stub patterns cover all observed bodies (corpus in `tests/fixtures/skill_clobber/`), plus a 200-byte stub floor.
- Loss is measured order-insensitively: the parent's non-blank lines are compared as a multiset, so a reorder with everything kept costs 0. More than 50% lost fails; more than 10% warns; `[allow-skill-shrink]` overrides with a warning.
- A change is judged against its parent, unless the parent is itself a stub, in which case it's judged against the last good ancestor. That closes the partial-restore gap.
- Replay over the last 27 SKILL.md changes flags exactly the commits above and nothing else.

## Self-healing (SHE)
`.github/workflows/she-skill-clobber-heal.yml` runs on each master push that touches a SKILL.md. It checks **all** tracked skills, not just the two covered by the contract. When it finds a clobber, it rebuilds the file from the last good body plus any new lines, records a SHE `Incident` (classification `skill-clobber`, authority `L1-known-repair`), and opens a repair PR so the normal gates verify it before merge. On pull requests it runs the unit tests and blocks a clobbering PR.

## Still open
1. Make `adaptive wait evidence skill contract` and the heal workflow's `detect` job required status checks on master, or have stamp writers use PRs, as #1262 and #1263 did. Repo settings change; owner decision.
2. Fix the writer: fetch, append, write; on any size or tool error, skip the stamp and comment instead.
3. Optional: an append-only session archive next to each skill, to keep stamps small. Not needed for correctness now.
4. A heal PR opened with `GITHUB_TOKEN` won't trigger PR gates. Set `OPERATOR_GITHUB_TOKEN` (see the secrets provisioning map) so repair PRs verify automatically.
