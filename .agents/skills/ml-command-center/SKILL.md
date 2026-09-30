---
name: ml-command-center
description: Operator command-center projection for Issue #175. Load when ranking PRs, binding dual-gate, or detecting minesweeper drift.
---

# Skill: ml-command-center

Projects the live operator board from `ml/pipelines/command_center/`.

- Hub issue: #175 (edit body, never pulse-comment)
- Vocab: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE
- Dual-gate: named jobs on **this** SHA
- Minesweeper peers: EXTRACT, do not overwrite
- Staging-only: #48 #788 stay on master-staging

```text
python3 -m ml.pipelines.cli center
python3 -m ml.pipelines.cli bind
python3 -m ml.pipelines.cli drift
```

Agent-Identity: Grok (Administrator)
