# Multivariate DOE / MVT Skill

## Purpose

Design agent-team experiments as evidence-bearing **Design of Experiments (DOE)** rather than an uncontrolled collection of A/B requests.

## Terminology

- **MVT**: multi-factor experimentation where multiple factors and levels may vary.
- **RCT**: randomized controlled experiment; useful when causal comparison is the objective.
- **RMT**: retain this term only when a project source explicitly uses it; do not silently redefine it as a universal scientific synonym for MVT.
- **DOE**: the umbrella experimental-design discipline used here to choose informative treatments efficiently.
- **Full factorial**: test every specified factor-level combination when feasible and justified.
- **Fractional factorial / screening**: deliberately sample combinations when the full design is too large, while documenting assumptions about interactions.
- **Orthogonal arrays / Taguchi-style designs**: structured designs for balanced factor-level coverage; use only when their assumptions match the experiment.
- **Plackett-Burman**: screening design for many factors when main effects are the primary target.

## Agent-team factors

The default factor space is:

`provider × model × prompt × manager × cohort × sequencing`

Extend it when justified with task family, task instance, scope/ref, tool policy, context budget, concurrency policy, validation policy, and recovery policy.

## Design rules

1. State the hypothesis before running treatments.
2. Define factor levels explicitly and preserve their provenance.
3. Separate the **same-task treatment** from adversarial/reviewer prompt variants; they answer different questions.
4. Randomize or rotate treatment order where ordering can confound results.
5. Preserve a stable cohort/ref so code changes do not masquerade as model effects.
6. Record manager/policy version independently from provider/model identity.
7. Do not use latency as a correctness proxy.
8. Record resource/quota state as a capacity variable, not a quality score.
9. Repeat successful-looking treatments before promotion.
10. Preserve negative, skipped, unavailable, and censored observations.
11. Avoid p-hacking: do not select a design or metric after seeing the result solely to obtain a preferred winner.
12. If the design changes midstream, create a new cohort/version and retain the prior ledger.

## Outcome model

Every treatment should distinguish:

`execution status → task outcome → correctness → integration → regression → resource cost`

A route that never executed is not a model failure. A successful HTTP request is not necessarily a successful task. A fast incorrect result cannot outrank a slower verified correct result.

## Adaptive design

Use sequential experimentation:

```text
screen → identify signal → expand promising interactions
      → replicate → validate → promote/cull
```

The next cohort may allocate more observations to promising treatments, but retain a baseline/control lane so improvements remain comparable.

## Scout integration

Scouts may propose candidate factors, free sources, evaluation tasks, security/performance challenges, or new providers. Scouts do not promote themselves or their proposals. Managers select experiments; telemetry records actual execution; reviewers challenge conclusions.

## BIUDL integration

DOE/MVT follows BIUDL:

`broad population → focused experiment → thin validated slice → feed-forward synthesis → broadened population`

The experiment ledger is durable evidence, not disposable benchmark output.

## Required experiment record

At minimum:

- experiment/cohort ID
- hypothesis
- factor names and levels
- treatment assignment
- provider/model identity and discovery source
- manager/policy version
- task/ref SHA
- sequencing/order
- workflow run/job identity
- prompt variant
- execution status
- outcome and evidence
- correctness/verification notes
- warnings/errors/severity
- latency and resource/quota observations
- analysis method
- promotion/culling decision
- uncertainty/limitations

## No artificial ceiling

Do not introduce a fixed application-level `max-parallel` or response-token ceiling merely for convenience. The experiment manager should adapt admission to live capacity, quota, cooldowns, dependencies, and platform constraints. Provider/model capability metadata and actual output limits remain separate observations.
