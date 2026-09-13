# PR Minesweeper

Read-only classification of open PRs so Jules/Linguist/Sentinel/Bolt
lanes stop stacking duplicates against `master`.

Dispositions: `NO_GO`, `DIRTY_HOLD`, `LANE_DUPLICATE`,
`MERGE_CANDIDATE`, `EXTRACT_CANDIDATE`, `MEGA_REVIEW`, `HOLD`.

Authority: this card does not merge, close, or force-push.
Stop at `ml_pipelines/minesweeper/classify.py` and the live snapshot.
