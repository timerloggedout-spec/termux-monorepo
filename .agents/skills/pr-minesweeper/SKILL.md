---
name: pr-minesweeper
description: Classify overlapping Jules/Linguist/Sentinel/Bolt/Codespace PRs. Triggers on minesweeper, lane consolidation, duplicate PRs, drift, or dirty mega-PR triage.
---

# Skill: pr-minesweeper

Read-only classifier. This skill does not merge, close, or force-push.

## Dispositions

| Code | Meaning |
|---|---|
| `NO_GO` | Wholesale / vibe / Class 3-4 — reject |
| `DIRTY_HOLD` | Conflicts vs master — extract on a fresh branch |
| `LANE_DUPLICATE` | >=3 open PRs on the same theme; keep newest unique slice |
| `MERGE_CANDIDATE` | Clean + small — still needs dual gates |
| `EXTRACT_CANDIDATE` | Thin intent; reconstruct from master |
| `MEGA_REVIEW` | >=80 files — CodeRabbit-scale review, not a squash |
| `HOLD` | Default |

## Lane patterns

linguist, sentinel, bolt, SHE, OX-Alpha/DeepSeek, skyhook, MCP hub, palette, ECC, skill-quality, codespaces, historical-backfill, ml-pipelines, dirty-mega.

Duplicate lanes (>=3) are EXTRACT or HOLD, never triple-merged.

## Current HOLD mega (2026-09-18)

#432 (dirty ML init, superseded by extract), #549 (dirty ML rebase, superseded by extract), #523 / #527 (backfill), #455 (mmdc, conflicted), #543 (skill-quality, stale base), #545 (codespaces), #500 (codespaces enablement), #485 (RinDig ICM), Jules lane-consolidation stack #510/#474/#466.
