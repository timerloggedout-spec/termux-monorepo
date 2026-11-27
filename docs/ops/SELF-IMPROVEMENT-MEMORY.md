# Self-Improvement Memory — repository adaptation

**Status:** ADAPTED contract; runtime emission and manager consumption remain experimental  
**Work item:** CCEL-007  
**Primary source:** Yu et al., [Self-Improvement Memory Enables Continual Recursive Self-Improvement](https://arxiv.org/abs/2611.18856), 2026-11-13  
**Companion:** [refTemplates/13_Third_Party_Refs/self-improvement-memory-crsi.md](../../refTemplates/13_Third_Party_Refs/self-improvement-memory-crsi.md)

## 1. Research finding

The paper studies **Continual Recursive Self-Improvement (CRSI)**: continuing harness optimization after a compatible benchmark or policy-model change. Its **Self-Improvement Memory (SIM)** belongs to the harness optimizer—the proposer and selector—not the task-solving policy.

SIM groups selected harness edits by recurring problem. Each attempt preserves:
- the diagnosed root cause;
- the harness modification, affected files and rationale;
- the predicted task IDs and expected effect, recorded before evaluation;
- the observed fixed, missed and unresolved task IDs, plus passed/total trial counts;
- the evaluation context: domain, source/target benchmark, source/target policy model, environment and optimization round.

The proposer consults SIM when creating candidates; the selector consults it when evaluating candidates. New selected attempts extend the history rather than overwrite prior attempts. Held-out evaluation remains outside the optimization feedback loop.

### Reported evidence

The 2026-11-13 preprint reports:
- four task domains;
- six cross-dataset continuation settings and four Opus-to-Gemini cross-model settings where Full SIM finished above the harness-only and root-cause-only conditions;
- ten independently evolved coding source runs, followed by paired continuations;
- SIM ahead in nine of ten coding pairs, with a mean paired advantage of 2.36 score points (95% CI 1.05–3.68; paired p=0.003).

The negative result remains material: one coding pair favored continuation without SIM by 0.61 points, and the Gemini 4 Argon generation-chain comparison finished 0.8 points below fresh RSI. The authors also report that an evolved harness can start below a seed harness after a model or benchmark transition.

These are **author-reported preprint results**, not results reproduced by this repository. The paper studies compatible executable harness interfaces, holds policy weights fixed, and identifies limited independent repetitions outside the dedicated coding study. Its companion page reports no public implementation link.

## 2. Repository boundary

SIM is **optimizer memory**, not another general-purpose agent memory service.

| Concern | Existing owner | SIM relationship |
|---|---|---|
| Task/session facts and experience | Hindsight integration | Separate; SIM records why harness changes were made and how they evaluated |
| Canonical execution events and provenance | Agent Evidence Substrate / ATES / Action→Effect | Evidence references only; SIM does not duplicate raw telemetry |
| Manager policy and orchestration | Agent Team Orchestration / MVT / DoE | Proposer and selector are manager-side consumers |
| Deterministic offline policy replay | Evolutionary Replay / Paper2Agent | Replay can compare policy candidates; SIM supplies attributable change history |
| Relationship evidence | Context Relationship Graph | CRG links source files, issues, PRs and evidence; SIM stores references, not graph copies |
| External pattern intake | refTemplates / CCEL | This paper is a research reference and adapted pattern, not a runtime dependency |

Canonical evidence remains repository-owned JSONL/receipts, immutable SHA/run linkage, task cohort, validation results, attribution confidence and Action→Effect records. ATES/WTCV remains observational; it does not become an acceptance score or merge gate.

## 3. Event contract

Schema: [SELF-IMPROVEMENT-MEMORY.schema.json](SELF-IMPROVEMENT-MEMORY.schema.json)

The contract represents one append-only JSONL stream with two record types:

1. `problem_opened` establishes a stable `problem_id`, concise problem summary, root-cause hypothesis, domain and opening round.
2. `attempt_recorded` appends one selector-accepted candidate, with a monotonically increasing ordinal for that problem.

Each attempt binds the change to affected files, a content hash and an artifact reference. It records rationale and prediction separately from measured observation. The attempt's `accepted: true` records the selector's choice; it remains independent of task outcome. A selected attempt may improve, regress, remain neutral or leave predicted tasks unresolved.

The context binds source/target run IDs and commit SHAs, source/target harness versions, source/target policy attribution, source/target benchmark cohorts, environment fingerprints, evaluator, domain, round and candidate/evaluation budgets. Predictions list task IDs before evaluation; observations partition those IDs into fixed, missed and unresolved sets and preserve passed/total trials.

The schema requires:
- an explicit `evolve` evaluation split;
- `held_out_feedback_exposed: false`;
- selected-candidate records to retain improved, regressed, neutral and unresolved outcomes;
- evidence references for every observed attempt;
- 40-character source/target Git SHAs and a SHA-256 change digest;
- strict object shapes with `additionalProperties: false`.

The validator additionally checks stream-level invariants: unique record and attempt IDs, problem-open ordering, contiguous per-problem attempt ordinals, prediction → observation → record chronology, attempt rounds relative to problem opening, disjoint predicted/fixed/missed/unresolved task sets, and passed ≤ total.

The local identity contract uses explicit stable `problem_id` values. The proposer or reviewer assigns a matching diagnosis to an existing identity; a materially different diagnosis receives a new identity. The validator preserves each problem definition across its attempts and leaves semantic matching decisions attributable to the optimizer.

## 4. Local adaptation from the paper

The repository adaptation intentionally differs from the paper in four ways:

1. **Append-only evidence stream.** Store problem and attempt events as JSONL records so history is reviewable and can be linked to GitHub commits and Actions artifacts. Preserve the canonical evidence corpus as the execution source of truth.
2. **Bounded retrieval.** The paper gives the proposer and selector the complete SIM. This repository keeps the full ledger durable but retrieves a bounded, relevance-ranked subset by problem, component, benchmark compatibility and policy context. Retrieval limits are recorded. This controls context cost; it is an explicit adaptation, not a reproduced paper implementation.
3. **Evidence-linked measurements.** Observations point to existing test, workflow, artifact and Action→Effect evidence. SIM does not copy prompts, completions, raw tool arguments, session transcripts or arbitrary provider payloads.
4. **Protected control plane.** Harness candidates execute in isolated, reviewable environments. SIM proposals cannot change human objectives, permissions, credential handling, branch protections, evaluation boundaries, merge rules or repository policy. Those remain governed by existing authorization and promotion contracts.

Source/target policy fields record evidence-backed attribution independently. Unknown provider/model identity remains absent and attribution is marked `unknown`; GitHub actor identity alone is insufficient.

## 5. Operational loop

```text
source run + immutable harness revision
  → diagnose recurring harness problem
  → record prediction and target task IDs before evaluation
  → propose bounded candidate
  → screen and select candidate
  → evaluate on evolve cohort
  → append accepted attempt + observed fixed/missed/unresolved tasks
  → retrieve compatible lessons for next round
  → repeat on a compatible target model/benchmark
  → sealed held-out evaluation
  → compare with seed and harness-only controls
  → fresh online validation + existing promotion gates
```

The incumbent harness remains a comparison/control candidate. A memory match is a hypothesis, not proof that a fix transfers. Re-evaluate inherited changes against the target model, benchmark and environment before retaining them.

## 6. Evaluation design

A first experiment should compare, on the same compatible cohort and budgets:

| Treatment | Starting state | Optimizer memory |
|---|---|---|
| Seed / cold start | canonical seed harness | empty |
| Harness transfer | source-evolved harness | none |
| Problem-only ablation | same source-evolved harness | root causes only |
| Full SIM | same source-evolved harness | root cause + edit + rationale + prediction + observation + context |

Keep policy model, task cohort, candidate count, optimization rounds, evaluator version and execution environment matched within each comparison. Repeat independent source runs where capacity permits. Report starting and final held-out scores, source-task retention, regressions, wall time, token/context cost, tool cost, retries and human intervention. Compare only matched budgets; label unmatched comparisons as non-comparable.

The repository's own quality checks, Action→Effect realization and review findings remain separate outcome evidence. A replay gain or SIM score never authorizes merge or production promotion.

## 7. Validation

Run the focused contract checks:

```sh
python3 -m pytest tests/test_sim_memory.py -q
python3 scripts/ci/validate_sim_memory.py --path /path/to/sim-memory.jsonl
```

The validator accepts an existing ledger path and performs read-only validation. This change establishes the schema and validator; production manager, proposer and selector emission/consumption remain future integration work.

## 8. Sources and limitations

- Paper: https://arxiv.org/abs/2611.18856
- Author companion: https://lucasxinyu.github.io/sim/
- Hugging Face Papers record: https://huggingface.co/papers/2611.18856

The paper is a preprint. Its results describe the tested settings and establish neither universal transfer nor guaranteed improvement after every model/benchmark change. The repository has not independently reproduced the reported experiments. The schema is an adaptation contract, not a claim of implementation equivalence with the authors' system.
