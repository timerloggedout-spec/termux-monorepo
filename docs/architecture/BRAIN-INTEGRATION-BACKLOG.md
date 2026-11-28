# Brain Integration Backlog

**Status:** evidence-backed planning baseline  
**Baseline:** Root Brain README on `master`; subsystem and ownership maps on `feat/root-brain-rust-core-final`.  
**Rule:** reuse existing owners, ship read-only adapters first, and preserve the existing execution and authority control planes.

## Decision summary

- **Shared reasoning kernel:** present as the `termux-brain` Rust crate facade over the root `brain.rs` source.
- **Specialist packages:** one source-visible package, `mosaic-brain`, under `archwiz/mosaic_brain/`.
- **Additional specialist count:** architecture sources define no fixed target. Admit a specialist only when a domain owner, typed contract, independent validation criteria, and integration need are documented. The 21 subsystem families are a capability taxonomy, not a count of specialist brains.
- **MOSAIC production integration:** typed contract and pure adapter exist; production host invocation route and host ownership remain unverified/unwired.
- **Execution authority:** QUE/admission, hub_mcp policy, dispatch, execution, verification, and memory owners retain authority.

## Delivery backlog

| ID | Priority | Workstream | Canonical owner / source | Dependency | Acceptance evidence | State |
|---|---|---|---|---|---|---|
| BRN-001 | P0 | Pin ownership contracts and identity chain | `docs/architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md` (proposal branch); `docs/ops/ORCHESTRATION-CONTRACTS.md` | Verify the map against current `master` paths and versioned contracts | Every adapter target has an owner, pinned source path/revision, contract version, and explicit unknowns; orchestration, cycle, attempt, task, participant, correlation, and evidence IDs remain traceable | In progress |
| BRN-002 | P1 | Harden shared Rust kernel | `brain/` facade and root `brain.rs`; kernel owns typed reasoning only | BRN-001 | `cargo fmt --check`, `cargo check --all-targets`, `cargo test`, and `cargo clippy --all-targets -- -D warnings` pass; deterministic stage and fail-closed contract tests cover invalid identity/domain/version and policy adapter errors | Kernel present; validation to rerun on current HEAD |
| BRN-003 | P1 | Verify MOSAIC specialist contract and host seam | `archwiz/mosaic_brain/`; host owner TBD | BRN-001, BRN-002 | Specialist contract/version, domain identity, evidence references, and advisory-only outcomes tested; host invocation owner and bridge contract documented; production route remains disabled until host integration tests pass | Package present; host route unwired |
| BRN-004 | P2 | Read-only context and knowledge adapters | ICM objects; CRG `build_index.py`, `query.py`, `temporal.py`; context cache owner | BRN-001, BRN-002 | Typed adapters return source refs, provenance, revision/time freshness, sensitivity, and bounded payloads; tests cover stale data, missing sources, unknown sensitivity, conflicting authority, and budget limits; adapters perform zero writes | Proposed |
| BRN-005 | P2 | Research evidence adapter | refTemplates source map and research dossier owners | BRN-001, BRN-004 | Each result preserves citation/source identity, retrieval timestamp, evidence class, and confidence; references remain evidence rather than dependency or authority; fixture tests cover stale, duplicate, and unqualified sources | Proposed |
| BRN-006 | P3 | Capability discovery projection | hub_mcp capability policy; provider catalog protocols and model evidence; workflow/skill registries | BRN-001, BRN-004 | Read-only capability records expose stable ID, owner, source path, schema/version, status, evidence refs, dependencies, security classification, freshness, and tests; catalog presence never implies entitlement or authorization | Proposed |
| BRN-007 | P4 | QUE/QDesk shadow handoff | QUE/QDesk intake and lifecycle; `project_task.py`; `dispatch_admission.js`; `dispatch_executor.py` | BRN-001, BRN-004, BRN-006 | Brain emits proposal only; stable idempotency/correlation IDs survive request and receipt; integration tests prove zero queue mutation, claim/lease operation, dispatch, workflow launch, or device execution | Proposed; owner contracts require verification |
| BRN-008 | P4 | Verification and evidence binding | Existing validators, normalized receipts, evidence-led ops | BRN-001, BRN-007 | Outcomes classify as TASK_PASS / TASK_FAIL / TASK_UNKNOWN independently of workflow conclusion; every claim binds to an authoritative receipt and source revision; missing evidence resolves to UNKNOWN | Proposed |
| BRN-009 | P5 | Authorized vertical slice | QUE admission → dispatch executor → existing execution → authoritative verifier | BRN-007, BRN-008; explicit owner authorization | End-to-end test demonstrates existing admission and policy checks, bounded execution, idempotent retries, verified task outcome, audit trail, and stop/revoke behavior; Brain itself never bypasses owners | Blocked on verified contracts and explicit authorization |
| BRN-010 | P6 | Governed learning candidates | Delphi, DoE, memory/evidence owners | BRN-008, BRN-009 | Candidate generation links baseline, experiment, held-out evidence, and independent review; memory owner alone persists; no autonomous promotion from reflection | Proposed |
| BRN-011 | P7 | Owner cockpit and runtime observability | ArchWiz / Tribute / QDesk projections; telemetry owner | BRN-001, BRN-007, BRN-008 | Dashboard distinguishes CI health from runtime metrics; traces show stage latency, provider/cost data where authorized, intervention, degradation, and evidence lineage; pause/revoke controls call existing owner APIs | CI dashboard present; runtime instrumentation unverified |
| BRN-012 | P8 | Bounded autonomy evaluation | Existing policy, admission, execution, and rollback owners | BRN-009, BRN-010, BRN-011 | Explicit action allowlist, budgets, stop conditions, rollback drills, independent verification, and owner revocation tests pass before any autonomy expansion | Future gate |

## First implementation slice

1. Complete BRN-001 by reconciling the proposed ownership map with current `master` paths and pinning the actual contracts.
2. Run BRN-002 validation and capture command output against the current commit.
3. Complete BRN-004 with a single read-only CRG/ICM vertical slice. Preserve provenance, freshness, sensitivity, and source references end-to-end.
4. Add BRN-006 only after the read adapter contract is stable; consume existing capability and provider catalogs as evidence.
5. Implement BRN-007 as a shadow proposal/receipt path with tests proving canonical QUE state remains unchanged.

## Specialist admission gate

A new specialist package enters the implementation plan only when all conditions hold:

- A named domain owner accepts responsibility for the domain contract and lifecycle.
- A domain-specific task boundary exists that the shared kernel and current specialists do not already cover.
- Input/output schemas, contract versioning, evidence requirements, and failure semantics are defined.
- Independent domain validation and regression fixtures exist.
- The host integration path and authority boundary are documented.
- The package provides measurable value without duplicating an existing owner.

This gate keeps the current specialist count evidence-based and prevents turning the 21-family taxonomy into an arbitrary 21-agent build target.

## Source records

- [Root Brain README](../../brain/README.md)
- [MOSAIC specialist package](../../archwiz/mosaic_brain/)
- [Subsystem taxonomy proposal](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md)
- [Ownership and integration map proposal](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md)
- [Brain architecture RFP #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501)
