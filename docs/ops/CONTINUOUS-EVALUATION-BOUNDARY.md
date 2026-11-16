# Continuous evaluation boundary

## Invariant

Continuous evaluation is an **append-only observation loop**, not a pull-request loop.

The system may continuously:

- poll provider/model catalogs;
- discover eligible candidates;
- select a provider/model for a role;
- invoke a treatment;
- record telemetry and outcome;
- create an evaluation epoch;
- update derived ranking/selection state.

None of those observations creates a pull request.

A pull request is reserved for a **durable implementation or policy change**.

## State boundaries

```text
provider catalog
      │
      ▼
candidate population
      │
      ▼
evaluation epoch ──► immutable evidence/ledger/artifact
      │
      ▼
outcome + telemetry
      │
      ▼
catalog/ranking projection
      │
      ▼
next selection
      │
      └──────────────► next evaluation epoch
```

A moving `master` SHA is an observation dimension. It does not require a new PR.

Minimum evaluation identity:

```text
run_uid
run_attempt
epoch_id
repository
head_sha
manager_policy
task/cohort
provider
model
role
```

The catalog snapshot used for selection must be preserved with the epoch, together with its observation timestamp and a content hash. This makes a later ranking reproducible without freezing the runtime catalog.

## PR anti-spam contract

The following are **not product PRs**:

- session recon/bind/stamp receipts;
- live-master status refreshes;
- lane-matrix pulses;
- evaluation manifests;
- provider catalog observations;
- ranking recalculations;
- model/provider eligibility observations;
- repeated evidence-only skill stamps.

The PR scope guard closes session/evaluation-only PRs as not planned. This is a containment mechanism, not the primary persistence layer.

## Catalog refresh

Runtime routing prefers live provider evidence. Scheduled catalog polling therefore produces an immutable workflow artifact rather than opening a PR for every drift event.

The tracked OpenRouter snapshot remains a bootstrap seed. It is not the continuous evaluation ledger.

## Evidence and durable learning

The longitudinal evidence plane should retain:

```text
action → observation → outcome → attribution → catalog update → next selection
```

Historical observations remain immutable. Rankings are derived projections and may change without rewriting the historical evidence.

See:

- `.github/workflows/continuous-evaluation.yml`
- `.github/workflows/pr-scope-guard.yml`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `docs/ops/HEX-MONEYBALL-INTEGRATION.md`
