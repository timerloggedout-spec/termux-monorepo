# Existing System Map — Coralogix/FOSS Reconstruction

This proposal extends the monorepo's existing evidence, telemetry, procurement, and integration surfaces.

| Existing surface | Verified role | Extension point |
|---|---|---|
| config/agent_stack_integrations.json | otel-core already ADOPT as canonical-neutral-telemetry-boundary | Pin Collector/SDK/exporter versions; preserve canonical JSONL receipts |
| docs/research/AGENT-EVIDENCE.schema.json | Agent lifecycle and tool event schema | Add trace/experiment fields through versioned schema change |
| docs/integrations/schemas/integration-event.schema.json | Normalized provider event envelope | Map provider request IDs, workflow/SHA, outcome, privacy, idempotency |
| docs/ops/EVIDENCE-ENVELOPE.schema.json | SHA-bound reconciliation evidence | Bind experiment results and confidence to immutable revisions |
| docs/integrations/ADAPTER-CONTRACT.md | Provider adapter lifecycle and guardrails | Add adapter-specific tests and promotion evidence |
| scripts/telemetry_ingest/ingest.py + sources.json | Manifest-driven Provenance and HindSight sinks | Extend source manifest/extractors while preserving separate sink contracts |
| data/briefing/procurement.jsonl | Existing ForeSight procurement/resource evidence | Record candidate version, license, portability, cost, confidence, disposition |
| ops/telemetry/integration-observability-index.json | Existing integration status projection | Add provider status only when source evidence and owner state support it |
| docs/ops/AGENT-OBSERVABILITY-RESEARCH-MATRIX.md | Existing parallel evaluation matrix | Maintain candidate comparisons and adapter decisions |
| refTemplates/05 and 11 | Source metadata and capability extraction | Keep provider references discoverable and metadata-first |

## Existing candidate status

- OpenTelemetry: existing integration catalog entry otel-core is ADOPT. Collector runtime deployment remains a distinct implementation decision.
- Langfuse and Phoenix: already represented in the observability research matrix and ForeSight procurement records; refTemplates adds source-level capability dossiers.
- Other providers: newly registered as comparison candidates; runtime admission requires exact-revision, compatibility, resource, security, and license evidence.

## Extension sequence

1. Validate the existing schema composition with fixtures.
2. Add a versioned trace/experiment context extension to the owning schema where required.
3. Implement one read-only provider adapter at a time under ADAPTER-CONTRACT.md.
4. Replay the same sanitized cohort into two operational providers and two AI evaluation providers.
5. Compare completeness, decision quality, privacy, resource use, export, and variance.
6. Record results in existing ForeSight and telemetry indexes; promote through repository gates.

## ForeSight candidate registration

The current branch appends 11 records to data/foresight/resource-registry.jsonl: OpenTelemetry Collector, SigNoz, HyperDX/ClickStack, OpenObserve, Parca, Grafana Pyroscope, Langfuse, Phoenix, Coralogix, My-Jogyo, and Docxology. Each record carries a resource/item/lane identity, H1 horizon, research_finding status, canonical source, procurement dimensions, unresolved questions, and a recomputed evidence_hash. The older data/briefing/procurement.jsonl remains a briefing-side extract; the Foresight resource registry is the canonical radar/procurement record.
