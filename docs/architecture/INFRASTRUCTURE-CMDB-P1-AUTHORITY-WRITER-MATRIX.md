# Infrastructure CMDB — P1 Authority, Writer & Reconciliation Matrix

**Status:** evidence-backed design work product; partial semantic review, not a complete CMDB  
**Parent:** [Infrastructure Registry Design](INFRASTRUCTURE-REGISTRY-DESIGN.md)  
**P0 baseline:** [Inventory baseline](INFRASTRUCTURE-CMDB-P0-INVENTORY.md)  
**Scope:** source authority by fact/field, write surfaces, conflict candidates, and reconciliation finding ownership  
**Safety:** read-only mapping only. No secret values, provider mutations, new poller, automatic remediation, or parallel event ledger.

## 1. Confidence and evidence vocabulary

- **Confirmed contract** — directly established by a source file/schema/workflow inspected for this matrix.
- **Candidate overlap** — two or more surfaces appear to touch the same logical resource; collision is not confirmed until scope, writes and execution evidence align.
- **Inferred relationship** — plausible from names or references but not directly declared.
- **Unknown / not inspected** — evidence does not yet establish an answer. This is not equivalent to absent or broken.
- **Configured** is not **observed**; **observed** is not necessarily **healthy**; **catalogued** is not **entitled**; **credential referenced** is not **credential valid**.

This matrix records only the field classes and writer candidates supported by the inspected sources. It intentionally does not claim a full census of every workflow or runtime.

## 2. Authority matrix (field-level)

