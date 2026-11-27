# Self-Improvement Memory / Continual Recursive Self-Improvement

- **Source:** Xin Yu et al., *Self-Improvement Memory Enables Continual Recursive Self-Improvement*, arXiv:2611.18856, submitted 2026-11-13 — https://arxiv.org/abs/2611.18856
- **Companion:** https://lucasxinyu.github.io/sim/
- **Linked paper record:** ../17_Papers/citations/sim-crsi-2026.json
- **Local adaptation:** docs/ops/SELF-IMPROVEMENT-MEMORY.md
- **Disposition (2026-11-27):** ADAPTED contract; runtime emission/consumption remains experimental. No live gitlink or external runtime dependency.

## Transferable pattern

SIM is persistent memory for the **harness optimizer**, not the task-solving policy. It groups harness edits by recurring problem and preserves the rationale, predicted effect, observed result and evaluation context. Both proposer and selector consult the history. New selected attempts extend it, including regressions and unresolved failures.

The paper's CRSI setting continues harness optimization after a compatible benchmark or policy-model change. It compares harness-only transfer, root-cause-only memory and the complete SIM record. The evaluation keeps held-out feedback outside the optimization loop.

## Source-reported evidence

- Four domains are studied.
- Full SIM finishes above harness-only and root-cause-only continuation in six cross-dataset settings and four Opus-to-Gemini settings.
- In ten independent paired coding continuations, SIM wins nine pairs and reports a mean +2.36 score-point difference (95% CI 1.05–3.68; paired p=0.003).
- The study retains counterexamples: one coding pair favors no-SIM by 0.61 points; the Gemini 4 Argon generation comparison finishes 0.8 points below fresh RSI.
- The authors identify compatible executable interfaces as a transfer condition and limited independent repetitions outside the coding study as a limitation.

These are preprint-reported results. This repository has not independently reproduced them. The companion page does not link a public implementation.

## Stored record details

Appendix D specifies run lineage, stable problem IDs, aliases for merged diagnoses, and per-problem attempts containing round, sample, accepted/backfilled flags, edit summary, affected files, predicted/fixed/missed task IDs, passed/total trials and domain. The case studies show why accepted selection and realized task outcome remain separate: selected edits can miss their predicted tasks, and later attempts preserve that history.

## Local adaptation

1. Reuse the repository's existing evidence substrate, ATES, Action→Effect, manager tournament and evolutionary replay contracts.
2. Represent memory as append-only, metadata-only JSONL events. Keep canonical execution records and artifact receipts authoritative.
3. Bind each selected attempt to the source/target SHA, harness artifact hash, model/policy attribution, benchmark/cohort, environment and evaluator evidence.
4. Record prediction separately from measured observation. Retain improved, regressed, neutral and unresolved outcomes.
5. Keep held-out feedback sealed from the optimizer. Use only evolve-split feedback for proposals, selection and memory updates.
6. Retrieve a bounded compatible subset through `scripts/agent_evolution/sim_memory.py` while retaining the complete source ledger. The adapter exposes source/target policy, benchmark and environment compatibility and preserves negative outcomes. This is a deliberate context-cost adaptation; the paper's implementation reads its complete SIM.
7. Keep human objectives, credentials, permissions, branch protections, evaluation boundaries and promotion policy outside the self-editable harness surface.

## Evaluation proposal

Compare seed/cold-start, harness-only transfer, root-cause-only memory and full SIM on the same target cohort, policy, environment, evaluator, candidate budget and round budget. Report starting and final held-out outcomes, source retention, regressions, repetitions, latency, token/context cost, retries and human intervention. Preserve the incumbent. Replay improvement remains candidate evidence; fresh online validation and existing dual gates govern adoption.

## Local status

- Schema: docs/ops/SELF-IMPROVEMENT-MEMORY.schema.json
- Read-only stream validator: scripts/ci/validate_sim_memory.py
- Contract tests: tests/test_sim_memory.py
- Runtime manager integration: NOT YET IMPLEMENTED
- Independent paper replication: NOT YET PERFORMED
