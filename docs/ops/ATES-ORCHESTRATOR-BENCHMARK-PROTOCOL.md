# ATES Orchestrator Benchmark Protocol

Status: implementation contract
Scope: RECON-style memory/routing evaluation, PerspectiveGap-style boundary preservation, deterministic execution gates, DAG/actor-critic isolation, and DoE/MVT manager experiments.

ATES remains the measurement spine. This protocol is a benchmark/evaluation layer under ATES, not a replacement for correctness checks.

Processing path:
orchestrator -> bounded benchmark -> deterministic gates -> trace/span evidence -> ATES reduction -> custom historical parser + optional MLflow adapter -> DSPy DoE/MVT -> manager comparison.

RECON rules:
- Every case that can be uncertain must expose an explicit abstain option.
- A wrong committed route receives the declared negative penalty; the default is 0.2.
- The scorer never rewards hallucinated certainty.

PerspectiveGap rules:
- Every required fragment must reach the correct downstream role.
- Declared distractors must not cross role boundaries.
- Missing or cross-role fragments are automatic failures.
- Boundary matching is all-or-nothing, not fuzzy.

Execution rules:
- Deterministic checks run first: exit code, assertions, observable state change, and optional DFA/state transition checks.
- A deterministic failure fails the case immediately.
- A qualitative judge is permitted only when deterministic evidence is explicitly inconclusive.
- Judge weight is capped at 0.30 and can never rescue a deterministic failure.

DAG and actor/critic rules:
- Pre-session child branches declare SPAWN mode.
- SPAWN mode must not inherit parent context.
- Sibling context is not inherited evidence.
- Actor and critic have separate context fingerprints.
- Critic-private tests and hidden labels are never visible to the actor.

DoE/MVT:
- MVT is the smallest frozen cohort covering abstention, wrong commit, fragment preservation, distractor isolation, execution gating, SPAWN isolation, and actor/critic isolation.
- DoE varies declared factors while task contract, environment fingerprint, benchmark version, and deterministic scorer stay fixed.
- Recommended first factors: routing single/delegated; actor-critic off/on; abstention required; spawn isolated; judge off/inconclusive-only.

Trace model:
- One trace_id identifies a benchmark run.
- Spans identify orchestrator decisions, retrieval, child spawn, tool calls, actor, critic, validator, and ATES reduction.
- Async hops preserve trace_id and use distinct span ids.
- The canonical trace envelope is docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json.

Dual processing:
- ATES performs local deterministic reduction, complexity normalization, throughput/effectiveness correlation, and historical backfill.
- The optional MLflow adapter converts the same sanitized evidence into evaluation rows and run metadata.
- JSONL evidence remains canonical; neither backend becomes the source of truth.

DSPy:
- DSPy is an optimization instrument for DoE/MVT arms, not the production router.
- DSPy consumes frozen benchmark contracts and emits signatures, factor values, and measured outcomes.
- Optimizer artifacts remain proposal artifacts until the existing dual-gate promotion path passes.
- No silent routing-weight mutation is permitted.

Acceptance invariants:
- deterministic failure short-circuits judging;
- judge weight never exceeds 0.30;
- required fragments are all-or-nothing;
- distractor leakage is always a failure;
- wrong commits apply the declared negative penalty;
- SPAWN mode never inherits parent context;
- missing evidence remains null;
- ATES never becomes a merge-quality gate;
- raw prompts, completions, secrets, private fixtures, and arbitrary tool payloads never enter canonical telemetry.