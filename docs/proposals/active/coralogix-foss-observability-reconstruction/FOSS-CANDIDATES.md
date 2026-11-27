# FOSS and Commercial Capability Candidates

**Evaluation rule:** parallel candidates consume the same evidence contract. This is a research shortlist, not a deployment or endorsement record.

| Candidate | Primary capability | Reported license posture | Proposed role |
|---|---|---|---|
| OpenTelemetry Collector | Receivers/processors/exporters for logs, metrics, traces | Apache-2.0 | P0 Collector component reference; the repository already adopts otel-core as the neutral boundary |
| SigNoz | OTel-native logs, metrics, traces, APM | MIT core; enterprise directories carry separate terms | P1 operational UI |
| HyperDX / ClickStack | Logs, traces, metrics, errors, session replay | MIT reported for HyperDX; verify component boundaries | P1 operational UI |
| OpenObserve | Logs, metrics, traces, dashboards, alerts | AGPL-3.0 core; enterprise features separately licensed | P1 operational UI; legal review |
| Parca | Continuous CPU/memory profiling | Apache-2.0 | P1 preferred permissive profiler |
| Grafana Pyroscope | Continuous profiling and telemetry correlation | AGPL-3.0 | P1 profiling comparator |
| Langfuse | LLM traces, datasets, evaluations, experiments, prompts | MIT core; enterprise components have separate terms | P1 AI experiment adapter |
| Arize Phoenix | LLM tracing, evaluations, datasets, experiments | ELv2, source-available | P1 AI experiment comparator; legal review |
| Coralogix | Commercial integrated observability, GitHub context, MCP/query | Proprietary commercial service | Capability/procurement comparator |

## Comparison dimensions

Signal coverage; OTLP/JSONL ingestion; batching/retries/backpressure/event limits; workflow/SHA/task/experiment/request correlation; dataset replay and evaluator provenance; CPU/memory profiling and ARM/Linux support; self-hosting, retention, export and offline behavior; auth/RBAC/audit/redaction; total operating cost; exact-revision license and dependency obligations.

## Recommended comparison set

- Interoperability: OpenTelemetry Collector.
- Operational UI: SigNoz vs HyperDX/ClickStack vs OpenObserve; Coralogix as commercial comparator.
- AI experiments: Langfuse vs Phoenix.
- Profiling: Parca vs Pyroscope.
- Research methods: My-Jogyo and Docxology as complementary exemplars; our own evidence and validation contracts.

License labels are research findings from upstream materials and prior source review. Each implementation candidate receives an exact-revision LICENSE/NOTICE/dependency scan before cloning, modification, redistribution, deployment, or custom-fork promotion. Preserve component-level boundaries. This register distinguishes reported posture from completed legal determination.
