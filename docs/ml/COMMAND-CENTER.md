# ML command center

Observe-mode command-center projection over repository-native SSOTs.

- Package: `ml/pipelines/command_center/`
- Cross-domain lane×project read model: `ops/tracking/tracking.json`
- PR-disposition view: `docs/ops/generated/lane-matrix-status.json`
- Dependency lifecycle: `docs/agentic/dependency-phases.json`
- CLI: `python3 -m ml.pipelines.cli center`
- Vocab v2 only (no HOLD/WAIT/OBSERVE)
- Dual-gate bind on **this** SHA
- Minesweeper drift report
- Extract planner (mega + staging-only)

Does **not** restamp `docs/ops/LANE-MATRIX.md`.
Does not write to any issue or create heartbeat comments. Human decisions remain on Desk.html / the owning Issue or PR.
