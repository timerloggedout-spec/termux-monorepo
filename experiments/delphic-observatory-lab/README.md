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

### Adversarial review

Review admission is triggered by evidence signals, including posterior uncertainty, benchmark regression, anomaly/retry density, provenance gaps, change-point evidence, and decision impact. This is an admission mechanism, not a reviewer ranking.

## Run

```bash
python3 scripts/delphic_oracle.py /path/to/input.json
pytest -q tests/test_delphic_oracle.py
```
