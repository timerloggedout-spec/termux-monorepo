# Agent Evidence Substrate — BIUDL 2026-09-27

## Status

- **Intent:** consolidate the agent-observability, reproducibility, provenance, MCP, complexity, and manager-evaluation lanes without collapsing their implementations.
- **Canonical evidence:** repository-owned JSONL/receipt artifacts + immutable Git SHA/run linkage.
- **Interoperability boundary:** OpenTelemetry-compatible events.
- **Environment substrate:** Docker for reproducible CI/research execution; Codespaces for interactive reproduction.
- **Promotion authority:** repository correctness gates and explicit operator promotion. Observability metrics remain observational.
- **Design rule:** do not infer success from queued/in-progress state, dashboard state, model identity, or price.

## Current-state correction

PR #523 is historical context, not the current execution surface. The current master stream is active and includes repeated observer/status refreshes plus continuous-evaluation boundary work. Future documentation MUST re-fetch the live branch/commit before describing #523 as open, mergeable, or pending promotion.

The project therefore treats historical PR state and current master state as separate evidence epochs.

## Canonical operating loop

```text
RECON
  ↓
PLAN / MEASURE
  ↓
IMPLEMENT / ACT
  ↓
COMMIT
  ↓
WAIT
  ↓
WATCH
  ↓
VALIDATE
  ↓
RE-FETCH
  ↓
COMPARE Δ
  ↓
CLASSIFY
  ↓
RECORD
  ↓
REPEAT
```

Terminal state claims require evidence from the actual execution boundary. A cancelled, skipped, queued, or superseded execution is retained with its observed state; it is never rewritten as success.

## Evidence layers

### L0 — immutable identity

Every observation SHOULD carry:

- repository full name
- ref
- commit SHA
- workflow/run/attempt when applicable
- event timestamp
- producer identity
- schema/contract version

### L1 — lifecycle evidence

Record:

- requested / queued / in-progress / completed
- job and step states
- conclusion
- duration
- artifact identifiers
- artifact digest where available

### L2 — action → effect

Record:

- action ID
- effect ID
- parent/causal reference when known
- realization status
- validation outcome
- attribution confidence

### L3 — agent quality

Existing metrics remain observational:

- TCV
- WTCV
- RPI
- action density
- parallel yield
- ATES
- TPV
- CIE
- tool delay
- handoff latency
- explicit complexity
- structural complexity

Missing evidence remains `null`, not zero.

### L4 — provenance graph

Connect:

```text
human / agent
    ↓
task / issue / PR
    ↓
workflow / session
    ↓
tool / model / provider
    ↓
code + data + environment
    ↓
artifact / result
    ↓
validation / acceptance
```

The graph must preserve uncertainty. Identity attribution is evidence-weighted, not inferred solely from the GitHub account that authored a commit or comment.

## P0 foundation

| Lane | Role | Decision |
|---|---|---|
| OpenTelemetry | neutral telemetry/interoperability boundary | **P0** |
| Canonical JSONL + receipts | repository-owned evidence source | **P0** |
| ATES / Action→Effect | execution measurement | **P0** |
| Complexity contract | normalized task/code difficulty features | **P0** |
| Docker | reproducible execution substrate | **P0** |
| Provenance identity | SHA/run/artifact/environment linkage | **P0** |

Docker is an execution substrate, not an evidence authority. OpenTelemetry is an interoperability layer, not a hosted-system dependency.

## P1 measurement/providers

| Provider | Contribution | Boundary |
|---|---|---|
| Tree-sitter | language-neutral structural features | complexity provider |
| Lizard | broad-language NLOC/CCN/token/parameter metrics | complexity provider |
| Radon | Python CCN/Halstead/maintainability | Python provider |
| Langfuse | datasets/traces/experiments/scores | optional adapter |
| Phoenix | open tracing/evaluation/datasets/experiments | optional adapter |
| Codespaces | interactive reproduction | environment surface |
| MCP/TDQS | tool-definition quality | tool-context evaluator |

Providers consume the canonical cohort/event contract. They do not become the source of truth.

## P2 research

- MASEval-class multi-agent benchmark suites
- manager-policy tournaments
- orchestration-policy replay
- advanced accelerator/energy studies
- vendor-specific persistence and UX

A benchmark result is evidence about the tested cohort and protocol, not a universal model-quality claim.

