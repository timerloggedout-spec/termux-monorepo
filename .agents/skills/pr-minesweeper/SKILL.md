---
name: pr-minesweeper
description: Classify overlapping Jules/Linguist/Sentinel/Bolt PRs. Triggers on minesweeper, lane consolidation, duplicate PRs, or drift.
---

# Skill: pr-minesweeper

Duplicate lanes (>=3 open PRs on the same theme) are EXTRACT or
HOLD, never triple-merged. Dirty mega PRs stay NO_GO. MERGE_CANDIDATE
still needs gates + review.
