---
name: tracelens-analysis-orchestrator
description: >-
  Orchestrates modular PyTorch profiler trace analysis with TraceLens: generates perf
  reports, prepares category data, runs system-level and compute-kernel subagents in
  parallel, validates outputs, and writes a prioritized stakeholder report (analysis.md).
  Use when the user asks to follow the analysis orchestrator, run the agentic analysis
  workflow, run it from config <run.yaml>, analyze a trace, compare two traces, or
  mentions standalone or comparative TraceLens analysis.
license: MIT
---

<!--
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->

# Analysis orchestrator

Coordinate **system-level** analysis (CPU/idle, kernel fusion, multi-kernel / comm / memcpy) and **compute-kernel** analysis (GEMM, SDPA, elementwise, etc.): one trace load, shared prep, parallel subagents, then aggregation into `analysis.md`.

## Full procedure

Follow **[reference.md](reference.md)** for every step (user prompts, `<prefix>` / `{CMD}` usage, CLI commands, subagent launch text, validation, report `tee` order, and plot embedding).

## Workflow index

```
0. Query User Inputs (interactive answers or a run YAML, Environment Setup) → cache/run_config.yaml
1. Generate Performance Report (one wrapper call on cache/run_config.yaml; semantic pre-processing first)
2. Trace-Quality Gate → Deterministic fallback analysis
3-6. Prepare Category Data (GPU Util, Top Ops, Tree Data, Multi-Kernel Data, Category Filtering)
7. System-Level Analysis (PARALLEL) → system_findings/
8. Compute Kernel Subagents (PARALLEL) → category_findings/
  8.5. Aggregate → priority_data.json::findings[]
9. Validate Subagent Outputs
10. load_findings + Model Identification (subagent) → metadata/model_info.json
    10.2. Analytical Roofline Augmentation (optional; only when <augment_analytical_roofline> is set)
11. Render performance PNG if agent_extension.py is absent
12. Generate analysis.md (orchestrator writes via <prefix> tee), optional extension, embed PNG
```

## Rules

- **Subagents:** Use your runner's subagent primitive (the Task tool in Claude Code or Cursor, `spawn_agent` under Codex) **only** where reference.md says “subagent” (Steps **7**, **8**, **10**, and **10.2**). The orchestrator runs everything else, including Step 8.5, using the command prefix from `<output_dir>/cache/cmd_prefix.txt` (`{CMD}` substitution).
- **Language:** Prefer vendor-agnostic terms (GPU kernels, collective communication, vendor GEMM library, DNN primitives, GPU graph). When quoting trace data, real kernel names are fine.
- **Subagent prompts:** Point each subagent at the checked-in agent file under `TraceLens/Agent/Analysis/skills/analysis-orchestrator/agents/<name>.md` (see reference.md for exact paths and prompt shells).

## Primary outputs

- **Deliverable:** `<output_dir>/analysis.md`
- **Internals:** `system_findings/`, `category_findings/`, `category_data/`, `metadata/`, `perf_report*.xlsx`, CSV folders — see package README for layout.

## Agent layout

Project subagents ship with this skill: `TraceLens/Agent/Analysis/skills/analysis-orchestrator/agents/*.md`.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/amd-skills/tracelens-analysis-orchestrator/skill.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/.federated.json
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/.gitignore
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/EVAL_RUBRICS.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/README.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/evals.json
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/machine.yml
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/analysis_tests/combined_traces_comparative.csv
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/analysis_tests/combined_traces_standalone.csv
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_scripts/generate_ref.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_scripts/kill_eval_jobs.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_scripts/pack_test_archives.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_scripts/run_pi_analysis_in_docker.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_scripts/run_repeatability_parallel.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/aggregate_repeatability.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/compare_lca_partitions.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/manual_eval_checklist.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/merge_results.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/quality_scripted_evals.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/report_section_rules.yaml
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/eval_utils/workflow_scripted_evals.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/README.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/generate_gold_ref.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/partial_test_cases.csv
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/run_partial_tests.sh
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/eval_utils/semantic_partition_scripted_evals.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/partial_tests/eval_utils/semantic_purity_aggregate.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/eval-post-processing/SKILL.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/eval-post-processing/reference.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/eval-post-processing/run_post_processing.py
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/quality-llm-eval/SKILL.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/quality-llm-eval/reference.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/workflow-llm-eval/SKILL.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/evals/skills/workflow-llm-eval/reference.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/reference.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/skill-card.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/templates/analysis_template.md
skills://plugins/amd-skills/tracelens-analysis-orchestrator/templates/sub_agent_spec.md