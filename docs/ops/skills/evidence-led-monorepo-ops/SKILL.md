# Skill: evidence-led-monorepo-ops

**Owner:** ArchW1z / operator continuous admin on timerloggedout-spec/termux-monorepo (and similar agentic monorepos).

**Triggers:** priority matrix, master gates, SHE progress, Manus/provider RE, dirty PR triage, Actions hygiene, "continue", "BIUDL", "maximize actions", full telemetry requests, multi-P0.* handling.

## Posture (non-negotiable)

- **Evidence over anecdote.** Every prioritization must cite live rows, run histories, or committed telemetry artifacts.
- **Full telemetry over isolated canary.** agentic-report is one example from the first row of the performance table — never treat it as the only signal. Correlate *every* row.
- **Quota ≠ run prevention.** Workflow activation (schedule/dispatch + daily AIC guardrail) can succeed while the agent step fails on Copilot/CLI quota. Separate activation success from agent failure.
- **Authority > ranking.** MoneyBall / 3L0 / leaderboard scores are decision-support only. Hard authority, policy, and human gates always dominate.
- **Anti-sprawl.** No source mutation in L0. Prefer thin stacked PRs. No vendoring of upstreams as promotion gates.
- **Multiple P0.** Handle concurrent P0.* classes by fingerprint/classification (workflow-failure, gate-failure, smoke-failure, observe-only for security).

## Primary surfaces

| Surface | URL / path | Use |
|---------|------------|-----|
| Actions performance (UI export) | `/actions/metrics/performance` | Job failure % + avg runtime; export CSV |
| Actions minutes | same page, total-minutes tab | Consumption ranking |
| Workflow runs | `/actions/workflows/<file>` | Per-workflow history |
| SHE | `she/` + `docs/architecture/SELF-HEALING-ENGINE-ROADMAP.md` | P0.1–P0.3 status |
| Telemetry snapshots | `docs/ops/generated/actions-metrics-*-YYYY-MM-DD.csv` | Dated ground truth |

## Workflow (evidence-led loop)

1. **Pull state** — list open PRs/issues, recent master commits, Actions runs for high-failure workflows, committed CSVs.
2. **Correlate rows** — join job-failures CSV + total-minutes CSV + per-workflow run pages. Rank by (failure_rate × volume) then by authority class.
3. **Disposition** — for each P0 class emit: status, evidence links, next thin increment, authority gate required.
4. **Advance SHE** — only L0 intents that do not mutate source; live token-bearing re-run is the next wire after planner+executor intents.
5. **Leave trail** — commit dated CSVs or correlation notes under `docs/ops/generated/`; update skill if process improved.
6. **No sprawl** — one focused branch/PR per thin slice; squash-merge only after green gates.

## P0 classification (current)

| Class | Example signal | L0 target |
|-------|----------------|-----------|
| workflow-failure | agentic-report 100%, continuous-evaluation ~48% | `actions_rerun_failed_jobs` / `actions_rerun_workflow` |
| gate-failure | repo-gate / termux-smoke | `actions_rerun_workflow` / `termux_restart_worker` |
| phase-sync fragility | dependency-phase-project-sync high % | observe + bounded retry |
| security / Dependabot | alerts | `observe_only` |
| high-volume low-failure | peer-review-orchestrator, Jules, Gemini | keep as promotion signals |

## Skill evolution rules

- When operator corrects ("it's a SINGLE EXAMPLE from the first row"), update this skill immediately and commit.
- Prefer reference to live CSVs / API aggregation over re-duplicating numbers in prose.
- Iterative dated CSV snapshots are valuable for time-series; do not delete prior exports.
- Document any new programmatic integration path in `docs/ops/ACTIONS-METRICS-INTEGRATION.md`.

## Anti-patterns

- Fixating on one canary workflow while ignoring the rest of the performance table.
- Treating monthly Copilot quota exhaustion as "runs should not fire".
- Ranking purely by failure rate without volume or authority context.
- Opening broad PRs that mix P0.3 live wire with unrelated refactors.
