# Telemetry Equation Registry and Verification Contract

**Status:** additive documentation proposal; existing ATES/WTCV reducer remains authoritative for implemented metrics  
**Verification date:** 2026-10-19  
**Principle:** equations are versioned contracts. A calculator result is a verification aid, not proof that production telemetry was collected correctly.

## Purpose

This registry makes telemetry formulas reviewable across GitHub Actions, SHE, platform201, n8n, Temporal, and optional research adapters. Every formula needs a definition, units, preconditions, missing-data policy, implementation reference, and reproducible fixture before it can influence longitudinal decisions.

- **Canonical evidence:** sanitized repository-native JSONL and receipts, correlated to run/attempt/SHA where available.
- **Computation:** pure reducers with deterministic tests.
- **Independent check:** Wolfram reference calculations and hand-checkable fixtures.
- **Visualization:** Equation.io for interactive exploration; The [canonical Mermaid source](TELEMETRY-EQUATION-PIPELINE.mmd) remains source-controlled outside the auto-render folder; the interactive view is rendered with Mermaid Chart.
- **Promotion:** human review and normal repository gates. No equation score independently authorizes a merge or deployment.

## Existing implemented equations

The authoritative implementation is [she/metrics/agent_throughput.py](../../she/metrics/agent_throughput.py), with regression coverage in [tests/test_she_agent_throughput.py](../../tests/test_she_agent_throughput.py) and event constraints in [AGENT-THROUGHPUT-EVENT.schema.json](AGENT-THROUGHPUT-EVENT.schema.json).

| ID | Formula | Unit / interpretation | Preconditions and missing-data rule |
|---|---|---|---|
| EQ-C-STRUCT-v1 | C = ln(1 + A + D) × sqrt(F) | Structural change proxy; dimensionless heuristic | A, D, F ≥ 0; all three structural values required. This is a proxy, not semantic complexity. |
| EQ-TCV-v1 | TCV = completed tasks / workflow minutes | completed tasks/minute | Workflow duration must be positive; otherwise current reducer returns 0. |
| EQ-WTCV-v1 | WTCV = sum(complexity scores) / workflow minutes | complexity-weighted units/minute | Every completed task must have valid complexity; otherwise null. |
| EQ-RPI-v1 | RPI = (failed tool calls + retry events) / (tool calls + retry events) | retry/failure overhead ratio | Failed/error tool-call events and retry events are counted separately. No actions gives 0 in the current reducer. |
| EQ-PY-v1 | PY = sequential baseline seconds / (agent count × workflow seconds) | baseline-normalized parallel yield | Requires declared sequential baseline, identified agents, and positive wall time; otherwise null. Do not silently clamp values; values above 1 should trigger cohort/baseline review. |
| EQ-TPV-v1 | TPV = (input tokens + output tokens) / inference seconds | tokens/second of inference time | Requires positive inference seconds; otherwise null. Not end-to-end latency. |
| EQ-CIE-v1 | CIE = output tokens / input tokens | output/input token ratio | Requires positive input tokens; otherwise null. Not a quality score. |
| EQ-ATES-v1 | ATES = WTCV × max(0, 1 − RPI) × PY | composite throughput observation | Requires WTCV and parallel-yield evidence; otherwise null. Never use as a standalone quality or merge gate. |

The structural fallback is implemented with math.log1p(additions + deletions) * math.sqrt(files_changed). Invalid or absent complexity stays unavailable; the reducer does not invent a complexity of 1.0.

### Formula interpretation safeguards

1. TCV and WTCV are comparable only across defined cohorts and compatible time windows.
2. Parallel yield depends on a **declared** sequential baseline. A baseline from a different task mix is not valid evidence.
3. RPI is operational overhead, not a direct probability of failure. Failed calls and retries are event counts, not necessarily independent incidents.
4. ATES is diagnostic throughput. Validation quality, accepted outcome, attribution confidence, human intervention, cost, and promotion state remain separate dimensions.
5. Null is meaningful. Dashboards must distinguish missing evidence from a measured zero.

