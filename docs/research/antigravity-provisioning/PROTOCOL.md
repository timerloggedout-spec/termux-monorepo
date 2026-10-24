# MVT / DoE / Moneyball / Delphi operating protocol

**Applies to:** Antigravity CLI provisioning candidates in the research lane  
**Parent:** [#1567](https://github.com/timerloggedout-spec/termux-monorepo/issues/1567)  
**Authority:** recommendations only; implementation/promotion remains an operator decision under normal repository gates.

## 1. Sequence is mandatory

```text
Freeze V0 → validate instructions → define hypotheses and gates
   → isolate V1…Vn candidates → run comparable MVTs
   → collect TLM receipts → Delphi Round 1 (independent)
   → freeze evidence packets → Delphi Round 2 (cross-review)
   → targeted MVT if decision-changing → per-candidate disposition
   → operator decision → normal implementation/release gates
```

Do not begin by extending the existing implementation simply because it exists. V0 is a preserved comparison candidate. V1…Vn must follow validated requirements and record their design delta from V0.

## 2. Candidate packet

Each candidate packet must include:

1. Stable candidate ID, immutable source refs and content hashes.
2. Hypothesis and requirements addressed.
3. Design delta from V0, changed factors, dependencies and assumptions.
4. Expected benefits, costs, risks, complexity and maintenance burden.
5. MVT protocol: scenario, fixtures, preconditions, actor, target, permitted actions, expected mutations, stop conditions, cleanup and rollback.
6. TLM receipts for every run, including failures and missing data.
7. Test assertions, failures, retries, timeouts, resource costs and recovery results.
8. Known unknowns, evidence limitations, strongest objection and next falsifying experiment.
9. Independent review ratings and confidence, recorded before seeing other candidates' scores.

## 3. Design of Experiments

- Freeze scenarios, fixtures, measurement definitions, environment assumptions and resource budgets before candidate scoring.
- Use the same representative scenarios for all candidates whenever possible.
- Isolate each candidate in a separate branch/worktree and evidence bundle; avoid shared mutable configuration and cross-candidate artifacts.
- Use one-factor-at-a-time trials when diagnosing a suspected cause. Use pairwise or factorial designs when factor interactions are material and the budget permits.
- Do not change multiple factors without documenting the confounders and why attribution remains credible.
- Record failed runs, retries, timeouts, partial completions and resource/quota usage. Repeats are for reproducibility, not for retrying an operational action without authorization.
- Mark unavailable evidence unknown. A skipped test is not a pass.
- If platforms, versions, fixtures or budgets differ materially, do not report a clean head-to-head result.

## 4. MVT safety and scope contract

Every Minimum Viable Trial must be the smallest experiment that could falsify one stated hypothesis. Before execution, record:

- trial owner and collaborators;
- existing authorization reference and authorized actor;
- exact target device/workspace and identity preconditions;
- allowed action categories and expected mutations;
- data collected and redaction/retention policy;
- resource/time budget and stop conditions;
- recovery path, rollback steps and independent access requirement;
- pass/fail/unknown criteria and evidence destination.

Existing authorized collaborator access and in-progress provisioning are part of the real baseline. This protocol does not retroactively prohibit them. It also does not expand their scope. Any additional actor, target, permission, data collection or mutation outside existing authorization requires explicit approval. Do not infer authorization from technical capability.

## 5. TLM receipt rules

Use [TLM-RUN-RECEIPT.md](TLM-RUN-RECEIPT.md) as the common contract. Reuse existing compatible receipts instead of duplicating telemetry. Keep observed telemetry, interpretation, reviewer opinion and operator decision distinct. Redact credentials, private prompts/completions, keys, unrelated files and sensitive command arguments. Hash the exact candidate inputs and outputs when appropriate.

## 6. Moneyball scoring

Apply hard eligibility gates before weighted scoring. A safety failure or missing mandatory requirement makes a candidate blocked/ineligible; convenience must not offset it.

Suggested 0–5 dimensions for eligible candidates:

| Dimension | Meaning |
|---|---|
| Requirement correctness | Required behavior is demonstrated by assertions, not claims alone |
| Evidence strength | Provenance, directness, completeness and independent corroboration |
| Repeatability | Consistent outcomes across defined repetitions |
| Safety/reversibility | Least privilege, bounded effects, clear rollback and recovery |
| Platform feasibility | Verified support on the intended Termux/Android/runtime target |
| Recovery behavior | Detection and recovery are observable and tested |
| Operational simplicity | Setup burden, cognitive load and failure diagnosability |
| Maintenance cost | Long-term upkeep, dependencies and compatibility risk |
| Resource efficiency | Time, storage, memory, network and quota/cost within defined budgets |

Publish raw measurements beside ratings. State dimension weights and why they reflect the use case. Run sensitivity analysis across plausible weights and report whether the ranking changes. Include uncertainty and sample size. Do not reward a candidate for commit count, recency, amount of code or sunk cost. Prefer the simplest candidate meeting all mandatory requirements unless a more complex candidate shows a meaningful, repeatable benefit.

## 7. Delphi Round 1 — independent

Each reviewer evaluates each candidate in isolation and records:

- evidence quality, project value, safety/reversibility, Termux feasibility, and operational simplicity (each 0–5);
- confidence (low/medium/high);
- strongest objection and disconfirming evidence sought;
- smallest next experiment that could change the assessment;
- recommendation and explicit unknowns.

These five Round 1 ratings are qualitative and are **excluded from the weighted score in §6**. They are not mapped one-to-one to the nine §6 dimensions: for example, project value has no corresponding §6 dimension. If a future analysis wants a weighted composite from Round 1 ratings, it must publish a separate mapping and weights before candidate scores are reviewed; do not retrospectively blend the two rubrics.\n\nReviewers should submit ratings before viewing other candidates' scores or the facilitator's ranking. A missing reviewer response is not a positive vote.

## 8. Evidence freeze

After Round 1, freeze and version:

- candidate source refs and file hashes;
- trial plans, fixtures, environment notes and budgets;
- all TLM receipts, test logs and failure records;
- rubric, weights, raw metrics and calculation method;
- reviewer ratings, rationales, confidence and objections.

Corrections create a new packet revision; never silently replace prior evidence. Check for incomparable environments and missing required evidence before any ranking.

## 9. Delphi Round 2 — cross-candidate synthesis

Share appropriately attributed or anonymized Round 1 distributions, rationales, strongest objections, dissent and evidence gaps. Each reviewer revises or reaffirms ratings and explains changes. Classify disagreements as empirical, methodological, or value/preference-based.

Run a targeted follow-up MVT only when its result could materially change the decision and the scope is authorized. Preserve earlier packets and scores. Record minority views and confidence; consensus is not required and must not be manufactured.

Each candidate receives one disposition:

- **Advance** — eligible and sufficiently supported for operator consideration.
- **Revise and retest** — a specific, fixable gap remains.
- **Defer for evidence** — a key uncertainty prevents a fair decision.
- **Reject** — fails requirements or is dominated without a justified context-specific benefit.
- **Blocked by safety gate** — a mandatory safety or authorization condition failed.

A single winner is optional. Different candidates may be best for different contexts. If evidence is incomparable, use the explicit **Inconclusive / design a better experiment** disposition rather than forcing a ranking.

## 10. Promotion and handoff

The panel recommends; the operator decides. Before implementation or promotion, require the repository's normal review gates, tests and platform-appropriate validation. The handoff must list ordered tasks, dependencies, owners, acceptance tests, rollback, evidence links and remaining unknowns. Never report a planned test as executed or a local test as a hosted check.

## 11. Current starting disposition

Based on the records currently linked from #1497 and PR #1514:

- **V0:** preserve as-found; eligible for comparison, not presumed correct.
- **Instruction audit:** in progress; see [INSTRUCTION-VALIDATION-MATRIX.md](INSTRUCTION-VALIDATION-MATRIX.md).
- **Known gaps:** reliable implementer completion, verifier contract coverage, native discovery/skill loading, nested delegation, boot/reboot delivery, whole-app recovery and full-workspace provisioning.
- **Next step:** complete source-level instruction extraction and confirm immutable current source SHAs before designing the first candidate-specific MVT.
- **No claim made here:** no device trial, model request, runtime mutation, or production provisioning was executed by this documentation change.
