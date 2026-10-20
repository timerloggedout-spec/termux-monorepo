# Lane matrix status (2026-10-20T02:10:00Z)

- Master: `2c67628353d095905ea6eff4a004dd69dd24eab5`
- Open PRs: **~144** (search snapshot)
- Closest promote candidate: #963 (base=tip, dual-gate SUCCESS, mergeable_state=unstable)

| Lane | Count |
|------|------:|
| CANDIDATE | ~60 |
| EXTRACT | 5 |
| NEED_EVIDENCE | ~50 |
| SUPERSEDE | ~60 |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

Next highest-leverage: promote #963 if mergeable_state becomes clean, else advance portability ratchet by removing tracked .bak files (120 remaining).
