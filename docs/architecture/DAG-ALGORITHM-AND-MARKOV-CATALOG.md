# DAG algorithm and Markov method catalog

**Status:** consolidated reference; implementation status is stated per method.  
**Work item:** DPH-400 — `docs/proposals/active/gantt-dependency-phases/ITEMS.md`  
**Canonical planner:** `she/orchestration/dag.py` · `kahn-reference-v2`

This catalog separates methods that appeared together in repository notes but solve different problems. The canonical Kahn planner remains the deterministic dependency-ordering authority. Adjacent algorithms, analysis methods, visualization designs, and research candidates retain their own roles.

## 1. Decision map

| Family | Method / component | Repository status | Role |
|---|---|---|---|
| Topological ordering | Kahn's algorithm, lexical min-heap tie-break | **Implemented; canonical** | Stable ordering, ready frontiers, residual detection |
| Topological ordering | DFS-based topological sort | **Alternative concept; not the canonical implementation** | Produces an order by reverse finishing time; useful as an independent algorithmic comparison |
| Independent oracle | NetworkX `lexicographical_topological_sort` | **Optional test/benchmark dependency** | Compares complete ordering; not production authority |
| Python standard library | `graphlib.TopologicalSorter` | **Available alternative; not currently selected** | Dependency readiness / static ordering for Python callers |
| Cycle analysis | Tarjan strongly connected components (SCC) | **Named in visual-language research packet; integration unverified** | Identifies cyclic components precisely; complements Kahn residuals |
| Ancestry | Lowest common ancestor (LCA), including criss-cross ancestry | **Design/research reference** | Common-ancestor queries in ancestry/merge graphs |
| Reachability | Bitset reachability | **Design/research reference** | Fast repeated reachability queries when graph representation and memory budget fit |
| Layered layout | Sugiyama | **Visualization design reference** | Renders DAG layers and edge crossings |
| Graph merge | Three-way merge matrix | **Design reference** | Makes competing graph edits explicit |
| Graph merge / replication | CRDT, LWW graph representation, operation-DAG append | **Design reference** | Mergeable distributed graph updates; requires conflict and identity contracts |
| Execution backend | FalkorDB-side frontier/query computation | **Benchmark candidate; measurement not run** | Potential server-side execution for large or shared graphs |
| Probabilistic dynamics | Markov tree / recombining trellis / collapsed transition graph | **Isolated lab** | State-transition probabilities and recombination; separate from dependency ordering |

**Interpretation:** Kahn, DFS topological sorting, NetworkX, and `graphlib` concern ordering. Tarjan, LCA, and bitset reachability answer different graph-analysis questions. Sugiyama is layout. CRDT/LWW and three-way merge concern graph mutation/reconciliation. FalkorDB is a backend candidate. Markov methods model stochastic transitions. These are complementary layers, not one interchangeable algorithm list.

## 2. Canonical Kahn planner

### Contract

- Edge direction: `(prerequisite, dependent)`.
- Duplicate edges are deduplicated; unknown endpoints and malformed edges are rejected.
- Disconnected components remain valid and independent.
- A min-heap gives deterministic lexical tie-breaking among ready nodes.
- `topological_order` is the stable emitted order.
- `ready_frontiers` group nodes by longest prerequisite path; each frontier is a dependency wave, not a snapshot after every heap pop.
- Residual nodes include cycle members **and** descendants blocked behind cycles. A residual node is not automatically a cycle member.
- The plan includes graph SHA-256 and algorithm version `kahn-reference-v2`.
- `dependency_state` classifies admission from prerequisite evidence; it does not execute work.

### Implementation and consumers

| Surface | Path | Responsibility |
|---|---|---|
| Canonical planner | `she/orchestration/dag.py` | Pure deterministic plan and admission classifier |
| Contract | `docs/architecture/DETERMINISTIC-DAG-ORCHESTRATION.md` | Edge, state, residual, validation, and benchmark semantics |
| Gantt compiler | `scripts/temporal/gantt_compile.py` | Filing parsing and violation aggregation; delegates ordering to canonical planner |
| Dependency-phase engine | `scripts/agentic/dependency_phase_engine.py` | Lifecycle/evidence evaluation and deterministic phase waves |
| DoE component registry | `docs/ops/DOE-COMPONENT-REGISTRY.md`, `ops/doe/component-registry.json` | Separately registered Kahn, Gantt, Bayesian, and Markov surfaces |

The Kahn planner is side-effect free. It does not dispatch tasks, mutate a graph, query FalkorDB, or propagate probability.

## 3. Alternatives and adjacent methods

### 3.1 DFS topological ordering

DFS-based topological sorting is a genuine algorithmic alternative to Kahn. It uses a visiting/visited state (or recursion-stack coloring) and reverse finishing order. It can detect a back-edge during traversal. The repository's canonical implementation and test contract currently select Kahn; this catalog records DFS as an alternative for future comparison, not as an implemented repository path.

Comparison criteria for any future implementation: deterministic tie-breaking, cycle diagnostics, recursion-depth behavior, memory profile, stable provenance, and exact edge-direction semantics.

### 3.2 NetworkX

NetworkX is already wired as an optional independent oracle and benchmark comparator. The repository compares the canonical planner with `networkx.lexicographical_topological_sort`. Treat it as an optional development dependency; the standard test path remains standard-library-only and offline-capable.

