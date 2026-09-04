# Agent Evaluation Framework

## Purpose

The Agent Evaluation Framework (AEF) is the measurement layer for the Agentic Development Environment. It turns agent development, provider/model experiments, repository-history replay, Actions execution, and oversight tasks into reproducible evaluation units.

This is broader than a model benchmark: the system evaluates **agents, managers, prompts, tools, orchestration policies, and development environments**.

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
| Deterministic regression | preservation of known-good behavior |
| Repository-history replay | ability to solve previously observed development tasks |
| Tool/API boundary | schema correctness, error handling, retry behavior |
| Agent trajectory | planning, sequencing, recovery, unnecessary-loop rate |
| Patch quality | tests, regressions, scope, maintainability |
| Orchestration | manager/team policy and lane coordination |
| Provider/model | treatment performance under controlled tasks |
| Oversight | Bug Bounty, Help Wanted, CTF, security/developer-skill validation cohorts |
| Long-horizon | stability across repeated development cycles |
| Adversarial | robustness against misleading context and failure conditions |

## DOE/MVT integration

AEF consumes experiment designs from the MVT/DOE layer. Factors may include:

`provider × model × prompt × manager × cohort × sequencing × evaluator × blindness condition`

Use full factorial designs when practical; otherwise use justified fractional-factorial, orthogonal-array, Plackett-Burman, sequential, or adaptive designs. The design choice itself is evidence and must be recorded.

## Blinded evaluation

When identity is not required for execution or safety, use the blind-agent-evaluation skill. Evaluators should receive opaque treatment IDs and sanitized evidence where feasible. Preserve a protected mapping so attribution remains reconstructable after unblinding.

Do not claim double-blind status when provider/model identity can be inferred from response or tooling signatures.

## Repetition and statistical discipline

Stochastic agents require repeated trials and stable cohorts. Do not promote a treatment from a single anecdotal success when replication is feasible. Record sample size, missing observations, failed executions, cohort changes, and evaluator agreement.

For paired tasks, prefer paired treatment comparisons. For many factors, estimate main effects first and expand promising interactions rather than blindly executing every Cartesian combination.

## #390 use case

PR #390 is a useful repository-history benchmark candidate because it contains a real agent-generated documentation/test change and a large event/comment history. It must **not** be treated as a benchmark merely because it is large or agent-authored. A benchmark extraction should define a bounded task instance, freeze the source context, establish objective success criteria, and preserve the source SHA/PR/run evidence.

A suitable replay cohort can measure:

1. context ingestion and reconstruction;
2. notation/proposal consistency;
3. test creation and execution;
4. cross-file relationship discovery;
5. regression detection;
6. review-quality findings;
7. final patch correctness.

The 2,500-comment history is itself a stress-test dimension, not a quality score. fileciteturn139file0L2-L2

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
VALIDATE  ← Agent Evaluation Framework
  ↓
DEVELOP
  ↓
LEARN
  └────────→ improved BROAD
```

AEF is therefore not a leaderboard alone. It is the **validation substrate for continuous BIUDL improvement**.

## Related systems

- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd`
- `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md`
- `docs/ops/LEAD-LAG-INDEX.md`
- `docs/ops/SCOUT-MISSIONS.md`
- `docs/ops/SCOUT-ROSTER.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `.agents/skills/blind-agent-evaluation/SKILL.md`
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- Issue #337 — Continuous Evaluation
- Issue #342 — Evaluations / LeaderBoards / 3L0
- Issue #390 — notation-set history/replay candidate
