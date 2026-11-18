---
name: multivariate-doe
description: Design controlled agent, skill, model, prompt, tool, and orchestration competitions as evidence-bearing Design of Experiments (DOE), including Approxination-backed skill comparisons.
---

# Multivariate DOE / MVT Skill

## Purpose

Design agent-team experiments as evidence-bearing **Design of Experiments (DOE)** rather than an uncontrolled collection of A/B requests. Use this skill whenever competing skills, prompts, models, providers, managers, tool layers, queues, or workflow policies are being compared.

## Terminology

- **MVT**: multi-factor experimentation where multiple factors and levels may vary.
- **RCT**: randomized controlled experiment; useful when causal comparison is the objective.
- **RMT**: retain this term only when a project source explicitly uses it; do not silently redefine it as a universal scientific synonym for MVT.
- **DOE**: the umbrella experimental-design discipline used here to choose informative treatments efficiently.
- **Multivariate-outcome analysis**: multiple response variables measured on each experimental unit. Not a synonym for MVT.
- **ANOVA**: an analysis method that partitions response variation into modeled sources. It is not an experimental design.
- **Full factorial**: every specified factor-level combination, when feasible and justified.
- **Fractional factorial / screening**: deliberately sample combinations when the full design is too large; document interaction assumptions.
- **Orthogonal arrays / Taguchi-style designs**: use only when their assumptions match the experiment.
- **Plackett-Burman**: screening design for many factors when main effects are the primary target.

## Agent-team factors

Default factor space:

`provider × model × prompt × manager × cohort × sequencing`

Extend when justified with skill version, tool mode, task family, task instance, scope/ref, context budget, concurrency policy, validation policy, reviewer, environment image, and recovery policy.

Canonical expanded matrix: `docs/ops/DOE-QUESTIONS-MATRIX.md`. DESIGN records cite its dimensions by number.

## Mandatory approximation competition for skill work

Substantive skill creation or upgrade must compete alternatives before adoption. Route through `.agents/skills/approxination-lane/SKILL.md`.

Minimum candidate set when feasible:
1. incumbent repository skill or no-skill baseline;
2. strongest sourced candidate discovered through Approxination or pinned external references;
3. independently designed candidate grounded in repository requirements.

If three distinct candidates are not feasible, record the reason and downgrade the conclusion; do not fabricate variants.

Keep two dimensions distinct:
- Approxination Benchmark A/B/C/D are fixed tool-surface treatments (cold/no tools, Approx CLI + Brave, skills.sh + Brave, Brave-only).
- Candidate skill implementations are separate treatment levels (incumbent, sourced, independent, etc.).

Do not claim that a formal Approxination benchmark ran unless its exact fork SHA, task set, solver/judge, run artifacts, and results are present. If hosted Approxination is unavailable, perform and label an offline comparison; formal hosted competition remains NOT RUN.

## Design rules

1. State the hypothesis and primary outcome before running treatments.
2. Define factor names, levels, and immutable treatment identities.
3. Separate same-task treatment from adversarial/reviewer prompt variants; they answer different questions.
4. Randomize or rotate treatment order where ordering can confound results.
5. Block known nuisance variables (task family/difficulty, environment, provider/quota window, execution slot) when appropriate; record the block rationale.
6. Preserve a stable task cohort/ref so code or dataset changes do not masquerade as treatment effects.
7. Record manager/policy and skill versions independently from provider/model identity.
8. Do not use latency as a correctness proxy.
9. Record resource/quota state as a capacity variable, not a quality score.
10. Repeat promising treatments on held-out or fresh tasks before promotion.
11. Preserve negative, skipped, unavailable, censored, and failed observations.
12. Avoid p-hacking: do not choose design or metrics after seeing results solely to obtain a preferred winner.
13. If the design changes midstream, create a new cohort/version and retain the prior ledger.
14. Declare confounded or unbalanced comparisons; do not repair them by silently dropping inconvenient observations.

## Outcome model

`execution/admission → task outcome → correctness → completeness → integration → regression/safety → resource cost`

A route that never executed is not a model failure. A successful HTTP request is not necessarily a successful task. A fast incorrect result cannot outrank a slower verified correct result.

## Adaptive design

```text
screen → identify signal → expand promising interactions
      → replicate → validate → promote/cull
```

The next cohort may allocate more observations to promising treatments, but retain a baseline/control lane so improvements remain comparable. Sequential allocation must preserve the exploration/control evidence needed to avoid winner's curse.

## Analysis and reporting

Report primary and secondary outcomes separately. Include:
- assignment method and order;
- block variables and balance;
- cohort/task coverage;
- treatment and source revisions;
- per-task and per-category results;
- uncertainty and evaluator disagreement;
- missingness, censoring, failures and non-admission;
- interactions actually tested (not assumed);
- replication and decision.

Pairwise preferences/ELO are useful, but not sole truth. An aggregate rank cannot compensate for correctness, safety, or integration failure.

## Scout integration

Scouts may propose candidate factors, free sources, evaluation tasks, security/performance challenges, or new providers. Scouts do not promote themselves or their proposals. Managers select experiments; telemetry records actual execution; reviewers challenge conclusions.

## BIUDL integration

`broad population → focused experiment → thin validated slice → feed-forward synthesis → broadened population`

The experiment ledger is durable evidence, not disposable benchmark output.

## Required experiment record

At minimum:
- experiment/cohort ID and hypothesis;
- factor names/levels and assignment;
- provider/model/skill/tool/manager identity and source;
- task/ref SHA and dataset version;
- sequence/order and block;
- workflow run/job identity;
- prompt/context variant;
- execution/admission status;
- outcome and verification evidence;
- correctness, warnings, regressions and severity;
- latency and resource/quota observations;
- evaluator/rubric/analysis method;
- promotion/culling decision;
- uncertainty, missingness and limitations.

## No artificial ceiling

Do not introduce a fixed application-level `max-parallel` or response-token ceiling merely for convenience. Adapt admission to live capacity, quota, cooldowns, dependencies, and platform constraints. Provider/model capability metadata and actual output limits remain separate observations.