## New candidate equations

These formulas now have pure helper implementations and regression tests in the existing reducer module. They are **not yet emitted by the runtime schema or projected into SHE**. Before production adoption, add versioned aggregate inputs, wire the helpers into a reducer/projection, and validate the resulting cohort evidence.

| ID | Candidate formula | Why it helps | Required guard |
|---|---|---|---|
| EQ-ECR-v1 — Evidence Coverage Ratio | ECR = valid required observations / expected required observations (pure helper implemented) | Quantifies whether a cohort contains the evidence it was supposed to produce. | Expected fields and schema version must be declared. Return null when denominator is unknown or zero. |
| EQ-VOR-v1 — Validated Outcome Rate | VOR = explicit validation passes / tasks with explicit validation outcome (pure helper implemented) | Separates completed work from work explicitly validated. | Return null with no evaluated tasks; show validation coverage alongside VOR so unevaluated tasks are not hidden. |
| EQ-VCOV-v1 — Validation Coverage | VCOV = tasks with explicit validation outcome / completed tasks (pure helper implemented) | Exposes the share of completed work whose correctness was actually assessed. | Return null when no completed tasks exist. Missing outcomes are not failures or passes. |
| EQ-CORR-v1 — Correlation Completeness | CORR = eligible records with required provenance / eligible records (pure helper implemented) | Measures ability to connect observations to run, attempt, SHA, cohort, and event identity. | Define eligibility and required identity fields per event class; return null if expected population is unknown. |

**Do not combine these candidates into a new scalar score yet.** Display coverage and outcomes separately first. Any future composite must specify normalization, weights, uncertainty, version, and sensitivity tests.

## Retry semantics and uncertainty-aware outcomes

Additional helpers were added for analysis and are deliberately **not runtime-emitted** until a versioned logical-operation identity and terminal-state contract is adopted.

| ID | Formula | Interpretation | Preconditions / guard |
|---|---|---|---|
| EQ-RAMP-v1 — Retry Amplification | RAMP = total attempts / logical operations | Average attempts per logical operation. 1.0 means one attempt per operation; 1.3 means 1.3 attempts per operation. It is not a failure probability. | Count attempts and logical operations at separate identity levels; require attempts ≥ logical operations and a positive known denominator. |
| EQ-RREC-v1 — Retry Recovery Rate | RREC = retried logical operations that eventually succeeded / logical operations with at least one retry | Conditional recovery among operations that needed retry. | Numerator and denominator count logical operations, not attempts. Include only retried operations with known terminal outcomes in the denominator; publish sample size. |
| STAT-WILSON-v1 — Wilson interval | (p=x/n), (d=1+z^2/n), (c=(p+z^2/(2n))/d), (h=z\sqrt{p(1-p)/n+z^2/(4n^2)}/d), interval = [max(0,c−h), min(1,c+h)] | Uncertainty interval for a binomial proportion; default (z≈1.96) gives an approximate 95% interval. | Requires integer counts (0≤x≤n), (n>0), and independent Bernoulli trials. Return null when counts or denominator are unavailable. Clustered workflow events require a cluster-aware method. |

### Operational interpretation from primary documentation

