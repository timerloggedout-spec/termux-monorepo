# ITEMS — leaderboard-aggregation

| ID | Work | Priority | Owner | Status | Evidence |
|----|------|----------|-------|--------|----------|
| LBA-01 | Register source, schema, retention, and feature-only policy | P2 | jules | done | This MANIFEST.md, ITEMS.md, `docs/proposals/registry.yaml` entry |
| LBA-02 | Implement normalized observation collection for approved sources | P2 | | blocked | Waits on LBA-01 acceptance |
| LBA-03 | Implement deterministic ranking and matrix generation | P2 | | blocked | Waits on LBA-01 acceptance |
| LBA-04 | Add scheduled publication workflow with bounded artifacts | P2 | | blocked | Waits on LBA-01 acceptance |
| LBA-05 | Add tests, source diagnostics, and operator documentation | P2 | | blocked | Waits on LBA-01 acceptance; gate files (`scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`) absent from this checkout |