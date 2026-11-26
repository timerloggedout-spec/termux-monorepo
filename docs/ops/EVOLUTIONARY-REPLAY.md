# Evolutionary Replay / Paper2Agent Integration

## Status

This is the repository-native implementation of the **AlphaEvolve + Dream-RSI lessons** as an extension of the existing Paper2Agent process. It is deliberately a bounded orchestration/evaluation layer, not autonomous self-training.

## Source-derived design lessons

### AlphaEvolve

Google DeepMind describes AlphaEvolve as an evolutionary coding agent that combines LLM-generated programs with automated evaluators, stores evaluated programs, and uses evolutionary selection to improve promising candidates. Its practical lesson for this repository is: **make the evaluator a first-class contract and optimize against measurable outcomes rather than model preference**.

Reference: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

### Dream-RSI

Dream-RSI treats completed discovery trees as exact replay simulators over the search space that was actually explored. Alternative exploration policies can be replayed against that history without re-executing the underlying work; the deployed incumbent is retained as a candidate so the selected policy cannot regress on the replay objective. The history is then expanded by the next online run.

Reference: https://arxiv.org/abs/2609.14858
Reference implementation/report: https://dream-rsi.com/

### Paper2Agent / z.ai dense feedback

The existing PAPER2AGENT.md requires thin adapters, local/cheap/objectively verifiable feedback, dual-gate evidence, attributable promotion/hold decisions, and explicitly rejects unrestricted recursive self-improvement. This integration keeps those constraints intact.

## Architecture

ONLINE AGENT RUN
  -> discovery history: nodes + realized outcomes
  -> deterministic replay simulator
  -> incumbent + bounded policy mutations
  -> fixed evaluator: score / cost / coverage
  -> selected replay candidate
  -> fresh online cohort
  -> dense feedback + tests
  -> dual-gate promotion

The key separation is **meta-exploration vs task execution**. Replay can improve the manager/exploration policy without repeatedly invoking providers. Actual online execution remains subject to the existing correctness, integration, provenance, security, and promotion gates.

## Implemented primitive

scripts/agent_evolution/replay_simulator.py provides:

- immutable DiscoveryNode records;
- JSONL DiscoveryHistory persistence;
- deterministic ReplaySimulator traversal;
- data-only ExplorationPolicy objects;
- incumbent-preserving EvolutionEngine generations;
- machine-readable evidence_record() output.

No generated code is executed by the simulator. No provider is called during replay. No repository mutation occurs inside the evolutionary engine.

## How this connects to the existing system

| Existing surface | Evolutionary replay role |
|---|---|
| Paper2Agent | research -> thin adapter -> local feedback -> dual gate |
| Adaptive Feedback Cycle | observe -> classify -> verify -> feed forward |
| MVT/DOE | policy/provider/manager/cohort are explicit factors |
| Action/Effect ledger | online execution remains the authoritative action/effect evidence |
| 3L0 / Moneyball | replay score is an experiment feature, not an intelligence claim |
| Context relationship graph | history nodes and experiment records become attributable evidence |
| WAIT -> WATCH -> VALIDATE -> RE-FETCH -> COMPARE | remains mandatory for online runs |

## Promotion contract

A replay improvement is **candidate evidence**, not proof of production improvement. A policy may be promoted only after an online cohort verifies the requested task outcome and existing correctness/integration gates pass. Preserve the incumbent and all candidate results so negative experiments remain usable evidence.

Recommended cohort identity:

manager + policy_version + cohort + task_family + task_instance + history_revision

Recommended observation identity:

manager + task + role + provider + model + workflow_run + head_sha + policy_id

## Guardrails

1. Replay history is exact only over the realized search space; it cannot predict unseen branches.
2. Replay scores must not be presented as task correctness unless the evaluator explicitly measures correctness.
3. Online deployment requires the existing dual gate.
4. No secret, credential, provider response, or raw prompt is persisted by this module.
5. No hardcoded model is required; provider/model identity remains experiment data.
6. The incumbent participates in every evolutionary generation to prevent replay-objective regression.
7. Failed, skipped, unavailable, censored, and negative observations remain evidence.
8. Recursive policy improvement is limited to the exploration-policy representation; it does not rewrite repository source or train model weights.

## First operational use

The first production-facing experiment should use an existing, bounded agent-quality or orchestration cohort:

1. capture the existing online discovery/attempt tree;
2. serialize it as JSONL;
3. replay several manager policies offline;
4. retain the incumbent as the control;
5. select a candidate only when replay improvement is reproducible;
6. deploy one candidate to a fresh cohort;
7. run the normal WAIT -> WATCH -> VALIDATE -> RE-FETCH -> COMPARE loop;
8. compare integrated outcome, correctness, feedback cycles, resource use, conflicts, and human intervention—not replay score alone;
9. feed the new tree back into the history pool.

This is the repository's **BIUDL** interpretation of recursive improvement: broad evidence -> focused replay experiment -> thin online validation -> feed-forward synthesis -> broadened evidence population.


## Longitudinal evidence contract

Replay evidence is an input to the existing Action→Effect / ATES / WTCV / TCV analysis layer, not a replacement for it. Preserve raw replay features and lineage so derived formulas can evolve without rewriting history.

