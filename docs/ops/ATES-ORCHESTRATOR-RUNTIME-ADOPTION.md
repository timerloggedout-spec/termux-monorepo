# Runtime Orchestrator Trace Adoption

The benchmark lane is intentionally decoupled from the legacy orchestrator implementation.

Runtime instrumentation should emit the canonical `ates.orchestrator.trace.v1` envelope at orchestration boundaries, using fingerprints rather than raw prompt/result payloads. ATES remains observational; MLflow is an optional downstream adapter.

Adoption order:
1. Wrap orchestration, retrieval, spawn, actor, critic, validator, and tool boundaries.
2. Propagate `trace_id` and `parent_span_id` through async tasks.
3. Use isolated SPAWN mode for sibling sessions with no inherited parent context.
4. Emit JSONL once per completed span.
5. Feed the same JSONL to the deterministic ATES reducer and optional MLflow exporter.
6. Run matched DoE/MVT cohorts before any DSPy optimization artifact is considered for promotion.

Do not make telemetry collection a correctness gate.
