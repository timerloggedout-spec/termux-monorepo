# ITEMS — l3verage-department

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| L3V-001 | P1 | done | Establish department charter, taxonomy, lifecycle, measurement and authority boundaries. | Department reuses CEEL, Integration Intelligence, DoE, ATES, 3L0/Moneyball, evidence envelope and existing governance; no duplicate control plane. |
| L3V-002 | P1 | done | Define strict mechanism schema and hypothesis catalog. | JSON parses; IDs unique; taxonomy/lifecycle valid; evidence references typed; validated/promoted states require evidence; seed entries remain hypotheses. |
| L3V-003 | P1 | done | Implement deterministic stdlib validator and regression tests. | Valid catalog passes; malformed fields, invalid states/classes, missing required fields, invalid timestamps, and evidence-free validation claims fail. |
| L3V-004 | P1 | done | Integrate leverage measurements with DoE, ATES and 3L0/Moneyball. | Read-only comparator consumes canonical EXPERIMENT JSONL; requires explicit cohort, arms, configured-instance keys, matched task/environment fingerprints, outcome/cost metrics, guardrails and preregistered sample size; no parallel telemetry. |
| L3V-005 | P1 | done | Design a bounded, reversible context-reuse pilot. | Pilot 001 specifies matched arms, frozen cohort requirements, cost/outcome measures, stop/rollback and independent verification; remains unadmitted and unrun pending DoE owner admission. |
| L3V-006 | P2 | done | Establish the opportunity review and compounding loop. | Review uses transparent impact/effort/confidence/reversibility/risk dimensions; no opaque score; lifecycle changes cite evidence and preserve Pareto trade-offs. |
| L3V-007 | P1 | posted | Admit and execute Pilot 001 through the DoE family. | DoE owner freezes cohort, metrics, configured instances and design; canonical arm-run records and independent verification exist before mechanism validation or promotion. |

## Validation

    python3 scripts/leverage/validate_mechanisms.py
    python3 -m unittest discover -s tests -p 'test_leverage*.py' -v
    python3 scripts/leverage/compare_experiment_records.py --help
    python3 scripts/proposals/validate_registry.py
    python3 scripts/ci/repo_gate.py

Termux smoke is optional platform evidence and is not an L3VERAGE required gate. GitHub connector writes do not execute a local checkout. Commands must run in repository CI or a full checkout, and results must be re-fetched against the same immutable PR head SHA. A queued or running check is not a pass.
