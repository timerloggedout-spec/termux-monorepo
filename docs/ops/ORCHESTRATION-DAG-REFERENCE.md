# Deterministic Orchestration DAG Reference

**Status:** isolated reference primitive; not an execution authority.

## Contract

- Edge direction is **prerequisite → dependent**.
- Node identifiers are non-empty, unique strings. Edges with unknown endpoints fail closed.
- Duplicate edges are deduplicated before hashing and ordering.
- Kahn's algorithm uses a lexical min-heap for reproducible tie-breaking.
- Disconnected components are valid and remain disconnected.
- A cycle report distinguishes vertices in cyclic strongly-connected components from downstream vertices left blocked by those cycles.
- Readiness is separate from ordering: a node is `READY` only if every direct prerequisite is explicitly `SUCCEEDED`. Failed/skipped/blocked prerequisites block downstream work; missing, running, pending, and unknown observations never imply success.
- The module does not dispatch tasks, mutate a scheduler, infer edges from the context-relationship graph, or calculate probabilities.

## Diagnostic receipt

`analyze_dag()` returns a compact in-memory diagnostic receipt containing:

- `schema_version` and algorithm version;
- caller-provided `run_id` and 40-character lowercase source commit SHA;
- SHA-256 of a canonical JSON graph document (sorted nodes and deduplicated edges);
- node/edge counts, emitted-order coverage, deterministic topological order;
- ready-frontier transitions;
- validation state, cyclic nodes, downstream blocked nodes, and all unresolved nodes;
- an explicit provenance-completeness flag.

Coverage is the fraction of input nodes emitted by Kahn's algorithm. It is not a confidence score and must not be interpreted as task success. For a non-empty cyclic graph, unresolved nodes reduce coverage. An empty graph is valid, but its coverage is not a measured percentage and must be represented as `null`.

The diagnostic result is not yet a persisted `ORCHESTRATION-RECEIPT.schema.json` instance or a promotion authorization. An adapter must map it to the canonical receipt contract before storing it.

## Validation and limits

Run the focused suite with:

```sh
python3 -m unittest discover -s tests -p 'test_orchestration_dag.py' -v
```

The tests cover chains, fan-in/fan-out, disconnected components, duplicate edges, unknown endpoints, empty graphs, deterministic ordering, cycle/downstream-blocked reporting, receipt provenance, and prerequisite readiness.

The implementation is a small Python reference baseline. A production-scale decision is deliberately deferred until measured benchmarks compare representative graph sizes and mutation rates against a NetworkX oracle and the pinned FalkorDB fork. NetworkX is not a runtime authority. Incremental recomputation, probability/state recomputation at merge nodes, durable receipt integration, and historical-corpus promotion remain separate work items.

## Promotion boundary

A valid topological order proves only that the returned order respects the supplied acyclic dependency graph. It does not prove that the edges are correct, that tasks succeeded, that probabilities may be multiplied, or that historical corpus data is eligible for promotion. Each of those requires its own evidence and policy gate.
