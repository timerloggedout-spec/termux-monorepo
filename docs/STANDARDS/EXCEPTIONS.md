# Hook and guard exceptions

Every bypass of commit-msg, pre-commit, rm-safe, or git-stash-safe is
logged here with date, author, reason, and revert plan.

| Date | Bypass | Reason | Reverted |
|---|---|---|---|
| 2026-09-30 | `core.hooksPath=/dev/null` | Habits pre-dating hooks | Yes — 39f20c56 onward runs hooks |
