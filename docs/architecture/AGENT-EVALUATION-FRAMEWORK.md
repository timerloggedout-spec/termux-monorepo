# Agent Evaluation Framework

## Purpose

The Agent Evaluation Framework (AEF) is the measurement layer for the Agentic Development Environment. It turns agent development, provider/model experiments, repository-history replay, Actions execution, and oversight tasks into reproducible evaluation units.

This is broader than a model benchmark: the system evaluates **agents, managers, prompts, tools, orchestration policies, providers/models, and development environments**.

## Evaluation unit

An evaluation record identifies:

`evaluation_id + experiment_id + task_family + task_instance + cohort + treatment_id + manager + sequencing`

and links it to:

`provider/model + prompt/version + request + SHA + workflow/run/job/step + logs/artifacts + evaluator + outcome`.

## Task outcome

Outcome is primary and separate from operational signals:

- `PASS` — success criteria satisfied with sufficient evidence.
- `FAIL` — criteria not satisfied.
- `PARTIAL` — useful result with material unmet criteria.
- `UNKNOWN` — insufficient or conflicting evidence.
- `ERROR` — execution could not produce a valid evaluation.

Latency, token count, quota, cost, retries, and availability are secondary measurements. **Correctness and integrated task outcome outrank latency.**

## Benchmark families

| Family | What it measures |
|---|---|
| SWE-agent reference | software-engineering agent treatments using pinned user-owned SWE-agent forks |
| SWE-bench family | standardized real-world issue-to-patch resolution |
| Deterministic regression | preservation of known-good behavior |
| Repository-history replay | ability to solve previously observed development tasks |
| Custom environment | performance under repository-specific tool/runtime conditions |
| Tool/API boundary | schema correctness, error handling, retry behavior |
| Agent trajectory | planning, sequencing, recovery, unnecessary-loop rate |
| Cognitive regression | degradation after context, prompt, tool, or orchestration changes |
| Patch quality | tests, regressions, scope, maintainability |
| Orchestration | manager/team policy and lane coordination |
| Provider/model | treatment performance under controlled tasks |
| Oversight | Bug Bounty, Help Wanted, CTF, security/developer-skill validation cohorts |
| Long-horizon | stability across repeated development cycles |
| Adversarial | robustness against misleading context and failure conditions |

## SWE fork cohort

The user-owned `timerloggedout-spec/SWE-agent_fork` and `timerloggedout-spec/mini-swe-agent_fork` are first-class **reference treatments**. They are not copied into this monorepo and are not routing authorities. Each run should pin an exact fork revision and retain upstream/fork lineage.

The historical `feat/swe-performance-evaluation` branch is preserved as lineage evidence. Current master reconciled its useful implementation without wholesale-merging a stale branch.

See `docs/evaluations/swe-performance/COHORTS.md` for the cohort matrix and admission/culling rules.

## DOE/MVT integration

AEF consumes experiment designs from the MVT/DOE layer. Factors may include:

`agent × provider × model × prompt × manager × cohort × sequencing × evaluator × blindness condition`

Use full factorial designs when practical; otherwise use justified fractional-factorial, orthogonal-array, Plackett-Burman, sequential, or adaptive designs. The design choice itself is evidence and must be recorded.

## Blinded evaluation

When identity is not required for execution or safety, use the blind-agent-evaluation skill. Evaluators should receive opaque treatment IDs and sanitized evidence where feasible. Preserve a protected mapping so attribution remains reconstructable after unblinding.

Do not claim double-blind status when provider/model identity can be inferred from response or tooling signatures.

## Repetition and statistical discipline

Stochastic agents require repeated trials and stable cohorts. Do not promote a treatment from a single anecdotal success when replication is feasible. Record sample size, missing observations, failed executions, cohort changes, and evaluator agreement.

For paired tasks, prefer paired treatment comparisons. For many factors, estimate main effects first and expand promising interactions rather than blindly executing every Cartesian combination.

## #390 use case

PR #390 is a **quick repository-history churn case study**, not a canonical SWE-bench instance. It highlighted why event/comment volume, context reconstruction, relationship discovery, and change-effectiveness must be measured without confusing activity with value.

A bounded replay cohort can measure:

1. context ingestion and reconstruction;
2. notation/proposal consistency;
3. test creation and execution;
4. cross-file relationship discovery;
5. regression detection;
6. review-quality findings;
7. final patch correctness.

Large comment/event history is a stress dimension, not a quality score. The benchmark seed is `benchmarks/repository-history/pr-390.yaml` and must remain linked to source SHA/PR/run evidence.

## Agent-team evaluation

Scout proposes benchmark tasks and candidate treatments. Managers select or generate experiment plans. Workers execute in isolated lanes. Independent evaluators score frozen evidence. MoneyBall/3L0 aggregates results after the evaluation boundary. Synthesis updates skills, SSOTs, and future benchmark cohorts.

## Evidence and anti-regression contract

Every evaluation must be traceable through:

`source state → experiment design → treatment assignment → execution → evidence freeze → evaluation → attribution → decision`.

Compare against a last-known-good baseline where applicable. A regression triggers quarantine/repair analysis; it must not erase the evidence that revealed it.

## No benchmark contamination

The system must distinguish training/context exposure from held-out evaluation. Agents must not be allowed to rewrite hidden tests or benchmark definitions they are being judged against. Benchmark updates require provenance and versioning.

## BIUDL

```text
BROAD
  ↓
INTEGRATE
  ↓
VALIDATE  ← Agent Evaluation Framework + benchmark cohorts
  ↓
DEVELOP
  ↓
LEARN  ← MoneyBall / 3L0 + provenance
  └────────→ improved BROAD
```

AEF is therefore not a leaderboard alone. It is the **validation substrate for continuous BIUDL improvement**.

## Related systems

- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd`
- `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md`
- `docs/ops/LEAD-LAG-INDEX.md`
- `docs/ops/SCOUT-MISSIONS.md`
- `docs/ops/SCOUT-ROSTER.md`
- `docs/evaluations/swe-performance/README.md`
- `docs/evaluations/swe-performance/COHORTS.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `.agents/skills/blind-agent-evaluation/SKILL.md`
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- Issue #337 — Continuous Evaluation
- Issue #342 — Evaluations / LeaderBoards / 3L0
- Issue #390 — notation-set history/replay case study
