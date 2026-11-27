# DoE / MVT Plan — Observability and Agent Workflows

## 1. Objective

Compare orchestration policies, telemetry backends, and evaluation providers on matched tasks. Optimize validated task outcome and evidence quality under an explicit operational-cost envelope.

## 2. Experimental identity

Workflow identity: workflow_run_id, run_attempt, repository, ref, commit_sha, lane, ssot_path, task_id, experiment_id, variant_set, environment_fingerprint.

Request identity: request_id, trace_id, experiment_id, variant_id, assignment_source, assignment_version, provider_id, model_id, endpoint_id, latency_ms, input_tokens, output_tokens, cost_observed, retry_count, outcome.

Propagate workflow identity to every request and tool invocation. Record assignment decider and policy version. Keep raw IDs in traces/events rather than high-cardinality metric labels.

## 3. Factor design

| Factor | Example levels | Control |
|---|---|---|
| Manager policy | baseline, research-led, pipeline-led, hybrid | Same task cohort |
| Research method | My-Jogyo sequence, Docxology staged pipeline, repository baseline | Same acceptance contract |
| Operational backend | SigNoz, HyperDX, OpenObserve, Coralogix | Same sanitized events |
| AI evaluation | Langfuse, Phoenix, repository-native evaluator | Same dataset and rubric |
| Profiling | Parca, Pyroscope, disabled baseline | Same workload/environment |
| Provider/model | selected eligible providers/endpoints | Exact model and endpoint |
| Environment | pinned container, declared runner, Termux when supported | Fingerprinted runtime |

Run one-factor screening first; use bounded factorial/fractional-factorial designs when interactions matter. Pre-register factors, levels, cohort, exclusions, stopping rule, primary outcome, and analysis.

## 4. Cohort and repetitions

Use tasks with explicit contracts, acceptance tests, and comparable complexity. Stratify by task class and complexity band. Match environment, dependency state, input data, and time window where practical. Randomize assignment within each stratum. Determine sample count from pilot variance and the minimum effect worth detecting. Preserve failed, cancelled, timed-out, and partial observations. Use paired comparisons where safe.

## 5. Outcomes

Primary: accepted task completion; correctness and validation pass rate; evidence completeness and attribution confidence; Action→Effect realization.

Secondary: time-to-integration; useful vs duplicate actions/tokens; retries, conflicts, human intervention; provider/model failures; p50/p95 latency and throughput; observed cost/resource use; CPU/memory profile; variance and reproducibility.

Guardrails: correctness dominates speed; missing evidence stays null; provider score scales remain separate until calibrated; causal claims require controlled design; results remain scoped to the tested cohort/environment.

## 6. Analysis and promotion

Report per-variant counts, medians, dispersion, confidence intervals, missingness, and failure categories. Use paired differences for matched tasks. Inspect interactions before attribution. Retain raw observations and analysis code.

Promote only when validated outcomes or decision/evidence quality improve at acceptable cost, repeated runs reproduce the effect, exportability/privacy hold, and repository dual-gate passes.
