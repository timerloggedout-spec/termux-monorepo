# Scientific Specialist & Behavioral Experiment Dispatch

**Proposal type:** `scientific_experiment_system`  
**Status:** in review  
**Related:** issue [#5189](https://github.com/timerloggedout-spec/termux-monorepo/issues/5189), implementation PR [#5190](https://github.com/timerloggedout-spec/termux-monorepo/pull/5190)

## Objective

Establish one governed, evidence-backed capability system for scientific and quantitative work, plus a distinct behavioral-experiment lane for DO Statements and Performance Psychology. Reuse the existing QUE admission, canonical DoE seats, experiment infrastructure, proposal registry, and dispatch machinery. Do not create a parallel queue, role-ID system, or provider-selection path.

## Triggerable intake types

| Proposal / intake type | Issue form | Admission lane | Route |
|---|---|---|---|
| Scientific research and validation | `.github/ISSUE_TEMPLATE/scientific-research-task.yml` | `scientific-quantitative` | `project-task-dispatch.yml` |
| DO Statements + Performance Psychology experiment | `.github/ISSUE_TEMPLATE/behavioral-experiment-task.yml` | `do-statements-performance-psychology` | `project-task-dispatch.yml` |
| General project task | `.github/ISSUE_TEMPLATE/project-task.yml` | `swarm-dispatch` | `project-task-dispatch.yml` |

Each form declares `issue-dispatch/v1`; the existing `swarm-admission` evaluator remains the only admission authority. The issue event is retained as the trigger contract. The route waits for the corresponding post-event admission receipt before intake.

## Capability families

- Scientific governance and domain research
- Mathematics, numerical methods, and formal methods
- Experiment design, measurement, and reproducibility
- Statistics, Bayesian methods, and causal inference
- Machine learning, evaluation, and data stewardship
- Validation, assurance, safety, and adversarial review
- Optimization, control systems, graph science, and complex systems
- DO Statements and Performance Psychology as measurable behavioral experiment lanes

Capability labels describe qualified work; they do not mint new canonical DoE seat IDs. Existing seats remain builder, operator, steward, observer, reviewer, scout, gambler, and participant.

## Experiment governance

- Distinguish exploratory from confirmatory work.
- Pre-register hypotheses, outcomes, factors, controls, analysis, and stopping rules for confirmatory work.
- Preserve unknown, skipped, blocked, censored, negative, and null outcomes; never convert them to success.
- Require independent review for high-impact/confirmatory experiments; author, operator, analyst, and reviewer must not collapse into self-approval.
- DO Statements and Performance Psychology remain separately measurable. Combine them only where the registered hypothesis explicitly requires it.
- Keep DoE as the umbrella, MVT as a design family, ANOVA as an analysis method, and ATES as its existing fixed harness. Promotion remains evidence-gated.

## Siglary and evidence

Use the repository's [Siglary standard](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/notation-sets/SIGLARY-STANDARD.md) for notation, epistemic state, provenance, and record validity. Unknown is represented as JSON null in data records, not serialized sentinel strings. Candidate lane detection is not preregistration and not evidence that an experiment ran.

## QDesk integration boundaries

- `docs/proposals/registry.yaml` is the proposal source of record.
- `scripts/proposals/proposals_feed.py` emits the registry projection.
- `apps/tribute-dashboard/proposals.html` renders proposal type, status, priority, author, and related evidence from the feed.
- `apps/tribute-dashboard/desk.html` remains the operational queue/traversal cockpit. It links to the proposals index but does not become a second proposal database.

## Acceptance gates

1. Preserve `issues.opened` and `issues.reopened` as the project-task route's event dependencies.
2. A matching, post-event QUE admission receipt is required before intake.
3. Deferred, unmatched, stale, and malformed receipts do not dispatch.
4. All triggerable forms use the shared intake headings and admission contract.
5. Contract tests cover admission timing, template identity, lane classification, and Siglary data guard.
6. Proposal type is carried verbatim through the registry/feed/UI; missing types remain unclassified, never inferred.
7. Repo gate and Termux smoke pass; runtime evidence is inspected before promotion.