| Entity / fact class | Preferred authority for that field | Consumers / derived views | Write or observation mechanism | Confidence and guardrail |
|---|---|---|---|---|
| Repository identity and tracked path state | GitHub repository + immutable commit/tree SHA | Inventory manifest; repository observatory | Git tree API / Git | **Confirmed contract.** A path snapshot is not a live-service inventory. Bind every census to a ref and SHA. |
| Workflow definition, triggers, permissions, concurrency, configured writer behavior | Workflow YAML at the inspected commit | Workflow catalog; ownership candidate matrix | Git commit changes; workflow execution is separate evidence | **Confirmed contract.** YAML establishes configured intent, not that a run executed or succeeded. |
| Workflow execution outcome | GitHub Actions run/job/artifact at a concrete run ID and commit SHA | Evidence projection; health/reconciliation view | Actions execution and retained artifacts | **Confirmed contract.** Capture run ID, attempt, commit SHA, observed time, status and artifact/source ref. A skipped/cancelled run is not success. |
| Quota service identity, metric, documented limit/window/reset, planned-use metadata | ops/quota/registry.json | Quota docs; routing/dispatch consumers | Reviewed source change | **Confirmed contract.** Registry rules explicitly say documented limits are entitlements, never balances; live poller output is a workflow artifact, not a committed record. |
| Passive quota signal support by provider family | ops/quota/provider-managers.json | Passive parser/observation workflows | Reviewed registry change; any actual read must be independently evidenced | **Confirmed contract.** File describes an offline registry, not a poller, account validation, entitlement assertion or admission input. |
| Current quota reading / provider reachability | Specific probe/poller response and run artifact, scoped to provider/account/metric/time | Private operational view; evidence projection | Existing observation workflow/poller | **Confirmed boundary; live values not inspected here.** Never synthesize missing counters or treat documentation as a reading. |
| Provider/model capability contract | docs/schemas/provider-capabilities.md and llm_api_hub/schemas/provider-capabilities.md, with provider-specific catalog/manifest as appropriate | Routing and provider batch consumers | Reviewed manifest/schema change; runtime tests separately | **Partial authority.** Catalog membership does not prove entitlement, reachability, or successful inference. Preserve distinctions between these signals. |
| Routing/orchestration design | docs/ops/ROUTING-ORCHESTRATION-MAP.md and related routing contracts | Cockpit graph / dependency projection | Reviewed docs/config/code changes | **Contract/documentation authority only.** The CMDB must not become a routing authority or change route selection. |
| Credential/variable names and intended consumer surfaces | docs/ops/secrets-and-variables-registry.md, docs/ops/CREDENTIAL-INVENTORY.md, data/ops/credential-surfaces.jsonl, workflow secrets.* / vars.* references | Private inventory projection; owner/writer candidate matrix | Reviewed docs/config/workflow changes; GitHub secret/variable APIs are separate observations | **Confirmed contract.** Registry says it is the source of truth for repository configuration names, but is inventory-derived and not exhaustive of values. Never ingest or expose values. |
| Credential presence / authentication / rotation | Presence: phantom-secrets audit's provisioned-names snapshot (live Actions API inventory fetched by the phantom-secrets-audit workflow, PR #1636). Backing family / authentication: purpose-built probe receipts (e.g. the credential-family probe, PR #1646) or an owner ruling, each with scope and timestamp | Private health/evidence view | Existing audit workflow (weekly + dispatch) for presence; operator-run probe for family/authentication | **Confirmed for presence (names only).** Authentication and backing family remain per-probe facts. Name occurrence alone proves only a declared reference. No low-entropy secret hashes. |
| Resource identity / research provenance / decision status | Existing source family appropriate to the lane: docs/research/resource-registry.yaml, FOSS procurement registry, model-selection market registry, repository observatory | Research/procurement cockpit | Reviewed resource-record update | **Confirmed separation.** A research candidate is not an installed dependency; preserve canonical source, version/commit, evidence and decision status. |
| Repository observatory record contract | docs/repositories/repository-observatory.schema.json | Generated repository index | Observatory builder and its receipt | **Confirmed schema.** The schema requires observed time, snapshot hash and provenance/classification fields. The generated index is a projection, not authority over GitHub. |
| Integration / app census state | integration-mesh-poll workflow artifacts (Actions cache/artifacts; state is never committed) + docs/ops/INTEGRATION-MESH-MATRIX.md as the snapshot document | Inventory / cockpit views | Scheduled poll (every 6h) + workflow_dispatch | **Confirmed mechanism.** Account-level installation totals are NOT ESTABLISHED via the PAT API (the installations list is PAT-inaccessible); record them as not established, never copied forward from dated pastes such as Issue #184's 2026-08-13 snapshot. |
| Adapter operation status and evidence label | ops/web_adapter_foundry/registry.schema.json plus ops/web_adapter_foundry/catalog.json and implementation | Foundry campaign / browser-lane import views | Reviewed catalog/schema/runtime changes; proof artifacts separately | **Confirmed schema boundary.** Status (discovered → stable/degraded) and evidence label (observed/inferred/reproduced/contradicted/unknown) are distinct. Do not infer upstream installation from catalog membership. |
| Relationship scope/exclusions | config/context_relationships/scope_registry.json | Context relationship index and audit workflows | Reviewed scope-registry changes; audit/backfill/reconcile workflows | **Confirmed contract.** Respect excluded session/browser/credential paths and max-file-size policy. Reuse existing relationship IDs and scope policy rather than creating a competing graph. |
| Reconciliation experiment evidence | docs/ops/EVIDENCE-ENVELOPE.schema.json | Production evidence ledger, MVT/DOE, recovery/review projections | Producers emitting SHA-bound evidence envelopes | **Confirmed schema.** Required fields include experiment/source/source ID, commit and baseline SHAs, observed time, status, outcome, provenance and confidence. Reuse it; do not introduce a second generic event envelope. |
| Git ref drift classification | .github/workflows/reconciliation-engine.yml | Reconciliation summary / operator cockpit | Workflow-dispatch observer, with dynamic target/base refs | **Confirmed workflow contract.** Observer-only; no candidate checkout/execution or ref mutation. It records immutable SHAs, merge-base, ahead/behind, changed-path count and stops on divergence/behind. |
| Reconciliation finding history and disposition | Existing finding-class-specific workflow, ledger and owner; map via reconciliation index and producer artifacts | Unified derived cockpit view | Existing finding producer + explicit disposition action | **Partially mapped.** Do not add a shared drift ledger until each finding class's current writer, state store, history/retention and disposition owner are mapped. |
| Service health and SLO target | Actual service-specific SLO/measurement contract and observation source | Health view | Existing probe/telemetry/incident workflow | **Gap to verify.** Workflow existence or a green CI badge is not an SLO. No canonical all-service SLO registry was established by this pass. |
| Skills presence, upstream provenance and pin | Actual tracked SKILL.md, skills-lock.json, .gitmodules, and relevant inventory docs | Skills inventory / agent cockpit | Reviewed file or pin update; runtime activation requires separate evidence | **Partially mapped.** A skill file in Git does not prove enabled/loaded; same-name skills in separate surfaces need not share authority. |

## 3. Writer and resource ownership candidates

These rows are deliberately conservative. A workflow that reads or references a resource is not automatically a writer. Confirmed writer claims require an explicit write operation or destination in the workflow/script plus matching scope; concurrent schedules alone are not a conflict.