Materialize the full generator inside the test's exception boundary. A yielded prefix is not proof that the entire graph is acyclic.

### 3.3 Python `graphlib.TopologicalSorter`

Python's standard-library `graphlib` offers another dependency-oriented API. It is a useful low-install comparison for Python consumers, but the repository's custom planner provides additional contracts: graph hashing, explicit residual nodes, lexical ordering, and ready frontiers. No current repository integration is asserted here.

### 3.4 Tarjan SCC

Tarjan's strongly connected components algorithm finds maximal mutually reachable components. It can distinguish actual cyclic components from downstream nodes that Kahn leaves residual. Use it as a diagnostic complement when precise cycle membership is required; keep Kahn as the ordering authority unless a separately reviewed change adopts another contract.

### 3.5 LCA and bitset reachability

LCA (including criss-cross ancestry) and bitset reachability appear in the Gemini visual-language packet alongside Kahn. They support ancestry and reachability queries, respectively. They do not generate a topological schedule and do not replace Kahn.

### 3.6 Sugiyama, merge matrices, CRDT/LWW

Sugiyama layered layout is a presentation algorithm. Three-way merge matrices, CRDTs, LWW graph representations, and operation-DAG append are graph-edit/reconciliation concepts. The visual-language packet records them as design directions; this catalog does not claim production integration.

### 3.7 FalkorDB

The current benchmark explicitly emits `falkordb_measurement: not_run`. Database-side frontier computation remains a candidate requiring a version-pinned, representative benchmark. Record server/fork revision, graph fixture hash, mutation rate, query shape, network placement, warm/cold cache, p50/p95, and resource use before making an authority or performance decision.

## 4. Markov boundary

Markov state-transition probability is a separate model from deterministic prerequisite order.

| Model/view | Meaning | Status |
|---|---|---|
| Strict state tree | Preserve every path occurrence; path provenance remains explicit | Markov lab |
| Recombining trellis | Merge equivalent `(time, state)` occurrences; sum incoming path mass | Markov lab |
| Collapsed transition graph | Long-horizon/state-machine view | Future/optional lab surface |
| Particle-flow walkers | Sample transitions from the same validated transition matrix | Lab visualization |
| Markov propagation through DAG ranks | Proposed coupling of probability dynamics with dependency layers | Research/design reference |

Markov lab invariants: normalize and validate outgoing transition rows; multiply transitions along a path; sum incoming path probability at recombined nodes; conserve total probability per layer for a closed stochastic system; sample particles from the same transition matrix; preserve path provenance separately from aggregate probability.

A Kahn topological order supplies dependency order only. It does not imply conditional independence, define transition probabilities, or authorize naive branch-probability multiplication. Keep the registered surfaces separate: `kahn.dag`, `gantt.dependency-phases`, `bayesian.routing`, and `markov.trellis-lab`.

## 5. Consolidated setup and validation

Run commands from the repository root.

### Core Kahn contract (standard library only)

```sh
python3 -m unittest discover -s tests -p 'test_dag_execution.py' -v
python3 -m unittest discover -s tests -p 'test_dag_properties.py' -v
```

### Optional NetworkX oracle and benchmark

Use a disposable development environment and a repository-approved NetworkX version. NetworkX is optional; Termux's core validation path remains offline and standard-library-only.

```sh
python3 -m pip install networkx
python3 -m unittest discover -s tests -p 'test_dag_properties.py' -v
python3 scripts/benchmarks/benchmark_dag_planner.py --nodes 500 --edge-probability 0.004 --seed 1443 --repeats 5
```

The benchmark records graph hash, algorithm version, graph size, seed, median timings, oracle availability/order agreement, and the explicit FalkorDB `not_run` state.

### Markov trellis lab

```sh
node experiments/archwiz-markov-lane/src/markov-engine.test.mjs
python3 -m http.server 4173 --directory experiments/archwiz-markov-lane
```

Open `http://localhost:4173/` for the isolated visualization. The lab remains outside production routing and provider admission.

### Repository gates

```sh
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
git diff --check
```

Run the two project gates on the exact proposed commit and record their evidence before promotion.

## 6. Source index

- [Canonical planner](../../she/orchestration/dag.py)
- [Deterministic DAG contract](DETERMINISTIC-DAG-ORCHESTRATION.md)
- [DoE component registry](../ops/DOE-COMPONENT-REGISTRY.md)
- [Gemini visual-language packet](../graph/GEMINI-VISUAL-LANGUAGE.md)
- [Markov trellis lab proposal](../proposals/active/archwiz-markov-trellis-lab/README.md)
- [Markov trellis lab items](../proposals/active/archwiz-markov-trellis-lab/ITEMS.md)
- [Gantt dependency-phase items](../proposals/active/gantt-dependency-phases/ITEMS.md)
- [DAG planner tests](../../tests/test_dag_execution.py) · [property tests](../../tests/test_dag_properties.py)
- [DAG benchmark](../../scripts/benchmarks/benchmark_dag_planner.py)

**Evidence boundary:** this catalog reflects the repository paths above. Research-packet items are labeled as design references unless an implementation and tests are linked. External algorithms are described as comparison options, not repository capabilities.
