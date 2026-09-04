# SWE Agent Evaluation

**Implements:** THUB-007  
**Status:** External/reference evaluation family; repository-local development evidence remains primary.

This evaluation surface connects the user-owned `SWE-agent_fork` and `mini-swe-agent_fork` repositories to the Agent Evaluation Framework (AEF), without turning either fork or an external benchmark leaderboard into routing authority.

## Reference implementations

- [`timerloggedout-spec/SWE-agent_fork`](https://github.com/timerloggedout-spec/SWE-agent_fork) — full SWE-agent reference cohort.
- [`timerloggedout-spec/mini-swe-agent_fork`](https://github.com/timerloggedout-spec/mini-swe-agent_fork) — lightweight SWE-agent reference cohort and existing bounded adapter.
- Historical branch: `feat/swe-performance-evaluation` — retained as lineage evidence. It was 342 commits behind current `master` when reconciled; its useful evaluation implementation was integrated/reworked rather than merged wholesale.

See `docs/evaluations/swe-performance/COHORTS.md` for the cohort matrix and MoneyBall/3L0 treatment schema.

## Benchmark boundary

SWE-bench is a benchmark for real-world software-engineering issues: an environment is prepared, an agent/model produces a patch, and the patch is evaluated against repository tests. The current public family includes Full, Lite, Verified, Multimodal, and Multilingual variants. SWE-bench-Live provides an additional live, multi-language/multi-OS research direction.

External benchmark results are **reference evidence**. They are not interchangeable with this repository's own correctness, review-resolution, coordination, regression, tool-boundary, or resource evidence.

## Invocation boundary

The existing `swe-reference-evaluation.yml` remains a bounded reference adapter. It must pin the external implementation revision and emit a redacted manifest. A successful agent process means only that an evaluation artifact was produced; it does not mean the task was solved.

The long-term direction is agentic/continuous evaluation through the AEF + BIUDL loop rather than a human-only benchmark switch. Any credential-bearing external run must remain explicitly isolated and fail closed when required credentials or evidence are absent.

## Result handling

Results must be reproducible and attributable:

`source state → benchmark/task version → treatment assignment → agent/provider/model → execution → evidence freeze → evaluator → outcome → MoneyBall/3L0 update`

Record task outcome separately from latency, token count, quota, cost, retries, and availability. Do not use a single aggregate percentage as the sole admission/culling criterion.

## #390 is a case study, not the benchmark

PR #390 is a quick repository-history scenario that exposed the **churn problem**. It is therefore a stress-test/use-case seed for context reconstruction, event-volume handling, relationship discovery, and change-effectiveness measurement—not a claim that a large PR/comment history is itself a SWE-bench task.

The existing `benchmarks/repository-history/pr-390.yaml` is the bounded seed. Its evidence should remain linked to the source PR/SHA/run graph and should not be inflated into a quality score merely because the history is large.

## BIUDL / MoneyBall

```text
BROAD → discover agents, forks, datasets, environments, tasks
  ↓
INTEGRATE → register/pin treatments and adapters
  ↓
VALIDATE → deterministic + blinded + trajectory + tool-boundary evidence
  ↓
DEVELOP → improve agent, prompt, manager, tools, orchestration
  ↓
LEARN → update MoneyBall/3L0, skills, SSOT, cohort registry
  └────────────────────────────────────────────→ BROAD
```

Culling preserves provenance. Promotion requires replicated evidence where practical. New benchmark variants, agents, providers, or environments enter as new treatments/cohorts instead of overwriting historical observations.

## Related artifacts

- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- `docs/evaluations/swe-performance/COHORTS.md`
- `docs/evaluations/development-performance/SUITE.md`
- `.github/workflows/swe-reference-evaluation.yml`
- `scripts/ci/swe_evaluation_contract.py`
- `benchmarks/repository-history/pr-390.yaml`
- `docs/ops/LEAD-LAG-INDEX.md`
- `docs/ops/SCOUT-MISSIONS.md`
- `docs/ops/SCOUT-ROSTER.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
