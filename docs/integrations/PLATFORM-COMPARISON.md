# Platform comparison — Langfuse × PromptLayer × PostHog × Braintrust

**Purpose:** fair participant selection for CEEL and the DoE family.  
**Status:** candidate comparison design; no platform is declared connected, deployed, validated or selected.

## 1. Candidate matrix

| Candidate | Proposed role | Evidence state | Required verification |
|---|---|---|---|
| Langfuse | Tracing, prompt lifecycle, datasets/experiments and scores | Existing evaluator-lane entry; observational | Exact cloud/self-host version, prompt lineage, trace export, dataset/eval semantics, retention, scopes and cost |
| PromptLayer | Prompt registry/version history, release labels and request analytics | Newly registered; not runtime-verified | Version pinning, commit/export API, prompt-to-request lineage, evaluator support, rollback and pricing |
| PostHog | Product/event analytics and experiment assignment/exposure | Newly registered; not runtime-verified | Assignment/exposure semantics, feature-flag versioning, event export, cohort/SRM support, privacy and pricing |
| Braintrust | Dataset/evaluation/experiment and scoring | Newly registered; not runtime-verified | Dataset/version semantics, scorer reproducibility, experiment lineage, API/export, deployment and pricing |
| Phoenix (Arize) | Existing open/self-hosted tracing/evaluation comparator | Existing evaluator-lane entry; observational | Version, storage/retention, instrumentation compatibility, evaluation reproducibility and operating cost |
| Repository-native baseline | Git-pinned prompts/config, redacted JSONL receipts, local cohorts, ATES/DoE | Canonical evidence authority | Confirm native capability and fixture coverage |

Descriptions are comparison hypotheses, not verified current feature inventories. Product claims must be checked against official docs for a pinned product version/date and exercised with bounded tests.

## 2. Evaluation dimensions

| Dimension | Measurement | Why |
|---|---|---|
| Prompt lifecycle | immutable version ID, source revision, approval/release state, rollback fidelity | Prevent hidden prompt drift |
| Invocation lineage | run → prompt → model@version → role → tools → dataset/evaluator | Causal attribution |
| Trace quality | span completeness, correlation IDs, missingness, redaction fidelity | Evidence trust |
| Experiment integrity | assignment, exposure, sample ratio, contamination, holdout | Prevent false uplift |
| Evaluation quality | dataset pinning, scorer version, inter-rater agreement, reproducibility | Prevent score gaming |
| Outcome validity | task success, correctness, integration and regression | Correctness outranks activity |
| Economics | tokens, requests, credits, storage, egress, seats, operations | Total cost |
| Portability | export format, API, schema stability, lock-in, self-hosting | Durable evidence |
| Governance | scopes, RBAC, retention, deletion, residency, privacy, auditability | Safe data movement |
| Reliability | rate limits, outage behavior, retry semantics, data loss/recovery | Failure isolation |
| Maintenance | setup/upgrade effort, dependencies, operational ownership | Long-run burden |

## 3. Four-factor complete factorial

Factors: L = Langfuse adapter; P = PromptLayer adapter; H = PostHog adapter; B = Braintrust adapter. Each is off/on. A complete 2^4 factorial has 16 combinations:

| Arm | L | P | H | B | Interpretation |
|---|---:|---:|---:|---:|---|
| A00 | 0 | 0 | 0 | 0 | Native Git/JSONL baseline |
| A01 | 1 | 0 | 0 | 0 | Langfuse only |
| A02 | 0 | 1 | 0 | 0 | PromptLayer only |
| A03 | 0 | 0 | 1 | 0 | PostHog only |
| A04 | 0 | 0 | 0 | 1 | Braintrust only |
| A05 | 1 | 1 | 0 | 0 | Langfuse + PromptLayer |
| A06 | 1 | 0 | 1 | 0 | Langfuse + PostHog |
| A07 | 1 | 0 | 0 | 1 | Langfuse + Braintrust |
| A08 | 0 | 1 | 1 | 0 | PromptLayer + PostHog |
| A09 | 0 | 1 | 0 | 1 | PromptLayer + Braintrust |
| A10 | 0 | 0 | 1 | 1 | PostHog + Braintrust |
| A11 | 1 | 1 | 1 | 0 | Langfuse + PromptLayer + PostHog |
| A12 | 1 | 1 | 0 | 1 | Langfuse + PromptLayer + Braintrust |
| A13 | 1 | 0 | 1 | 1 | Langfuse + PostHog + Braintrust |
| A14 | 0 | 1 | 1 | 1 | PromptLayer + PostHog + Braintrust |
| A15 | 1 | 1 | 1 | 1 | All four adapters |

This estimates all main effects and interactions, subject to replication and valid assignment. An arm is executable only when every enabled adapter passes admission, cost, privacy and read-only runtime proof. If a platform is unavailable, mark the arm blocked/not executable; never silently substitute. A smaller screening design must declare aliasing and cannot claim all interactions are identified.

## 4. Cohorts and blocks

Use two task families with separate outcomes:
1. Prompt lifecycle: prompt change → review → release → invocation → rollback/reproduction.
2. Agent evaluation: fixed task/dataset → invocation → trace/evaluation → outcome and regression verification.

Block by task family, model@version, configured-instance identity, runtime and time window. Match task instances across treatments and randomize treatment order. Keep inputs, prompt bytes, model settings, tools and evaluator versions identical except declared factors.

One dispatched/executed run is one observation and one canonical experiment record. Repeated runs on the same task are not independent task replications.

## 5. Outcomes and analysis

Primary: proportion of tasks meeting frozen correctness + integration acceptance contract.

Secondary: trace completeness, prompt lineage, assignment integrity, evaluation reproducibility, regression detection, missingness, latency, tokens/credits, human intervention, retries, export portability, security findings and operator effort.

Set practical improvement and non-inferiority margins, sample-size/power approach, missing-data handling, stopping rule and confirmation cohort before execution. Report uncertainty. No significance claim from an unpowered screening sample.

Estimate main effects and interactions; check sample-ratio mismatch before analysis; report per-cohort outcomes and missingness; compare correctness first, then reliability, privacy/security, cost, latency and maintenance. Produce a Pareto frontier rather than an opaque weighted score. Confirm finalists on held-out tasks. Retain combinations only when marginal benefit exceeds integration/maintenance cost. Retain distinct evidence providers when they add decision value.

## 6. Required evidence and disposition

For each candidate retain official documentation URL/retrieval date, exact product/deployment/version, API and least-privilege scopes, redacted fixtures, prompt/model/run lineage, cost/latency/retention/export observations, failure/rate-limit/retry behavior, privacy/security review, canonical experiment refs, limitations and unknowns.

All four are candidates only. This change does not connect accounts, provision API keys, make billable calls, upload prompt/customer data or deploy adapters. Native baseline and existing Phoenix, DSPy, SWE and local cohort lanes remain participants.
