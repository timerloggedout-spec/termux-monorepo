# Delphic Bayesian Oracle × Observatory Lab

A standalone Gemini-style design/evaluation surface.

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

Open `graph-lab.html` from the experiment directory to explore the visual Step / Play / Reset interaction.

### Semantic boundaries

These graph kinds are intentionally distinct:

- `git_history`
- `decision_dag`
- `evidence_dag`
- `dependency_dag`
- `state_reconciliation`
- `markov_trellis`

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
- **Information value:** scalar EVI and outcome-weighted EVSI-style utility calculations require finite inputs and normalized outcome probabilities.
- **Markov:** transition probabilities are explicit, finite, non-negative, and complete over every modeled outgoing edge; terminal mass is exposed so probability cannot disappear silently.
- **DAG:** Kahn ordering and longest-path dynamic programming retain theoretical `O(V+E)` bounds while documenting deterministic reference-implementation sorting overhead; longest-path distance is measured in edges.
- **Ancestry:** maximal common ancestors are defined for general DAGs and can be multiple; tree-only LCA assumptions are not imported.
- **Reconciliation:** missing keys and explicit `null` values remain distinct, so clean deletions are not converted into synthetic nulls.
- **Provenance:** algorithm input and parameter digests cover every value capable of changing a result.

Wolfram is used as an external mathematical reference/verification layer. The production research lane remains stdlib-only and does not make runtime calls to Wolfram.