## Complexity contract

Preserve raw features before deriving scores:

```text
C_explicit
C_structural
C_ast
C_ccn_multilang
C_python
        ↓
derived complexity
        ↓
complexity-adjusted 3L0
```

Each provider result MUST retain:

- provider
- provider version
- raw feature values
- derived value
- confidence
- source SHA
- analysis timestamp

The base structural fallback remains:

```text
ln(1 + additions + deletions) × sqrt(files_changed)
```

Provider disagreement is retained as evidence rather than silently averaged away.

## MCP and agent-interoperability security boundary

MCP compatibility does not imply trust.

Admission records SHOULD include:

- server identity
- server/version provenance
- tool schema hash
- declared capability/scope
- authorization mode
- delegation depth when applicable
- policy decision
- request/response evidence hashes
- parent agent-turn ID

Secrets MUST remain outside source, telemetry, and artifacts.

A future single-writer lease must be an enforcement gate, not merely a label or coordination comment.

Cross-platform synchronization identity is:

```text
GitHub master SHA
       ↕
GitLab master SHA
       ↓
synchronization state
       ↓
review ownership / reconciliation
```

A feature-branch SHA versus GitLab master is not by itself evidence of a synchronization conflict.

## Reproducibility contract

For each bounded experiment, capture:

- repository SHA
- environment/image digest
- OS/architecture
- runtime versions
- dependency lock state
- model/runtime/backend versions
- input dataset/cohort identifier
- configuration hash
- tool versions
- network/dependency availability
- result/artifact hashes

Docker provides the reproducible CI substrate. Codespaces provides interactive reproduction. Their purposes are related but not interchangeable.

## Manager tournament contract

Do not optimize isolated model leaderboard scores.

Compare orchestration policies over the same task cohorts and evidence contract:

```text
manager A
manager B
manager C
manager D
   ↓
same cohort
   ↓
same acceptance/evaluation
   ↓
same evidence schema
   ↓
integrated outcome
```

Measure:

- final acceptance
- correctness/validation outcomes
- time-to-integration
- useful versus duplicate actions/tokens
- feedback cycles
- retries
- conflicts
- human intervention
- provider/model failures
- attribution confidence
- realization ratio
- complexity-adjusted metrics
- variance across repetitions

The Moneyball objective is integrated outcome per total operational cost, not zero-dollar usage alone.

## Edge / ARM / Android extension

Local inference experiments SHOULD record:

- device and ABI
- CPU/GPU/NPU backend
- model hash
- quantization
- runtime version
- tokens/sec
- latency p50/p95
- peak memory
- thermal state
- energy proxy
- fallback path

Prefer portable, inspectable FOSS runtimes and preserve a CPU fallback so accelerator-specific experiments do not become architecture dependencies.

## Supply-chain / provenance extension

The evidence graph should eventually join:

```text
SBOM / AIBOM
   +
build provenance
   +
runtime tool use
   +
environment fingerprint
   +
artifact digest
   ↓
execution provenance graph
```

Standards-first exchange is preferred. Vendor persistence remains an adapter.

## Procurement decision fields

Every candidate/tool/runtime record SHOULD support:

- license
- canonical source
- maintenance/activity
- portability: ARM/Linux/Android/Termux
- offline capability
- interoperability
- reproducibility
- provenance
- dependency risk
- lock-in risk
- security surface
- resource cost
- operational fit
- horizon
- confidence
- evidence status
- decision status
- last verified date
- version/commit

## Promotion gates

### Gate 1 — instrument

Canonical event schema, watcher, SHA/run linkage.

### Gate 2 — validate

Correctness checks and evidence integrity pass.

### Gate 3 — reproduce

Same bounded cohort can be replayed from a pinned environment.

### Gate 4 — compare

At least two providers/policies can consume the same evidence contract.

### Gate 5 — promote

Explicit operator/policy decision; no implicit merge or promotion.

## Non-goals

- no speed-only merge gate
- no ATES-only merge gate
- no TDQS-only merge gate
- no vendor as canonical evidence source
- no synthetic zeros for missing telemetry
- no attribution from actor identity alone
- no benchmark score treated as universal quality
- no secret material in telemetry/artifacts
- no automatic rerun merely to improve dashboard appearance
- no promotion inferred from queued/in-progress status
