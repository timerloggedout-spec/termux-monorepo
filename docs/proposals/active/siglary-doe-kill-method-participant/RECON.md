# Recon — Siglary / DoE / versioned kill-method participant

**As of:** 2026-11-16  
**Intake:** RFP #5514  
**Classification:** verified repository facts vs proposed integration

## 1. Verified canonical ownership

| Concern | Canonical owner | Contract / evidence |
|---|---|---|
| Siglary taxonomy, standard, enforcement design | Linguist | [SIGLARY-STANDARD.md](../notation-sets/SIGLARY-STANDARD.md), [Matrice](../../notation-sets/CAVEMAN-MICRO-DENSE-V2.md) |
| DoE family and campaign intake | DoE family | [DOE-FAMILY.md](../../../ops/DOE-FAMILY.md) |
| Experiment record | MVT surface; adopted by DoE family | [EXPERIMENT.schema.json](../../../../ops/corpus/EXPERIMENT.schema.json) |
| MVT / DoE / ATES separation | DoE expert lane | [MVT-DOE-ATES-SEPARATION.md](../../../../ops/MVT-DOE-ATES-SEPARATION.md) |
| Candidate capability / participant index | CEEL / Integration Intelligence | [capability graph](../../../integrations/capability-opportunity-graph.json), [graph schema](../../../../integrations/capability-opportunity-graph.schema.json) |
| Normalized integration event | Integration Intelligence | [integration event schema](../../../../integrations/schemas/integration-event.schema.json) |

**No new SSOT is proposed.** The opportunity graph is an index/projection, not a runtime authority. The experiment record remains one record per dispatched/executed run. Cross-surface references remain citations, not copied payloads.

## 2. Siglary constraints — verified

- Siglary is already repo-wide enforced; this implementation must conform rather than establish a competing notation.
- The A2A/machine register permits **OPERATORS + plain one-token words**. GLYPHS and CHORDS belong to the human display register.
- Existing dispatch stamp:

  `dispatch {from}→{to} · {task} · gate: {scope} · receipt {refs} · ∆ ask: {ask}`

- Existing reply stamp:

  `{live|degraded|down|blocked} {task} · verified receipt {PR/SHA/run} · owner action: {act ∨ none}`

- Principle ⑤ requires expansion when a compact form can be misread. A DO-statement extension requires Linguist review; this branch does not self-ratify syntax.
- `N∅` is chat-only. Data records use schema nulls.

## 3. DoE constraints — verified

- DoE means Design of Experiments and is a family; MVT is nested within DoE, and ATES is the execution harness.
- Every dispatched/executed run emits exactly one record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`.
- Configured-instance identity is more than model@version: provider, model@version, system prompt ref+SHA, tools ref+SHA, role, moniker, context, and instance_key.
- Campaign admission requires a committed design record and run evidence. A proposal alone is not an admitted experiment.
- Evaluation distinguishes execution status, task outcome, correctness, integration, regression, and resource cost.
- Promotion/culling is evidence-governed; new cherry-picked configurations become a new cohort/version, not a silent edit to an existing treatment.

## 4. Existing kill/stop-like mechanisms — distinct semantics

| Existing mechanism | Exact scope | What it proves | What it does not authorize |
|---|---|---|---|
| `QUEUE_PITCREW_ENABLED=false` | Feature flag for `scripts/ci/queue_pitcrew.py` | The script has a bounded opt-out; policy only selects superseded queued runs in an explicit allowlist and never touches `in_progress` | Global workflow cancellation or process termination |
| `scripts/temporal/kill_resume_harness.py` | Disposable worker in a self-host Temporal development-server test | SIGKILL fault injection, second-worker recovery, exactly-one receipt, unknown-outcome surfacing, history digest | Production worker/service/device termination |
| DoE cull | Experiment/population participant lifecycle | A participant is culled under a campaign rule; the gambling lane has a same-record wallet-to-pool consequence | Killing a process, cancelling a workflow, or disabling a feature flag |

These mechanisms must not be collapsed into one generic operation. The schema models the participant/method contract and exact target; policy owners retain authority.

## 5. Proposed relationship graph delta

Candidate node (not yet admitted or merged):

- `id: kill-method-participant`
- `kind: capability` or `internal_component` only after CEEL owner chooses the correct existing node class
- owner: existing policy/orchestration owner to be resolved in review; CEEL owns graph admission, not execution
- internal consumers: DoE family, ATES, existing queue policy, Temporal test harness
- evidence: RFP #5514 and the source files above
- lifecycle: `proposed` until owner review; no claim of runtime integration

Candidate edges: DoE family `informs` participant lifecycle; ATES `implements` test/fault-injection validation; policy gate `controls` method authority only if an allowed relationship is added to the graph vocabulary. Do not invent unsupported edge labels.

## 6. Gaps / decisions

1. **Owner of kill-method contract:** no single generic kill-method SSOT was found. Resolve whether policy/orchestration or CEEL owns the participant contract before canonical graph admission.
2. **Version compatibility:** existing capability graph is schema 1.0.0 with a closed node shape. Adding participant-version metadata requires a deliberate additive schema-version change and validator/test update; do not smuggle extra keys into 1.0.0.
3. **DO grammar:** existing A2A stamp is normative; any DO extension needs Linguist approval and conformance tests.
4. **Method families:** queue cancellation, worker fault injection, experiment culling, and feature-flag disable have different target/effect semantics and require separate method IDs/versions.
5. **Execution:** initial descriptor is non-executable. No runtime adapter, global switch, production target, or automatic termination.

## 7. Evidence references

- [RFP #5514](https://github.com/timerloggedout-spec/termux-monorepo/issues/5514)
- [Siglary standard](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/notation-sets/SIGLARY-STANDARD.md)
- [Siglary A2A skill](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/.agents/skills/siglary-a2a/SKILL.md)
- [DoE family](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DOE-FAMILY.md)
- [Experiment schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/corpus/EXPERIMENT.schema.json)
- [Queue pit crew](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/scripts/ci/queue_pitcrew.py)
- [Queue pit crew policy](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/ops/queue/pitcrew.json)
- [Temporal kill/resume harness](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/scripts/temporal/kill_resume_harness.py)
- [CEEL capability graph schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/integrations/capability-opportunity-graph.schema.json)
