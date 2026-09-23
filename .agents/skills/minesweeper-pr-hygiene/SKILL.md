---
name: minesweeper-pr-hygiene
description: Detect and neutralize overlapping agent PRs (minesweeper). Prefer extract slices over wholesale merge. Triggers on minesweeper, overlapping PRs, dirty mega, Jules 80+ file PRs.
---

# Skill: minesweeper-pr-hygiene

## Signals

- `changed_files >= 40` on a bot PR
- `mergeable_state=dirty` against a moved master
- Multiple skills-record PRs stacked on stale SHAs
- Title says "fix X" but diff touches unrelated dashboards/docs/workflows

## Response

1. Do **not** merge.
2. Label mentally as EXTRACT or HOLD.
3. Reconstruct the intended slice from master.
4. Close as superseded only after the extract lands.

#630 this session: 89 files, dirty, Jules dashboard fallback — extract the rich-UI fallback only if still missing on master.
