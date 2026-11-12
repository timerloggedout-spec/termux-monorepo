# Delphic → QUE / AutonomousOpsStuff integration contract

**Status:** proposal / integration boundary only  
**Version:** 0.1.0  
**Date:** 2026-11-12  
**Related:** Delphic #968 · scoped PR #5216 · QUE migration #5113 · participant identity #5136 · QDesk RFP #5145 · proposal digest #5156

## Purpose

Make Delphic a reusable evidence/decision analysis capability inside QUE without creating a second orchestrator or silently granting it operational authority.

## Placement

```text
Canonical evidence + immutable receipts
             │
             ▼
     QUE governor / dispatch
       │ policy, gates, timebox
       ▼
   Delphic analysis adapter
       │ deterministic, bounded, read-only
       ├── Bayesian posterior / predictive
       ├── information gain / EVSI
       ├── DAG / trellis / Markov projection
       └── expected path cost / uncertainty
             │
             ▼
     Decision packet (proposal only)
             │
             ▼
  Human/authorized seat + governor decision
             │
             ▼
   Existing dispatch/action machinery
             │
             ▼
     append-only execution receipts
```

## Consumer contracts

1. **Input:** immutable evidence references, source hashes, schema versions, explicit observation windows, declared missingness, and caller/seat identity.
2. **Execution:** local deterministic stdlib-only calculation; bounded input size and execution budget; no provider/network calls in the calculation path.
3. **Output:** analysis record with input digest, algorithm/formula version, parameters, assumptions, missingness, result, uncertainty, complexity estimate, runtime, and provenance.
4. **Authority:** analysis is advisory. QUE governor retains routing, policy, approval, timebox, escalation and dispatch authority. Delphic cannot mint permissions, authorize spending, dispatch work, mutate canonical evidence, or promote a candidate.
5. **Receipt:** emit a proposal/analysis reference to the existing QUE feed; only the authorized execution surface emits an action receipt. Never fabricate a successful execution receipt from an analysis result.
6. **Replay:** same immutable inputs + same versioned contract must yield equivalent deterministic output within declared numeric tolerances.
7. **Failure:** missing, stale, malformed or conflicting evidence returns HELD/INCONCLUSIVE with reasons; no silent imputation or default-to-success.

## Integration tranches

| Tranche | Work | Done evidence |
|---|---|---|
| A — passive consumer | Read existing QUE/DoE feed snapshots; produce analysis packet only | fixture + provenance/digest + zero writes |
| B — proposal adapter | Publish analysis reference into QUE proposal surface | schema validation + append-only receipt + idempotency test |
| C — governed dispatch | QUE may consider packet under existing gate/approval rules | explicit gate reference + before/after + action receipt |
| D — feedback | Compare forecast to observed outcomes; calibrate priors and review admission | time-windowed calibration report + reproducible fixture |

Tranche A is the first implementation target. B–D remain gated by their own issues and acceptance evidence.

## Cross-context integrations

- **QDesk / Delphi / DoE:** provide EVSI, uncertainty, expected path cost and adversarial-review evidence as inputs to existing RFP/award and signed-package workflows. The QD-039 proposal-package digest remains independently mandatory; Delphic output does not substitute for approval or signature.
- **Context relationship graph:** export read-only, provenance-carrying projections; do not mutate historical backfills or canonical graph records.
- **ArchWiz / Markov Trellis:** reuse graph-kind and algorithm registry; preserve tree-vs-recombining-trellis distinction and predecessor provenance.
- **Research-Astute lanes:** consume versioned analysis contracts and publish isolated research receipts; no cross-org credentials or implicit authority.
- **CI / review:** use repository-native checks and available independent reviewers. Gemini Dispatch is deprecated and must not be invoked as a required or assumed review provider.

## Runtime and availability

Termux Origin is currently offline (operator-reported, 2026-11-12). Do not require a Termux-originated live run for this research PR. GitHub-hosted tests validate portable logic only; the Termux target gate remains explicitly NOT RUN / PENDING until Origin returns. Do not relabel GitHub-hosted smoke as native-device proof.

## Wolfram boundary

Wolfram is for symbolic derivation, simplification, identity checks and adversarial mathematical review. Production calculations remain local, deterministic and stdlib-only.

## Non-goals

No replacement QUE scheduler, no parallel governor, no direct action execution, no automatic approval, no hidden telemetry, no external calculator dependency, no false live-state dashboard.


## DoE / MoneyBall model-task pool integration

See `docs/ops/DELPHIC-DOE-MONEYBALL-INTEGRATION.md` for the normative contract. Delphic feeds task-fit evidence and deterministic analysis into the existing DoE/MoneyBall pool. Assignment is per exact configured instance (provider × model@version × endpoint × protocol × account scope × prompt/tool hashes × role/context × instance_key), never model name alone. Reuse DoE Experiment records, MoneyBall participant wallets/cull waterfall, QUE admission and executor, quota ledger, and independent verification. No new scheduler, model catalog, wallet ledger, or quota system. Role-clone work remains gated by #5183 census and #5136 identity issuance; pool dispatch remains gated by #5176/#4979/#5151 sequencing. No live provider probes, paid fallback, wallet movement, or participant provisioning in this integration tranche.
