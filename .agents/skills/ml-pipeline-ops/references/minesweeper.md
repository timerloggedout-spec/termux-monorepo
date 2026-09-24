# Minesweeper

Concurrent agents (Jules, Sentinel, Bolt, Devin, Copilot) open overlapping PRs.

- Do not overwrite a WAIT peer's branch.
- Bot author + files>40 → EXTRACT, never wholesale merge.
- Classify with `ml.pipelines.lanes.minesweeper_rules`.
