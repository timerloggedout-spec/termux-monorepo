# Synaptic Bus Compatibility Matrix

The bus is a correlation and transport envelope. Existing schemas remain canonical for their own domains.

| Existing contract / plane | Canonical owner | Bus event(s) | Bus carries | Bus must not do |
|---|---|---|---|---|
| `integration-event.schema.json` | Integration adapter | observation / action lifecycle | event ID, integration record reference, correlation | Copy execution payload or redefine integration status |
| `EPS-EVENT.schema.json` | Evidence Projection Surface | observation / attention / outcome | EPS event reference, source SHA, provenance | Replace EPS event ledger or broaden its attributes |
| `ORCHESTRATION-RECEIPT.schema.json` | Orchestrator | plan / route / handoff / action / outcome | receipt reference, cycle and attempt IDs | Treat a receipt projection as complete longitudinal evidence |
| `AGENT-THROUGHPUT-EVENT.schema.json` | Throughput collector | action started/completed/failed | throughput event reference and task/agent dimensions | Copy tokens, prompts, or tool payloads into a general event stream |
| `ACTION-EFFECT-EVENT.schema.json` | Action/effect evaluator | outcome recorded / validation completed | correlation reference and confidence pointer | Claim causal attribution from temporal follow-through |
| `EVIDENCE-ENVELOPE.schema.json` | Reconciliation/evidence collector | observation / outcome / validation | evidence URI, source SHA, confidence pointer | Replace SHA-bound evidence semantics |
| `ATES-ORCHESTRATOR-TRACE.schema.json` | ATES benchmark plane | plan / action / validation / outcome | trace and benchmark-case references | Flatten spans or combine benchmark scores with 3L0 |
| `3l0-intake/v1` | 3L0 scoring plane | action completion / confirmed outcome | reference to immutable intake record | Score actors, fold weights, or rewrite intake history |
| MoneyBall | MoneyBall PR-scoring plane | none directly | no scoring ownership | Merge with 3L0 or consume raw bus traffic as a score |

## Field mapping guidance

- `event_id` is the bus identity; keep each source system's own event/receipt ID in its evidence reference.
- `correlation.task_id`, `orchestration_id`, `cycle_id`, and `attempt_id` should be copied only from the owning source record.
- `subject.sha` is the source object SHA, not necessarily the commit created by the action.
- `actor.provider`, `actor.model`, `actor.adapter`, and `actor.role` remain independent dimensions. Unknown is null, never inferred from a GitHub author.
- `status` is the bus lifecycle status. Domain-specific status enums remain in the source schema.
- `evidence_refs[].uri` is an address to a canonical source record. Verify the record before making downstream claims.

## Explicit non-goals

No bus-driven ranking, provider admission, manager selection, quota adjustment, MoneyBall score, 3L0 score, or automatic dispatch is introduced. Those decisions stay with their existing owners and approval gates.