| Resource / state | Known source or writer candidate | Potential overlap | Evidence required before declaring collision | Current classification |
|---|---|---|---|---|
| Quota registry metadata | ops/quota/registry.json (reviewed Git data) | Poller artifacts and quota dispatch outputs may carry observations about the same service | Compare destination/path, producer code, artifact names, schedule and schema; distinguish config from observed balance | **No collision established.** Registry says live poller output is an artifact, not a commit. |
| Provider quota observation | ops/quota/provider-managers.json defines passive parsing capabilities; quota poller/workflows are separate | Provider-specific availability probes may overlap in provider/model coverage | Identify exact signal, account scope, source response, writer destination and freshness policy | **Candidate overlap.** This registry is not itself a poller or admission input. |
| GitHub secret/variable names | Secrets-and-variables registry + credential inventory + JSONL surfaces + workflow references | Multiple catalogs may describe the same name or consumer | Normalize name/class/scope, compare inventory provenance and current workflow references; never compare values | **Catalog overlap expected; not a write collision.** Choose one canonical names registry, keep other sources as evidence/consumer maps. |
| Repository/skill catalog | Skills inventory, actual skill files, locks/submodules, external proposals | Inventory can drift from tracked files or external pins | Compare path-derived entrypoints with catalog rows and exact upstream refs; inspect any generator/writer | **Drift candidate.** No evidence yet of two active writers. |
| Repository observatory / research resources | Repository observatory and several lane-specific resource registries | Same upstream project can appear as a candidate in multiple research lanes | Compare canonical URL, upstream ID, version/commit, lane purpose and primary placement; retain facets/cross-membership instead of duplicate identity | **Semantic overlap likely; not infrastructure duplication.** |
| Reverse-engineering toolkit | Foundry catalog + registry schema/runtime + browser-lane import list | Candidate appears in both Foundry and browser-lane lists | Compare canonical upstream URL and import state; preserve one primary placement and explicit cross-membership facets | **Known taxonomy overlap to reconcile.** Current GitHub state re-check confirms PR #1550 and PR #1551 are closed and merged. Preserve one primary placement plus explicit cross-membership facets. |
| Context relationship graph | Scope registry + relationship index/evidence matrix + audit/backfill/reconcile/publish workflows | Generated graph/index may be mistaken for authority or multiple jobs may publish derived outputs | Map each workflow's output path, permissions, schedule, concurrency, commit/publish step and evidence contract | **Writer ownership not yet proven.** Reuse existing relationship IDs/scope policy; generated edges must retain provenance. |
| GitHub/GitLab governed reconciliation | Reconciliation engine + GitHub/GitLab governed reconciliation workflows + production evidence ledger | Multiple finding classes or providers may emit records about related PR/ref states | Map output schema, destination, dedupe key, retention/history, disposition owner and idempotency behavior | **Separate scopes presumed until proven otherwise.** Do not merge ledgers just because both say “reconciliation.” |
| Deployment and health observations | Provider availability, deployment-health lane, incident/health workflows | Same service may have CI, endpoint, credential and end-to-end signals | Normalize signal type, environment, observation window, source run/receipt and SLO; compare only like-for-like signals | **Multiple signals are intentional.** No single “healthy” boolean should overwrite distinct evidence. |
| AntigravityCLI / external awesome-list intake | Issue/PR research proposals and resource registry entries | External candidate references may be mistaken for installed, pinned or approved integrations | Verify current issue/PR state, exact upstream ref, license/trust review, imported paths, owner and update mechanism | **Research-only unless installation/pin evidence exists.** Current state check: issue #1497 is the AntigravityCLI research/provisioning proposal; PR #1514 remains open and unmerged (base master-staging); PR #1612 remains open, draft and unmerged. Proposal or PR draft is not deployment proof. The referenced issue/PR text is not enough to establish an installed integration or active runtime. |

### Writer-collision acceptance rule

A **confirmed writer conflict** requires all of the following:
1. Same normalized resource or state key, including environment/account scope.
2. At least two independent write-capable mechanisms (not merely readers/catalogs).
3. Evidence of overlapping write windows or incompatible desired values/ownership.
4. Source refs, workflow/script locations, and run/event IDs sufficient to reproduce the claim.

If one of these is absent, classify as **candidate**, **inferred**, or **unknown** and state the missing evidence. Never auto-resolve by picking the latest timestamp without an authority and conflict policy.

## 4. Existing reconciliation producers and evidence contracts

