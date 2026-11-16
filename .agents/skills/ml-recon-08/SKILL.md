---
name: ml-recon-08
description: Observe-only Issue #175 recon binder v0.8.0. Load before ranking PRs, separating product SHA from observer tips, or touching minesweeper peers.
---

# Skill: ml-recon-08

Version `0.8.0`. Package `ml/pipelines/recon08/`. Keeps the v0.6.0 command-center DAG.

## Hard rules

1. Product SHA `8d36f149214f4a147932188bc424e7c29b8de444` is the last recorded dual-gate. Observer tip `677a2d72d6c251e4f12e81e1bdba3b787671b2d6` is not a promote.
2. Edit Issue #175 when intent changes. Do not pulse-comment it.
3. Do not restamp `docs/ops/LANE-MATRIX.md`.
4. Wholesale ML and minesweeper peers are EXTRACT. Do not overwrite peer branches.
5. `#48` and `#788` never retarget onto master.
6. Credential notes are names-only (#184).
7. CodeRabbit / Qodo / Devin / Copilot / Vercel are non-gate.
8. PR #1188 is a stale recon07 cut. Do not promote that SHA.

```text
python3 -m ml.pipelines.cli recon
python3 -m ml.pipelines.cli steward
python3 -m unittest discover -s ml/pipelines -p 'test_recon08_*.py'
```

Agent-Identity: Grok (Administrator)
