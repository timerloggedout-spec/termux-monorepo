# PR Minesweeper

Read-only classification of open PRs so Jules/Linguist/Sentinel/Bolt
lanes stop stacking duplicates against `master`.

Dispositions: `NO_GO`, `DIRTY_HOLD`, `LANE_DUPLICATE`,
`MERGE_CANDIDATE`, `EXTRACT_CANDIDATE`, `MEGA_REVIEW`, `HOLD`.

Live 2026-09-13 notes (observe-only):

- **#432** — DIRTY_HOLD / MEGA. Supersede with master-based extract.
- **#263** — DIRTY_HOLD. Extract remaining unique slices only.
- **#264** — closed. Do not reopen for wholesale salvage.
- **#501** — Jules audit consolidate. Treat as lane overlap, not merge.
- **#499** — 1-file devcontainer. Small, but `mergeable_state=unstable`.

Authority: this document does not merge, close, or force-push.