A replay observation should carry, where available:

- manager
- policy_id
- task
- provider
- model
- workflow_run
- head_sha
- cohort
- history_size
- replay_score
- covered_nodes
- replay_cost
- terminal_count
- execution
- verification

Recommended identity:

manager + task + provider + model + workflow_run + head_sha + policy_id + cohort + history_revision

This deliberately separates who/what/where/when from evaluator-derived features. ATES, WTCV, TCV, RPI, action density, parallel yield, TPV, CIE, delay, handoff latency, and complexity-adjusted measures can then be computed downstream using the repository's existing reducers and null semantics.

### Manager tournament extension

Once a sufficient history pool exists, manager candidates can be screened offline:

history revision → incumbent + candidates → replay → raw evidence → existing reducers → fresh online cohort

Do not rank managers on replay score alone. The online comparison must include integrated correctness/outcome, resource use, feedback cycles, conflicts, retries, and human intervention. A candidate that wins replay but loses the real task remains a failed candidate; a candidate that changes cost without changing outcome remains measurable rather than being collapsed into a single opaque agent score.


## DoE-controlled evolutionary planes

The evolutionary replay primitive now participates in the existing DoE family through
`scripts/agent_evolution/doe_control.py`. DoE is the design/control plane; AlphaEvolve
and Dream-RSI mechanisms are bounded candidate-generation and replay components.

### Plane ownership

| Plane | Owner | Contract |
|---|---|---|
| Design/control | DoE family | Freeze hypothesis, factors, levels, incumbent, seed, task blocks, assignment, replication and thresholds before evaluation |
| Candidate generation | EvolutionEngine | Produce bounded data-only policy mutations and preserve the incumbent |
| Replay/evaluation | ReplaySimulator | Evaluate every arm against the same immutable realized history; no provider or task execution |
| Online execution | ATES + existing runner | Execute a selected candidate only in a fresh cohort; emit canonical EXPERIMENT records |
| Analysis/challenge | DoE reducers + Delphi | Report main effects, interactions, uncertainty, missingness, cost and counter-evidence |
| Promotion | Proposal lifecycle + dual gates | Require held-out confirmation, verified task outcome, correctness, integration and same-SHA gates |

These responsibility planes compose existing owners and reuse their orchestrator,
run ledger, scheduler, registry and merge authority.

### Design artifact and confirmation assignment

`docs/ops/corpus/EVOLUTION-DESIGN.schema.json` defines the frozen
`agent.evolution-doe-design.v1` offline design artifact. It records campaign ID,
factor levels, policy arms, incumbent control arm, deterministic seed, design ID and
downstream authorities.

After offline replay selects at most one candidate,
`docs/ops/corpus/EVOLUTION-CONFIRMATION-ASSIGNMENT.schema.json` defines a separate
randomized complete-block assignment containing only the incumbent and that selected
candidate. This separation keeps offline screening distinct from online confirmation.

The per-run observation remains the existing
`docs/ops/corpus/EXPERIMENT.schema.json` record. A design artifact describes what
was planned; an EXPERIMENT record describes one observed execution. Neither artifact
replaces the canonical run ledger.

### Executable adapter

`scripts/agent_evolution/doe_control.py` provides:

- full-factorial policy factor expansion for `max_active`, `min_score` and
  `stop_after_terminal`;
- deterministic arm IDs and exactly one incumbent control;
- design integrity validation and replay of every arm against one shared
  ReplaySimulator/history;
- machine-readable replay rows carrying design, campaign, arm, policy and history
  lineage;
- a separate confirmation assignment that randomizes only the incumbent and one
  selected candidate across task blocks and replicates; and
- fail-closed promotion-readiness receipts that never execute promotion.

Factorial levels are declared before replay. The incumbent is retained even when its
settings are absent from the candidate grid. Duplicate policy configurations collapse
to one arm. Online confirmation assigns both the incumbent and selected candidate
exactly once per task unit × replicate.

### Operating sequence

1. Pre-register the hypothesis, primary outcome, factor levels, practical threshold,
   history revision, evaluator revision, seed, blocks and replication.
2. Replay the incumbent as control and every factorial policy arm against the same
   completed discovery history.
3. Preserve every arm result, including negative, tied and dominated candidates.
4. Select at most one candidate for a fresh online confirmation cohort.
5. Create a separate confirmation-assignment artifact that randomizes only the
   incumbent and one selected candidate within declared task blocks.
6. Emit one canonical EXPERIMENT record per dispatched run and preserve configured
   instance identity, workflow/run SHA and evidence references.
7. Analyze primary and secondary outcomes separately; report main effects,
   interactions, uncertainty, missingness, assignment integrity and total cost.
8. Route conclusions through existing review and proposal lifecycle. Promote only
   after held-out confirmation, verified outcome, correctness/integration evidence
   and both repository gates pass on the same immutable head SHA.

### Interpretation

Replay score estimates performance only over the realized history and evaluator.
It does not estimate unseen branches, task correctness, model intelligence or online
production effect. The online confirmation cohort supplies the external validity
check. A replay winner that fails the real task remains a failed candidate. Unknown
measurements remain unknown; the design and all negative observations remain
append-only evidence.
