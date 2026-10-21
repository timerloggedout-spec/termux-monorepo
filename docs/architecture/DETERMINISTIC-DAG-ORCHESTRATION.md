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
  nodes, and acyclicity.
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
blocked.

Planning and execution remain separate: the caller must record actual execution
outcomes and re-evaluate dependent nodes. This primitive does not implement
retry policy, cancellation propagation, persistence, or incremental graph
updates.

## Complexity and limitations

The algorithm is O(V + E) for graph traversal, with deterministic sorting and
heap operations adding ordering overhead. This small reference is intended for
correctness and contract tests, not a claim that Python beats database-side
frontier queries. Benchmark realistic graph sizes and mutation rates against
the repository's FalkorDB fork and a NetworkX oracle before selecting a
production execution authority.

## Probability and corpus safety

A topological order expresses prerequisite ordering only. It does not imply
conditional independence, multiply branch probabilities, or recalculate beliefs.
Probability propagation requires a separate model, explicit assumptions, and
independent tests. Likewise, a corpus checkpoint must pass its own provenance
and validation gates; successful topological sorting alone never makes data
eligible for promotion.

## Tests

`tests/test_dag_execution.py` covers empty graphs, chains, fan-in/fan-out,
disconnected components, deterministic tie-breaking, duplicate edges, unknown
endpoints, cycles with downstream residual nodes, and prerequisite admission.
NetworkX comparison/property tests and database benchmarks remain follow-up
work; they are not represented as completed here.
