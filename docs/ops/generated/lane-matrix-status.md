# Lane matrix status (2026-10-25T21:20:00Z)

- Master: `fba41626ae10bb5c6428e9fa11dc9f912bb942ce`
- Open PRs: **~60** (fresh recon)
- Oldest tracked: #47 / #48 era

| Lane | Count |
|------|------:|
| CANDIDATE | ~24 |
| EXTRACT | 1+ |
| NEED_EVIDENCE | ~19 |
| SUPERSEDE | ~16 |

## Tip observation (this hourly)

| PR | Base SHA match | mergeable_state | Dual-gate note | Title |
|---:|:--------------:|:---------------:|----------------|-------|
| #1663 | YES (fba41626) | unstable | hygiene+portability SUCCESS; agentic termux smoke SUCCESS; contracts FAIL | ⚡ Bolt: optimize provider registry caching and item matching |
| #1659 | NO | unstable | behind tip | 🛡️ Sentinel: Fix symlink traversal... |
| #1645 | NO | dirty | behind tip | fix: harden Help-Wanted telemetry... |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

## Portability ratchet (baseline.json @ tip)

- device_absolute_symlinks: 34
- tracked_backup_files: 102
- tracked_session_artifacts: 423
- paths_with_spaces: 451
- tracked_browser_profile_files: 607

Next compounding: advance Class B/D untrack or bring #1663 contracts to green + mergeable clean.
