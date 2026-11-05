# ITEMS — build-orchestration-evaluation

**Proposal:** [PROPOSAL.md](PROPOSAL.md)  
**Status:** posted — implementation items are not yet authorized.  
**Rule:** after proposal acceptance, initial execution is limited to `BOE-00-01` and `BOE-00-02`. Each later item requires separate recorded authorization and item-level scope confirmation.

| Item | Priority | Scope / deliverable | Acceptance evidence | Status |
|---|---|---|---|---|
| BOE-00-01 | P1 | Baseline inventory of project manifests, task scripts, dependency edges, existing CI jobs, and Termux constraints; emit a provenance-stamped inventory without changing project files. | Reproducible inventory; unknown/unsupported entries explicit; no secret values; repo-gate passes. | todo |
| BOE-00-02 | P1 | Define canonical task/project/evidence schemas and adapter contract, including task identity, input fingerprint, environment fingerprint, outputs, cache policy, provenance, and failure semantics. | JSON Schema fixtures validate; duplicate/ambiguous identities rejected; contract docs reviewed. | todo |
| BOE-10-01 | P1 | Build equivalent pilot fixtures and baseline native execution measurements for representative Python, Node, Rust, and Go projects actually present in the repository. | Fixture selection tied to BOE-00-01; cold/warm baseline receipts; no fabricated language lane. | todo |
| BOE-10-02 | P1 | Prototype Turborepo only for eligible JS/TS package tasks; verify package/workspace prerequisites and cache invalidation. | Turbo adapter report; exact commands and lockfile; no root-wide adoption assumption. | todo |
| BOE-10-03 | P1 | Prototype Nx project graph/affected-task detection and task caching against the same eligible workload set. | Nx adapter report; plugin/configuration footprint; correctness compared with baseline. | todo |
| BOE-10-04 | P1 | Prototype Moonrepo as the primary polyglot candidate, including language/toolchain support and task graph semantics. | Moon report; Termux install/runtime feasibility; equivalent workload results. | todo |
| BOE-10-05 | P2 | Assess Bazel as a bounded reference candidate, not a default deployment target; quantify hermeticity and operational overhead. | Written go/no-go with reproducibility and maintenance evidence. | todo |
| BOE-20-01 | P1 | Implement a read-only evaluator that maps the canonical project/task registry to candidate adapters and produces comparable run receipts. | Deterministic output; no dispatch or writes; fixtures and negative tests pass. | todo |
| BOE-20-02 | P1 | Integrate evaluation receipts with existing DOE/MVT and action-effectiveness evidence, preserving observed-vs-planned cadence and retention rules. | Crosswalk to existing schemas; deduplication/idempotency tests; no telemetry deletion. | todo |
| BOE-20-03 | P1 | Define GitHub Actions orchestration boundaries: validation, evaluation, and optional execution remain separate jobs/workflows with least privilege. | Workflow threat review; permissions matrix; no implicit workflow-token chaining. | todo |
| BOE-30-01 | P1 | Validate Termux/Android execution parity and define portable fallback behavior for unavailable runtimes. | Device evidence where available; otherwise explicitly marked unverified; smoke gates remain authoritative. | todo |
| BOE-30-02 | P1 | Compare cost, latency, cache hit/miss correctness, invalidation, maintenance burden, and agent-context overhead; issue evidence-backed selection ADR. | Decision matrix with uncertainty, rejected alternatives, and rollback plan. | todo |
| BOE-40-01 | P1 | Implement only the selected adapter(s) and minimal canonical registry integration after review and acceptance. | Approved ADR; independent review; all relevant gates green on immutable SHA. | blocked |
| BOE-40-02 | P1 | Add operator runbook, migration/rollback, cache hygiene, secret handling, and stale-evidence reconciliation. | Dry-run runbook; rollback tested; docs and CI contract aligned. | blocked |

## Dependency order

`BOE-00-01` → `BOE-00-02` → `BOE-10-01` → `BOE-10-02/03/04` (+ bounded `BOE-10-05`) → `BOE-20-01/02/03` → `BOE-30-01/02` → review/ADR → `BOE-40-01/02`.

The candidate prototypes are parallelizable only after the same fixture set and contract are pinned. No candidate may change shared workflow files during the evaluation phase.
