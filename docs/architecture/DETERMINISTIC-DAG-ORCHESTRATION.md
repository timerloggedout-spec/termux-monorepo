# Deterministic DAG planning and dependency admission

## Status

Reference implementation only. This module plans a static dependency graph and
classifies whether a node's prerequisites permit admission. It does not execute
tasks, mutate a graph, access FalkorDB, or propagate probabilities.

## Contract

- An edge `(prerequisite, dependent)` means the prerequisite must be resolved
  before the dependent can be admitted.
- Duplicate edges are deduplicated. Unknown endpoints are rejected.
- Disconnected components are valid; no edge is inferred between them.
- A min-heap provides deterministic lexical tie-breaking among ready nodes.
- `ready_frontiers` groups emitted nodes into concurrent dependency waves by
  longest prerequisite path; it is not a snapshot after each individual heap
  pop. The graph hash covers sorted nodes, deduplicated edges, edge semantics,
  and algorithm version. The plan includes frontiers, ordered nodes, residual
  nodes, and acyclicity. `kahn-reference-v2` distinguishes corrected wave plans
  from the earlier heap-snapshot projection in provenance records.
- If Kahn emits fewer nodes than supplied, the residual set contains nodes in
  cycles and any descendants still blocked behind those cycles. It is not a
  claim that every residual node is itself part of a cycle.
- `dependency_state` returns `ready` only when all prerequisites are terminal
  and in the caller's allowed-success set. Known blockers take precedence over
  unknown prerequisites; absent evidence is never interpreted as success.

## State policy

The primitive recognizes `succeeded`, `skipped`, `failed`, and `blocked` as
terminal labels. The default admission policy accepts only `succeeded`; callers
may explicitly allow `skipped` where their task contract permits it. An
in-progress or other nonterminal state blocks admission. Missing/`unknown`
states return `unknown` unless another prerequisite already proves the node
blocked. The seeded state matrix tests this precedence and the opt-in skipped
policy; this is an admission classifier, not a persisted execution state machine.

## Validation

`tests/test_dag_execution.py` covers deterministic examples and malformed
inputs. `tests/test_dag_properties.py` adds seeded graph-property checks,
input-order/hash invariance, dependency-order invariants, and a state admission
matrix. When NetworkX is installed, the test suite additionally compares
lexicographical Kahn order against `networkx.lexicographical_topological_sort`.
The required test path remains standard-library-only for Termux and works
offline; therefore the oracle test is explicitly skipped when NetworkX is not
installed. To run the oracle lane locally, install a repository-approved
NetworkX version in a disposable development environment and run:

```sh
python3 -m unittest discover -s tests -p 'test_dag_properties.py' -v
```

## Benchmark and database decision

A reproducible Python/optional-NetworkX microbenchmark is available:

```sh
python3 scripts/benchmarks/benchmark_dag_planner.py --nodes 500 --edge-probability 0.004 --seed 1443 --repeats 5
```

The JSON receipt records the graph hash, algorithm version, graph size, seed,
median timings, and whether the NetworkX order matched. It explicitly reports
FalkorDB measurement as `not_run`; it does not fabricate a database result.
Before choosing a production execution authority, run the same pinned graph
fixtures against the repository's FalkorDB fork and record server version,
dataset hash, mutation rate, query shape, network placement, warm/cold cache,
p50/p95 latency, and resource use. No database connection or representative
FalkorDB service is assumed by this offline harness, so that comparison remains
an environment-dependent promotion gate.

## Complexity and limitations

The algorithm is O(V + E) for graph traversal, with deterministic sorting and
heap operations adding ordering overhead. This small reference is intended for
correctness and contract tests, not a claim that Python beats database-side
frontier queries. NetworkX is an independent test oracle, not a production
execution authority by default.

## Probability, provenance, and corpus safety

A topological order expresses prerequisite ordering only. It does not imply
conditional independence, multiply branch probabilities, or recalculate beliefs.
Probability propagation requires a separate model, explicit assumptions, and
independent tests. Likewise, a corpus checkpoint must pass its own provenance
and validation gates; successful topological sorting alone never makes data
eligible for promotion. The plan records graph SHA-256 and algorithm version;
source SHA, run identity, probability-model provenance, and corpus promotion
receipts belong to the eventual execution/observability layer rather than this
pure planner.