| Producer / surface | What it can establish | What it cannot establish by itself | Registry integration rule |
|---|---|---|---|
| `.github/workflows/reconciliation-engine.yml` | Ref resolution, immutable target/base SHAs, merge-base, ahead/behind, changed paths and graph state | Runtime health, provider readiness, or authority for external service state | **Observer-only, read-only permissions.** No candidate checkout/execution or ref mutation. Capture run ID, attempt, source SHA and summary; preserve STOP state for divergence/behind. |
| `.github/workflows/agent-mvt-experiment.yml` | Experiment-specific validation outcomes if run receipts exist | General production health outside its measured cohort | Reuse experiment ID, candidate/baseline SHA, outcome and provenance. |
| `.github/workflows/pr-production-ledger.yml` | SHA-bound PR production telemetry in GitHub workflow summaries/comments for its declared scope | All resource ownership or every reconciliation finding class; not runtime service health | **Read-only control-plane telemetry.** Reacts to PR/review/comment events, uses status-aware API retries, and does not check out or execute PR code. Before joining a shared findings view, extract its exact emitted summary/comment schema, dedupe key and retention policy from the full workflow. |
| `.github/workflows/context-relationship-reconcile.yml` | Rebuilds the bounded relationship history window from canonical `master`; writes `workspace/llm_map/context_relationships/` and commits/pushes deltas to `master` | Universal infrastructure dependency truth; generated graph is not authority for service health or configuration values | **Confirmed master writer.** Concurrency group `context-relationship-writer-master`, `cancel-in-progress: false`. Runs a `--full-refresh` and commits only if generated paths differ. |
| `.github/workflows/context-relationship-backfill.yml` | Resumable page-bounded history backfill; reads canonical manifest and writes the same `workspace/llm_map/context_relationships/` destination on `master` | Completeness beyond reported page window; pagination exhaustion alone does not establish promotion eligibility | **Confirmed second master writer, serialized with reconcile** by the same `context-relationship-writer-master` group and `cancel-in-progress: false`. Push-to-master path triggers can wake bounded continuation. Validate checkpoint, page bounds and temporal lineage before accepting output. |
| `.github/workflows/context-relationship-publish.yml` | Builds relationship index from `master-staging` and pushes generated artifacts to `master-staging` | Canonical production state on `master`; staging output is not promoted merely because it exists | **Separate staging writer** using `context-relationship-writer-master-staging`. Treat as staging evidence only; no master promotion is implied. |
| `.github/workflows/context-relationship-backfill-watcher.yml` and `context-relationship-validate.yml` | Watcher captures run/job/artifact observations; validation runs schema/collector/lineage checks | Neither is a canonical graph writer; watcher evidence is not the graph itself | **Read-only observers/validators.** Keep run ID/attempt/head SHA separate from generated corpus state. |
| `.github/workflows/gitlab-governed-reconciliation.yml` and `docs/ops/GITHUB-GITLAB-GOVERNED-RECONCILIATION.md` | Governed GitHub/GitLab cross-platform findings in declared scope | A universal replacement for platform-native source records | Preserve platform identity, ref/SHA, finding class and disposition provenance. |
| `docs/ops/EVIDENCE-ENVELOPE.schema.json` | Shared structure for SHA-bound evidence records | Evidence truth without a producer, source reference and actual payload | Prefer the existing envelope; validate required fields and enum values at producer boundaries. |
| `.github/workflows/phantom-secrets-audit.yml` + `scripts/secrets_audit/` | Live Actions provisioned-name inventory; classifies workflow `secrets.*` references; uploads `phantom-secrets-report` for 30 days; opens remediation PRs for mechanical case-variant/dead-branch fixes; regenerates `docs/ops/PHANTOM-SECRET-REMEDIATION.md`; posts names-only report to issue #184 | Credential validity, authentication success, or anything about values; a provisioning checklist does not prove a credential exists | **Confirmed multi-surface writer** with workflow concurrency `phantom-secrets-audit`: report artifact, remediation branches/PRs, generated remediation doc, and issue comment. Scan fails closed if provisioned inventory cannot be read. Consume the generated report/classifications; never hand-maintain a parallel phantom list. |
| `.github/workflows/reviewer-metrics-collect.yml` | Reviewer delivery observations per provider × context; ECC findings counts | Code quality, approval, or merge readiness | Consume `docs/ops/generated/reviewer-metrics.json` as a derived projection republished via refresh PRs; never edit the map by hand. |
| `.github/workflows/integration-mesh-poll.yml` + `scripts/github/integration_mesh_poll.py` | Six-hour census/diff; retains prior snapshot in Actions cache and uploads per-run snapshot artifact for 30 days; posts material diffs to issue #1505 and opens/updates a labeled `mesh-refresh` issue for structural changes (or accumulated figure-only changes) | Account-level installation totals the PAT API cannot establish; committed state or a permanent service inventory | **Confirmed external-state writer, not repository-file writer.** Permissions are `contents: read`, `issues: write`; poll output is never committed. Treat issue comments/refresh issues as finding surfaces and cache/artifact as observation state. |

