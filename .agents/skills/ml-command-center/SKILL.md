---
name: ml-command-center
description: Repository-native operator command-center projection. Load when ranking PRs, binding dual-gate, or detecting minesweeper drift.
---

# Skill: ml-command-center

Projects a read-only operator view from `ml/pipelines/command_center/`, anchored to repository SSOTs.

- Cross-domain lane×project read model: `ops/tracking/tracking.json`
- PR-disposition projection: `docs/ops/generated/lane-matrix-status.json`
- Dependency lifecycle: `docs/agentic/dependency-phases.json`
- Human approvals: Desk.html / owning Issue or PR; no generic issue hub
- Vocab: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE
- Dual-gate: named jobs on **this** SHA
- Minesweeper peers: EXTRACT, do not overwrite
- Staging-only: #48 #788 stay on master-staging

```text
python3 -m ml.pipelines.cli center
python3 -m ml.pipelines.cli bind
python3 -m ml.pipelines.cli drift
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
```

Agent-Identity: Grok (Administrator)
