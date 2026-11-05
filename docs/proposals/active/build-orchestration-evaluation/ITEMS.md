# ITEMS — build-orchestration-evaluation

**Proposal:** [PROPOSAL.md](PROPOSAL.md)  
**Status:** posted — implementation items are not yet authorized.  
**Rule:** this proposal is posted, not accepted, and no item is authorized. If accepted, only `BOE-00-01` and `BOE-00-02` may be considered for initial authorization; each still requires a separate recorded item-level authorization before work starts. Every later item requires its own recorded authorization. The `Authorization` column below is the item-level gate; `todo` never means authorized.

| Item | Priority | Scope / deliverable | Acceptance evidence | Authorization | Status |
|---|---|---|---|---|---|
| BOE-00-01 | P1 | Baseline inventory of project manifests, task scripts, dependency edges, existing CI jobs, and Termux constraints; emit a provenance-stamped inventory without changing project files. | Reproducible inventory; unknown/unsupported entries explicit; no secret values; repo-gate passes. | not authorized (no recorded item vote) | todo |
| BOE-00-02 | P1 | Define canonical task/project/evidence schemas and adapter contract, including task identity, input fingerprint, environment fingerprint, outputs, cache policy, provenance, and failure semantics. | JSON Schema fixtures validate; duplicate/ambiguous identities rejected; contract docs reviewed. | not authorized (no recorded item vote) | todo |
| BOE-10-01 | P1 | Build equivalent pilot fixtures and baseline native execution measurements for representative Python, Node, Rust, and Go projects actually present in the repository. | Fixture selection tied to BOE-00-01; cold/warm baseline receipts; no fabricated language lane. | not authorized (no recorded item vote) | todo |
| BOE-10-02 | P1 | Prototype Turborepo only for eligible JS/TS package tasks; verify package/workspace prerequisites and cache invalidation. | Turbo adapter report; exact commands and lockfile; no root-wide adoption assumption. | not authorized (no recorded item vote) | todo |
| BOE-10-03 | P1 | Prototype Nx project graph/affected-task detection and task caching against the same eligible workload set. | Nx adapter report; plugin/configuration footprint; correctness compared with baseline. | not authorized (no recorded item vote) | todo |
| BOE-10-04 | P1 | Prototype Moonrepo as the primary polyglot candidate, including language/toolchain support and task graph semantics. | Moon report; Termux install/runtime feasibility; equivalent workload results. | not authorized (no recorded item vote) | todo |
| BOE-10-05 | P2 | Assess Bazel as a bounded reference candidate, not a default deployment target; quantify hermeticity and operational overhead. | Written go/no-go with reproducibility and maintenance evidence. | not authorized (no recorded item vote) | todo |
| BOE-20-01 | P1 | Implement a read-only evaluator that maps the canonical project/task registry to candidate adapters and produces comparable run receipts. | Deterministic output; no dispatch or writes; fixtures and negative tests pass. | not authorized (no recorded item vote) | todo |
| BOE-20-02 | P1 | Integrate evaluation receipts with existing DOE/MVT and action-effectiveness evidence, preserving observed-vs-planned cadence and retention rules. | Crosswalk to existing schemas; deduplication/idempotency tests; no telemetry deletion. | not authorized (no recorded item vote) | todo |
| BOE-20-03 | P1 | Define GitHub Actions orchestration boundaries: validation, evaluation, and optional execution remain separate jobs/workflows with least privilege. | Workflow threat review; permissions matrix; no implicit workflow-token chaining. | not authorized (no recorded item vote) | todo |
| BOE-30-01 | P1 | Validate Termux/Android execution parity and define portable fallback behavior for unavailable runtimes. | Device evidence where available; otherwise explicitly marked unverified; smoke gates remain authoritative. | not authorized (no recorded item vote) | todo |
| BOE-30-02 | P1 | Compare cost, latency, cache hit/miss correctness, invalidation, maintenance burden, and agent-context overhead; issue evidence-backed selection ADR. | Decision matrix with uncertainty, rejected alternatives, and rollback plan. | not authorized (no recorded item vote) | todo |
| BOE-40-01 | P1 | Implement only the selected adapter(s) and minimal canonical registry integration after review and acceptance. | Approved ADR; independent review; all relevant gates green on immutable SHA. | not authorized (no recorded item vote) | blocked |
| BOE-40-02 | P1 | Add operator runbook, migration/rollback, cache hygiene, secret handling, and stale-evidence reconciliation. | Dry-run runbook; rollback tested; docs and CI contract aligned. | not authorized (no recorded item vote) | blocked |

## Authorization record

An item is eligible only when its `DEBATE.md` contains a recorded authorization naming the exact item ID, bounded scope/deliverable, approver, timestamp, and evidence reference. The authorization must be explicit and current; silence, proposal acceptance, a `todo` status, a PR comment, or an agent's inference is not authorization. Record revocation or supersession in the same decision log. No item in this proposal currently has such a record.

## Dependency order

`BOE-00-01` → `BOE-00-02` → `BOE-10-01` → `BOE-10-02/03/04` (+ bounded `BOE-10-05`) → `BOE-20-01/02/03` → `BOE-30-01/02` → review/ADR → `BOE-40-01/02`.

The candidate prototypes are parallelizable only after the same fixture set and contract are pinned. No candidate may change shared workflow files during the evaluation phase.