**Unresolved before a unified findings view:** exact output schema and dedupe keys for every producer, retention/compaction and terminal disposition vocabulary, operator/automation ownership, and the full reviewer-metrics refresh write path. Do not invent a global writer or merge findings with different scopes.

## 5. Secret-safe configuration inventory

The CMDB may hold only metadata needed to locate and govern a credential reference:

- credential_ref_id (stable ID derived from repository + secret/variable name; do not hash the value)
- name (configuration name, if the projection's access policy allows it)
- class (secret / variable / built_in / unknown)
- name_semantics (issuer_named / route_named / unknown — a name may encode the consumer route rather than the issuer; fleet ruling 2026-10-24)
- backing_family (the verified issuer family, where a probe or owner ruling establishes it; otherwise unknown)
- declared_consumers (workflow/script IDs, each with a source ref)
- scope (repository/environment/org where verified; otherwise unknown)
- owner and rotation_policy_ref (only if documented)
- presence_state (declared, present, absent, inaccessible, unknown)
- validation_state (not_checked, authenticated, rejected, expired, unknown)
- observed_at, source_ref, evidence_ref, fresh_until where applicable

Never store values, masked values, token prefixes/suffixes, cookies, private keys, authorization headers, low-entropy hashes, or diagnostic payloads that may echo credentials. A successful request validates only the exact credential, scope, endpoint and time covered by that probe. A name in a registry does not prove that the secret currently exists.

## 6. Health and SLO normalization

Do not collapse different health signals into one boolean. Each observation should name:
- subject_id, environment, signal, measurement_method
- result and unit/structured value
- observed_at, optional window_start / window_end, fresh_until
- source_id, source_ref, run/attempt or telemetry query reference
- state_class (configured, documented, observed, derived, asserted)
- confidence, known exclusions, and failure/unknown reason

At minimum keep these signals separate:
1. configuration parses/validates;
2. provider catalog/model is listed;
3. credential reference is present;
4. authenticated endpoint is reachable;
5. a bounded capability request succeeds;
6. an end-to-end service path succeeds;
7. SLO target is met over its defined measurement window;
8. incident state and last-known-good observation.

A missing, stale, skipped, cancelled, blocked, or inaccessible observation is **unknown/stale/blocked**, not healthy. SLO records need a named service owner, SLI formula, target, measurement window, exclusions, alert policy and source. This matrix does not claim those contracts are already present for every service.

## 7. Next implementation gate

The next bounded implementation slice should be schema + fixtures only, after source-owner review:

1. Normalize a small, reviewed cohort (quota registry, provider quota-manager registry, credential-name inventory, repository observatory schema, Foundry operation schema, relationship scope registry, evidence envelope, and the phantom-secrets audit's provisioned-names snapshot — names-only, already produced by the existing audit workflow, and the cohort's only live-observation source).
2. Build fixtures for configured-vs-observed, stale-vs-fresh, candidate-vs-confirmed conflict, missing-vs-inaccessible credential, and superseded evidence.
3. Validate identity uniqueness, relationship endpoints, source references, timestamps, allowed state classes, and public/private projection rules.
4. Run deterministic tests offline; no network probe or secret access in unit tests.
5. Keep the schema as a derived projection contract; do not add a database, scheduler, poller, event store or remediation executor in this slice.
6. Require review from existing source owners and validate on the exact current PR head before promoting P0/P1 status.

## 8. Evidence still required

- Complete read of remaining writer-capable workflow/script bodies and their output destinations, especially the PR production ledger's exact emitted schema and the generated reviewer-metrics refresh path.
- Current issue/PR state for AntigravityCLI, awesome-list intake and external skill pinning.
- Skill inventory reconciliation against actual entrypoints and pin files.
- Per-producer reconciliation output schema, state store, retention and disposition owner. Inspected context-relationship workflows establish two serialized master writers (reconcile + backfill), a separate staging writer, and read-only watcher/validator; no cross-branch promotion is implied. Integration-mesh is cache/artifact + issue based; phantom-secrets audit is artifact + remediation PR/doc + issue-comment based.
- Service-by-service SLO/SLI contracts and actual observation receipts.
- A refreshed path manifest when the base ref advances beyond the recorded census SHA.

Until these are completed, this matrix is a source-backed working model, not a production CMDB or proof of comprehensive inventory.
