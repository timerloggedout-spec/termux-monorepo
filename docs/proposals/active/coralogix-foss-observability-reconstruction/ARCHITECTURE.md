# Target Architecture

## 1. System boundary

    GitHub / Actions / agent runtimes / Termux
                      |
                      v
             workflow + task identity
                      |
                      v
             canonical JSONL + receipts
                      |
               sanitized adapter
                      |
                      v
             OpenTelemetry Collector
                /      |       \
               v       v        v
        operational  AI eval  profiling
          adapters   adapters  adapters
             |         |         |
             v         v         v
        SigNoz /    Langfuse /  Parca /
        HyperDX /   Phoenix     Pyroscope
        OpenObserve
             \         |         /
              \        |        /
               +-------+-------+
                       |
                       v
             repository-owned reducers
             ATES / 3L0 / Moneyball
                       |
                       v
                 Admin Desk views

Coralogix participates as an optional commercial comparison endpoint. Canonical evidence remains in repository-owned JSONL/receipts and immutable GitHub artifact references.

## 2. Responsibility boundaries

| Layer | Responsibility | Authority |
|---|---|---|
| Producers | Emit lifecycle, tool, model, request, result events | Producer observation |
| Identity envelope | Bind repo/ref/SHA/run/attempt/task/experiment | Canonical identity contract |
| Sanitizer | Allowlist fields, redact secrets/private payloads | Privacy policy |
| OTel Collector | Receive, batch, transform, route, export | Transport only |
| Observability providers | Query and visualize operational signals | Observational |
| AI evaluation providers | Dataset replay, scores, experiment comparison | Evaluation observations |
| Profilers | CPU/memory profile artifacts | Performance observations |
| Reducers | Derive ATES/3L0/Moneyball and confidence | Repository-owned logic |
| Admin Desk | Present status, evidence, policy and authorized actions | Governed control surface |

## 3. Adapter contract

Each adapter declares ID/version, supported signals, schema versions, identity fields preserved, redaction behavior, retry/backpressure behavior, event size/batching limits, export/deletion behavior, resource/cost model, failure mode, and health signal.

Adapters map canonical events to provider representations and preserve the original event digest. Provider-specific fields remain namespaced.

## 4. Data classes

Operational metadata: repo, ref, SHA, workflow, run attempt, job, step, task, environment fingerprint.

Experiment metadata: campaign, experiment, variant, assignment source/version, cohort, evaluation protocol.

Request metadata: request ID, trace ID, provider, model, endpoint, latency, token counts, retry count, outcome.

Profile metadata: profile type, process/runtime, sample interval, environment, profile digest.

Sensitive payloads: prompts, completions, private context, credentials, authorization headers, raw request/response bodies. Exclude by default; allow only through a separately reviewed and redacted dataset workflow.

## 5. Deployment topology

Start with ephemeral CI or local lab services and a small reproducible cohort. Keep service state and caches outside the tracked worktree. Capture container image digests, architecture, runtime versions, configuration hashes, and resource measurements.

A persistent service requires a separate decision covering storage, retention, backup, authentication, ingress, upgrade, monitoring, and deletion. Termux remains an orchestration/development surface; heavy indexing and profiling workloads belong on a declared remote or ephemeral runner unless device resource evidence supports local execution.

## 6. Failure semantics

Producer failure is distinct from collector failure and provider outage. Missing telemetry remains missing evidence. Partial exports preserve observed state and artifact digests. Provider dashboards do not override GitHub run conclusions or canonical receipts. Retries preserve original request/trace identity and add attempt metadata.
