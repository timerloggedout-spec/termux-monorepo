---
name: pr-minesweeper
description: Classify overlapping Jules/Linguist/Sentinel/Bolt PRs. Triggers on minesweeper, lane consolidation, duplicate PRs, or drift.
---

# Skill: pr-minesweeper

Duplicate lanes (>=3 open PRs on the same theme) are EXTRACT or
HOLD, never triple-merged. Dirty mega PRs stay NO_GO / DIRTY_HOLD.
MERGE_CANDIDATE still needs gates + review.

#432 (ML pipelines, 138 files, dirty) is MEGA + DIRTY_HOLD — rebase
as a master-based extract, do not merge the stale base.
#263 is DIRTY_HOLD. #264 is closed.
#499 (devcontainer, 1 file) is small but mergeable_state=unstable.
