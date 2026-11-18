# ITEMS — l3verage-department

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| L3V-001 | P1 | done | Establish department charter, taxonomy, lifecycle, measurement and authority boundaries. | Department reuses CEEL, Integration Intelligence, DoE, ATES, 3L0/Moneyball, evidence envelope and existing governance; no duplicate control plane. |
| L3V-002 | P1 | done | Define strict mechanism schema and hypothesis catalog. | JSON parses; IDs unique; taxonomy/lifecycle valid; evidence references typed; validated/promoted states require evidence; seed entries remain hypotheses. |
| L3V-003 | P1 | done | Implement deterministic stdlib validator and regression tests. | Valid catalog passes; duplicate IDs, invalid states/classes, missing required fields and evidence-free validation claims fail. |
| L3V-004 | P1 | done | Integrate leverage measurements with DoE, ATES and 3L0/Moneyball. | Read-only comparator consumes canonical EXPERIMENT JSONL; requires explicit cohort, arms, configured-instance keys, matched task/environment fingerprints, outcome/cost metrics, guardrails and preregistered sample size; no parallel telemetry. |
| L3V-005 | designed | Select and run a bounded, reversible pilot. | Pilot has baseline, frozen cohort, treatment, cost, stop/rollback rule and independent verification; no production routing changes without separate authorization. |
| L3V-006 | executing | Build a department-level opportunity review and compounding loop. | Prioritization assumptions visible; mechanisms can be retained, adapted, combined, rejected or retired using evidence; Pareto trade-offs preserved. |

## Validation

```bash
python3 scripts/leverage/validate_mechanisms.py
python3 -m unittest discover -s tests -p 'test_leverage*.py' -v
python3 scripts/leverage/compare_experiment_records.py --help
python3 scripts/proposals/validate_registry.py
python3 scripts/ci/repo_gate.py
```

GitHub connector writes do not execute a local checkout. These commands must run in the repository's CI or a full checkout; their results must be re-fetched and bound to the same immutable PR head SHA. A queued or running check is not a pass.
