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
