# Agent Throughput & Quality Metrics

**Status:** adopted observational measurement contract  
**Principle:** **quality > time**. Throughput is a diagnostic dimension, never a merge-quality proxy by itself.

## Purpose

SHE already reconstructs durable GitHub Actions timing from run/job timestamps. This lane extends that reducer model to multi-agent execution telemetry without introducing a hosted observability dependency.

ATES is **not a future/fancy add-on**: Phase A has already landed as a pure reducer and test contract. The remaining phases add evidence emission, longitudinal correlation, provider experiments, and manager-level use around that foundation.

The design accepts Gemini's ATES concepts, but makes three corrections:

1. **Weighted work, not raw task count.** `WTCV` replaces raw TCV as the primary throughput measure when task complexity is available.
2. **No speed-only merge gate.** A fast, low-quality agent must not outrank a slower validated agent. ATES is an observation, not a CI threshold.
3. **Missing evidence stays missing.** No sequential baseline, token telemetry, inference timing, or task complexity means the corresponding metric is `null`, not a fabricated zero or unit score.

## Event contract

Agents should emit JSONL events conforming to `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`.

Useful event classes:

- `task_started`
- `task_completed`
- `tool_call`
- `tool_retry`
- `handoff`
- `active_window`

Optional fields include `tokens_in`, `tokens_out`, `inference_seconds`, `duration_ms`, `latency_ms`, and `complexity_score`. A completed task may also carry structural features under `metrics` (`additions`, `deletions`, `files_changed`) for the implemented fallback.

### Privacy boundary

Execution telemetry is metadata-first. Do not emit prompts, completions, credentials, tool payloads, repository secrets, or arbitrary message bodies. If provenance needs a text fingerprint, export a hash rather than the text.

## Metrics

| Metric | Definition | Interpretation |
|---|---|---|
| TCV | completed tasks / workflow minutes | Raw task velocity; useful only when task difficulty is comparable. |
| WTCV | sum(complexity scores) / workflow minutes | Preferred throughput signal when complexity is known for every completed task. |
| TPV | (input + output tokens) / inference seconds | Model inference throughput; not total system latency. |
| Handoff latency | agent-B start − agent-A emit | Queue/context/state-transfer overhead. |
| Action density | actions / active seconds | External interaction intensity. |
| Parallel yield | sequential baseline / (agents × wall time) | Efficiency of parallel execution relative to a declared baseline. |
| RPI | (failed actions + retries) / total actions | Retry/error overhead. |
| Tool delay | mean non-LLM tool duration | Infrastructure/I/O latency. |
| CIE | output tokens / input tokens | Context/completion efficiency; only meaningful with token telemetry. |
| ATES | WTCV × (1 − RPI) × parallel yield | Composite throughput observation, not a quality score. |

## Complexity

Complexity may be supplied by the agent or derived from repository evidence. The Phase A reducer now supports both explicit `complexity_score` and the documented structural fallback:

`C = ln(1 + additions + deletions) × sqrt(files_changed)`

If a completed task has no complexity evidence, WTCV and ATES remain `null` for that reduction rather than silently treating the task as complexity 1.0.

Tree-sitter, Lizard, Radon, or language-specific AST reducers may be evaluated later as separate measurement providers. They must be benchmarked against labeled fixtures before their values are allowed to affect longitudinal comparisons.

This avoids rewarding verbosity: raw line churn is logarithmic, and documentation-only churn should not be presented as equivalent to semantic work.

## Quality coupling

SHE should display throughput beside evidence quality dimensions:

- validation result;
- tests/checks;
- realization ratio / action-effect delta;
- attribution confidence;
- human intervention;
- conflict/retry class;
- promotion state (`COMMITTED`, `EXECUTED`, `VALIDATED`, `PROMOTED`).

Do **not** add a `MIN_ATES_THRESHOLD` merge gate. A threshold would optimize the proxy and could incentivize agents to split work, inflate action counts, or trade correctness for speed.

## Quality lane

`.github/workflows/agent-quality-lane.yml` is a dedicated check for the telemetry contract. It verifies:

1. source/documentation presence and linkage;
2. module/public-symbol documentation for the reducer;
3. explanatory comments around non-obvious measurement formulas;
4. the no-speed-gate invariant;
5. JSON schema validity;
6. focused reducer tests, including missing-evidence and structural-complexity cases.

The lane is intentionally not a comment-density score. The goal is auditable explanation of non-obvious logic, not decorative comments.

## PR review layering

Phase A does **not** replace the repository's normal review. Instead, after Phase A is present, the same PR/review process is evaluated through an additional evidence layer:

`PR review → validation/checks → Action→Effect → ATES/WTCV observation → longitudinal record`

The ATES layer can explain whether an orchestration policy was efficient **after** the PR has evidence of correctness. It cannot convert an unvalidated change into a good result. When later telemetry emission is live, the review cycle should be re-run over comparable cohorts so the ATES observation can be attached to actual run/attempt/SHA evidence.

## Candidate observability backends

| Backend | Decision | Reason |
|---|---|---|
| GitHub Actions JSONL | **Primary** | Free-scope, repository-native, durable enough when artifacts/corpus are retained. |
| Langfuse | **Optional experiment adapter** | Rich traces/tokens/tool spans, but adds an external service and secret/egress boundary. |
| Arize Phoenix | **Optional parallel experiment adapter** | Strong local tracing/evaluation option; compare against Langfuse rather than coupling SHE to either. |
| Hex | **Optional analytical consumer** | Current connector is plan-blocked; contract remains useful and can consume sanitized evidence later. |

The repository should measure the adapters against the same event schema, then retain only the fields that improve evidence quality enough to justify their operational cost.

## Implementation surfaces

- Phase A reducer: `she/metrics/agent_throughput.py`
- Phase A tests: `tests/test_she_agent_throughput.py`
- Phase A quality gate: `.github/workflows/agent-quality-lane.yml` + `scripts/ci/verify_agent_quality.py`
- Hex-compatible sanitizer: `scripts/hex_moneyball_export.py`
- Actions timing reducer: `she/metrics/job_timestamps.py`
- Longitudinal corpus: `workspace/llm_map/context_relationships/`
- SHE projection contract: `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`

## Phase model

### Phase A — measurement primitives **[IMPLEMENTED]**

Land schema + pure reducer + fixtures + quality verification. No external telemetry dependency. This is the ATES foundation already present on the active integration branch.

### Phase B — evidence emission **[NEXT]**

Teach eligible agent workflows to emit sanitized JSONL and publish a receipt alongside existing Action artifacts. Every event must retain run/attempt/SHA linkage where available.

### Phase C — longitudinal correlation

Join execution events to GitHub run attempts, SHAs, PRs, Action→Effect events, and corpus observations.

### Phase D — multi-provider experiment

Run equivalent telemetry through Langfuse and Phoenix adapters. Compare completeness, latency, cost, privacy surface, and decision quality on the same bounded cohorts.

### Phase E — manager evolution

Use validated outcome/evidence dimensions to compare orchestration policies. Throughput is one factor in the manager score, never the sole objective.

## Acceptance invariants

- Every reported metric has a source event/baseline or is `null`.
- No raw prompt/completion/tool payload reaches the evidence plane.
- ATES never blocks a merge by itself.
- Complexity providers are versioned before longitudinal comparison.
- Workflow duration is sourced from Actions timestamps, not deprecated timing endpoints.
- All observations remain traceable to run attempt + SHA where available.
- Quality verification is itself a visible Actions check.
