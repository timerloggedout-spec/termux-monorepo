---
name: ml-recon-07
description: Observe-only Issue #175 recon binder. Load before ranking PRs, separating product SHA from help-wanted observer tips, or touching minesweeper peers.
---

# Skill: ml-recon-07

Version `0.7.0`. Package `ml/pipelines/recon07/`.

## Hard rules

1. Product SHA `8d36f149` is the last recorded dual-gate. Observer tip `9dc1e437` is not a promote.
2. Edit Issue #175 when intent changes. Do not pulse-comment it.
3. Do not restamp `docs/ops/LANE-MATRIX.md`.
4. Wholesale ML and minesweeper peers are EXTRACT. Do not overwrite peer branches.
5. `#48` and `#788` never retarget onto master.
6. Credential notes are names-only (#184).
7. CodeRabbit / Qodo / Devin / Copilot / Vercel are non-gate.

```text
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
python3 -m unittest discover -s ml/pipelines -p 'test_recon07_*.py'
```

Agent-Identity: Grok (Administrator)