- OpenTelemetry's error-recording guidance says errors that were retried or handled so an operation completes gracefully should not be recorded as errors on spans or metrics describing that logical operation. Preserve attempt-level failures/retries separately from the terminal outcome: [Recording errors](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/).
- Temporal distinguishes an Activity Execution from its Activity Task Executions; individual task executions represent attempts/retries. Keep workflow/activity logical identity separate from attempt identity: [Detecting Activity failures](https://docs.temporal.io/encyclopedia/detecting-activity-failures) and [Retry policies](https://docs.temporal.io/encyclopedia/retry-policies).
- n8n provides explicit error-workflow control paths. The adapter must preserve source execution IDs and terminal status rather than assuming n8n retry behavior is equivalent to Temporal: [n8n error handling](https://docs.n8n.io/build/flow-logic/handle-errors-gracefully/).
- OpenTelemetry's metrics data model and CI/CD conventions are interoperability references, not a mandate to encode every repository-specific diagnostic as a standard semantic convention: [Metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/) and [CI/CD metrics](https://opentelemetry.io/docs/specs/semconv/cicd/cicd-metrics/).

### Aggregation rules

1. Keep **attempt events**, **logical-operation terminal outcomes**, and **validation outcomes** as distinct populations. A retry attempt is not a second completed logical task.
2. Pair every rate with its numerator, denominator, eligible-population definition, and terminal-state policy. A rate without denominator counts is not auditable.
3. Missing, pending, and unknown outcomes are not failures or successes. Exclude unresolved outcomes only under an explicitly versioned eligibility policy; expose their count separately.
4. Do not average precomputed p50/p95/p99 values across workers or time windows. Merge compatible histogram buckets or aggregate raw observations, then calculate the percentile.
5. A Wilson interval assumes independent Bernoulli trials. If events are clustered within workflows, agents, repositories, or repeated CI runs, the naive interval can be too narrow; use a cluster-aware method or report descriptive counts only.
6. Compare rates across compatible cohorts and time windows. Stratify by task class/provider/workflow when mix changes; otherwise Simpson's paradox can make an aggregate trend misleading.
7. The helper implementations and fixtures are useful now, but no new candidate metric is wired into the runtime event schema or SHE projection. Integration requires versioned IDs for logical operations and attempts, explicit terminal states, tests for duplicate/out-of-order events, and a replay-safe reducer migration.

## Wolfram reference checks

Wolfram Language evaluation was used as an independent arithmetic check for these fixtures. Values are illustrative test inputs, not live production measurements.

| Check | Input | Wolfram result |
|---|---|---:|
| Structural complexity | additions=9, deletions=1, files_changed=1 | ln(11) ≈ 2.3978952728 |
| Structural complexity, four files | additions=9, deletions=1, files_changed=4 | 2 ln(11) ≈ 4.7957905456 |
| ATES arithmetic | WTCV=18, RPI=2/3, parallel yield=1 | 18(1 − 2/3)(1) = 6 |
| Evidence coverage example | 4 valid / 5 expected observations | 0.8 |
| Validation rate example | 3 explicit passes / 4 explicit outcomes | 0.75 |

These checks validate arithmetic and intended formula behavior. They do **not** by themselves validate production event completeness, attribution, cohort equivalence, or reducer integration. The Python reducer and fixtures remain the implementation-level authority.

## Interactive equation view

Equation.io parser-validated reference view of the structural complexity formula (a=additions, k=deletions, n=files changed):

[Open the interactive structural-complexity equation](https://equation.io/g/a%20%3D%2010;k%20%3D%202;n%20%3D%203;score%20%3D%20ln%281%20%2B%20a%20%2B%20k%29%20%2A%20sqrt%28n%29;view%28x%20%3D%20-2..30%2C%20y%20%3D%200..12%29)

The tool parser rejected an initial draft that used d as a variable because Equation.io reserves it for derivative syntax. The final graph uses k for deletions; every row validated successfully. This demonstrates why parser validation belongs before publishing equation examples.

## Orchestration and aggregation boundaries

- **GitHub Actions:** canonical source for repository checks, run IDs, attempts, commit SHAs, and immutable evidence artifacts.
- **platform201 and n8n:** integration/automation adapters. They may trigger work or forward events, but should not silently redefine canonical metric semantics.
- **Temporal:** candidate durable orchestration for long-running and retryable workflows. Record workflow/run identity and retry history; distinguish a retry from a new logical task.
- **SHE / historical corpus:** correlate sanitized observations and project metrics. Preserve raw event facts separately from derived, versioned scores.
- **OpenTelemetry:** interoperability boundary for spans, metrics, and events. Map stable attributes and units; do not export prompts, completions, credentials, arbitrary tool payloads, or secrets.
- **Wolfram:** independent formula calculation and fixture generation.
- **Equation.io:** interactive exploration, not a production computation dependency.
- **Mermaid Chart:** rendered view of the source-controlled .mmd architecture.
- **SVG Diagram:** generated context illustration for collaboration/review; source documentation and Mermaid remain version-controlled.
- **Vectorize:** suitable for approved raster logos/icons that need editable SVG variants. It is not a telemetry reducer or a general-purpose math/diagram validator; use it only when an approved source asset is identified.

The n8n and Temporal roles are supported by official documentation on [n8n error handling](https://docs.n8n.io/build/flow-logic/handle-errors-gracefully/), [Temporal workflow execution](https://docs.temporal.io/workflow-execution), and [Temporal retry policies](https://docs.temporal.io/encyclopedia/retry-policies). OpenTelemetry conventions define stable span/metric/event attributes and units; see the [semantic conventions](https://opentelemetry.io/docs/specs/semconv/).

## NerdCalci reference integration

The [NerdCalci fork](https://github.com/timerloggedout-spec/NerdCalci_fork) is a **reference input**, not a runtime dependency to embed in the Python telemetry pipeline. Its README and [reference guide](https://github.com/timerloggedout-spec/NerdCalci_fork/blob/main/REFERENCE.md) describe an offline-first, variable-aware calculation notebook with expression syntax, named calculations, unit conversion, date/time arithmetic, user-defined functions, and file-based sessions.

Useful ideas to adapt without copying the Android implementation:

- named, human-readable calculation variables and comments;
- reusable formula definitions with explicit inputs;
- clear parse/validation errors and worked examples;
- portable, offline-friendly reference fixtures;
- exportable calculation records that preserve formula version and input provenance.

The existing repository is Python/JSONL/GitHub Actions oriented. Kotlin/Compose, Room, and the Android calculator UI should not become dependencies of the telemetry reducer. If a shared equation DSL is proposed later, first define its grammar, numeric precision, units, null semantics, licensing boundary, and conformance fixtures.

## Source-of-truth and change workflow

1. Edit the registry and implementation/test contract together.
2. Run focused Python tests and JSON schema validation.
3. Recalculate reference fixtures in Wolfram and record exact inputs/outputs.
4. Validate interactive graph syntax in Equation.io when a graph is included.
5. Update the canonical Mermaid source and review its Mermaid Chart rendering; preserve existing auto-render folder contracts and never replace canonical source files with rendered outputs.
6. Review provenance, privacy, missing-data behavior, and cohort compatibility.
7. Observe actual CI, re-fetch the final SHA, compare evidence, and record COMMITTED, EXECUTED, VALIDATED, and PROMOTED independently.

## References

- Repository reducer: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/she/metrics/agent_throughput.py
- Existing metric contract: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-THROUGHPUT-METRICS.md
- Existing event schema: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-THROUGHPUT-EVENT.schema.json
- Existing priority decision: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md
- Integration graph matrix: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/INTEGRATION-GRAPH-MATRIX.md
- NerdCalci fork: https://github.com/timerloggedout-spec/NerdCalci_fork
- Wolfram large-system engineering guidance: https://reference.wolfram.com/language/tutorial/BuildingLargeSoftwareSystemsInTheWolframLanguage
- OpenTelemetry semantic conventions: https://opentelemetry.io/docs/specs/semconv/
- n8n error handling: https://docs.n8n.io/build/flow-logic/handle-errors-gracefully/
- Temporal workflow execution: https://docs.temporal.io/workflow-execution
- Temporal retry policies: https://docs.temporal.io/encyclopedia/retry-policies
- Temporal Activity failure/attempt semantics: https://docs.temporal.io/encyclopedia/detecting-activity-failures
- OpenTelemetry error-recording guidance: https://opentelemetry.io/docs/specs/semconv/general/recording-errors/
- OpenTelemetry metrics data model: https://opentelemetry.io/docs/specs/otel/metrics/data-model/
- OpenTelemetry CI/CD metric conventions: https://opentelemetry.io/docs/specs/semconv/cicd/cicd-metrics/
