# Actions metrics correlation — 2026-08-24

Sources:

- `docs/ops/generated/actions-metrics-job-failures-2026-08-24.csv`
- `docs/ops/generated/actions-metrics-total-minutes-2026-08-24.csv`
- Workflow runs pages for high-failure rows
- SHE 0.3.1 on master (`ab1144b` + telemetry commit `c30d19e`)

## Priority matrix (multi-P0.*)

| Rank | Workflow | Failure % | Runs (approx) | Minutes | Class | Disposition |
|------|----------|-----------|---------------|---------|-------|-------------|
| P0 canary | agentic-repository-operations-report.lock.yml | **100%** | 6–7 | ~35 | workflow-failure | Primary L0 canary. Activation + AIC pass; Copilot CLI step fails. Quota ≠ prevention. `intents_for_workflow_failure` ready. |
| P0 secondary | continuous-evaluation.yml | **~48%** | 54 | ~278 | workflow-failure | High volume × rate. Ingest + L0 planner target. |
| P0 secondary | dependency-phase-project-sync.yml | **~78%** | 9 | ~9 | phase-sync | Low volume, high rate. Observe + bounded retry. |
| P0 secondary | ox-alpha-smoke.yml | **~71%** | 7 | ~7 | smoke-ish | Small consistent canary. |
| Observe | repository-observatory / openrouter-free-catalog-sync | 100% | 1 each | 1 | single-shot | Recur → promote; else ignore. |
| High volume | peer-review-orchestrator.yml | ~17% | 4652 | **~6525** | noise / expected | Dominant minutes. Authority > ranking. |
| Healthy | agent-review-auto-jules, agent-feedback-linear-sync, deepseek-ci, gemini-*, repo-gate, termux-smoke | <10% | high | high | promotion/gate | Keep as green signals. |
| Zero | codeql-advisory, actionlint, most context-relationship*, audit-cycle | 0% | varies | low–mid | stable | No L0 action. |

## Key validated facts

1. agentic-report is **one row** (first in the performance table). Full run history is on its workflow page. All rows correlated.
2. Runs continue to fire on schedule/dispatch even when monthly Copilot quota is exhausted; failure is isolated to the agent step after AIC guardrail.
3. SHE P0.1–P0.3 (incident, observers, L0 planner + executor intents + canary helper) implemented. Next thin wire: **live token-bearing Actions re-run job** behind authority gate.
4. CSVs are point-in-time UI exports. Live reconstruction uses `/actions/runs` + `/jobs` + timing (see `docs/ops/ACTIONS-METRICS-INTEGRATION.md`). Dated snapshots retained for time-series.

## Next increments (authority-gated)

1. Wire live re-run job that consumes `L0Intent(target=actions_rerun_failed_jobs, run_id=…)`.
2. Optional: scheduled aggregator that writes the next dated CSV pair from the public API.
3. CE / dependency-phase / ox-alpha remain secondary canaries; do not expand scope until primary wire lands.

Refs: #348 #347 #175 #337  
Agent-Identity: ArchW1z / Grok (Administrator)
