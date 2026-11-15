# Delphic Bayesian Oracle × Observatory Lab

A standalone Gemini-style design/evaluation surface.

## Versioned Tribute surface

- `VERSION.json` records the experiment-lane version (`0.2.0`, research-preview).
- The four-family graph view is published through Tribute at `apps/tribute-dashboard/delphic-graph.html`.
- `apps/tribute-dashboard/algorithm-labs.json` registers the lane and its UI/source/version references.
- The nested version header links to the experiment source, engine, tests, and version record.

## Architecture

```
                         CANONICAL EVIDENCE
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             LEFT / NOW                RIGHT / THREADING
       tensor · graph · matrix      DAG · trellis · Markov
          · constellation            · provenance
                    │                       │
                    └───────────┬───────────┘
                                ▼
                       DELPHIC ORACLE
                  posterior · uncertainty · EVI
                                │
                                ▼
                    REVIEW ADMISSION SIGNAL
                                │
                                ▼
                         OBSERVATORY
                      read-only projection
```

### Semantics

The left side answers **what is observed now and how evidence is related**.

The right side answers **how hypotheses, states, treatments, observations, and routes interthread over time**.

The Oracle does not declare truth. It explains current belief and the information still worth acquiring.

### Graph Lab

The standalone Graph Lab is the executable-explanation surface for the algorithms behind the right-side projections:

- Kahn topological ordering.
- DAG longest-path dynamic programming.
- Forward probability propagation with explicit normalized transitions.
- Maximal common ancestors for general DAGs, including criss-cross histories.
- Three-way reconciliation as a distinct state-reconciliation operation.

Algorithm definitions live in `docs/schemas/graph-algorithm-registry.yaml`, while deterministic reference implementations live in `scripts/delphic_graph_lab.py`.

Open `graph-lab.html` for the original Step / Play / Reset algorithm demo. Open `graph-views.html` for the four-family interactive map: AST containment, Kahn dependency DAG, Markov trellis with per-layer mass checks, and temporal snapshot lineage. The four panels have independent fixture-refresh state; refresh is local-only and never claims a remote fetch.

### Semantic boundaries

These graph kinds are intentionally distinct:

- `git_history`
- `decision_dag`
- `evidence_dag`
- `dependency_dag`
- `state_reconciliation`
- `markov_trellis`
- `ast_containment`
- `temporal_lineage`

A DAG does **not** imply that every graph operation is `O(V+E)`. Complexity is registered per algorithm.

Tree-only LCA algorithms are not treated as general-DAG common-ancestor solvers. Multiple maximal common ancestors remain explicit rather than being silently collapsed.

### Adversarial review

Review admission is triggered by evidence signals, including posterior uncertainty, benchmark regression, anomaly/retry density, provenance gaps, change-point evidence, and decision impact. This is an admission mechanism, not a reviewer ranking.

## Run

```bash
python3 scripts/delphic_oracle.py /path/to/input.json
pytest -q tests/test_delphic_oracle.py
```


## Mathematical substrate

The lane now treats mathematics as a contract rather than presentation metadata:

- **Bayesian:** Beta-Bernoulli posterior updates with exact equal-tail Beta credible intervals; the normal approximation remains available only as explicitly labeled legacy/approximate output.
- **Posterior prediction:** Beta-Binomial predictive PMF, mean, and variance are computed in the log-Beta/log-Gamma domain for numerical stability.
- **Information theory:** Beta differential entropy, Beta-to-Beta KL divergence, and one-step expected information gain are explicit; tiny negative roundoff is clamped only at machine-noise scale.
- **Information value:** scalar EVI and decision-optimized binary EVSI use `E_y[max_a EU(a|y)] - max_a EU(a) - cost`, rather than treating arbitrary post-information utility as a substitute for re-optimization.
- **Markov:** transition probabilities are explicit, finite, non-negative, and complete over every modeled outgoing edge; terminal mass is exposed so probability cannot disappear silently.
- **Markov path economics:** expected accumulated edge cost is propagated alongside probability mass, preserving the recurrence `C_j += P(i→j)(C_i + m_i c(i,j))`.
- **DAG:** Kahn ordering and longest-path dynamic programming retain theoretical `O(V+E)` bounds while documenting deterministic reference-implementation sorting overhead; longest-path distance is measured in edges.
- **Ancestry:** maximal common ancestors are defined for general DAGs and can be multiple; tree-only LCA assumptions are not imported.
- **Reconciliation:** missing keys and explicit `null` values remain distinct, so clean deletions are not converted into synthetic nulls.
- **Provenance:** algorithm input and parameter digests cover every value capable of changing a result.

Wolfram is used as an external mathematical reference/verification layer. The production research lane remains stdlib-only and does not make runtime calls to Wolfram.

## Visual-model boundaries

- The browser Kahn routine in graph-views.html is a small deterministic teaching fixture. The production planner remains she/orchestration/dag.py, algorithm version kahn-reference-v2.
- The Markov panel is a probability-conservation fixture. The ArchWiz model engine in experiments/archwiz-markov-lane/src/markov-engine.mjs is the reusable transition/tree/trellis implementation.
- AST containment and temporal lineage are validated independently; neither is silently converted into a dependency DAG.
- Refresh recomputes local fixtures only. It does not fetch live GitHub data, mutate canonical evidence, dispatch work, or change routing authority.
