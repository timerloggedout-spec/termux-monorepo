# Infrastructure CMDB — P0 Inventory Baseline

**Status:** initial tracked-path census; not an exhaustive semantic inventory  
**Design parent:** [Infrastructure Registry Design](INFRASTRUCTURE-REGISTRY-DESIGN.md)  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Ref inspected:** `master`  
**Git tree SHA:** `b8adaa2e05f3ebc246e90945d199fd1b9c0c15da`  
**Census result:** 9,738 recursive tree entries, 8,785 tracked blob paths, tree API reported `truncated=false`.  
**Method:** GitHub recursive Git tree API plus focused reads of the source documents listed below. Counts are path-pattern counts from this snapshot, not counts of unique live services or semantic entities.

## 1. What the census confirms

| Surface | Snapshot count / evidence | Interpretation and boundary |
|---|---:|---|
| `.agents/skills/*/SKILL.md` | 27 skill entrypoints | First-party agent skill surface; must be reconciled with the skills inventory and any upstream pins |
| `.github/skills/*/SKILL.md` | 10 skill entrypoints | Workflow/automation skill surface; not assumed interchangeable with `.agents/skills` |
| `.github/workflows/*` | 185 paths | Workflow definitions; workflow YAML is configured intent, not evidence that a run succeeded |
| `ops/quota/*` | 3 paths | Quota registry and poller family; read-only vendor posture is documented |
| `ops/web_adapter_foundry/*` | 12 paths | Foundry runtime, catalog, schema, examples, and proof artifacts |
| Paths containing `context-relationship` or `context_relationship` | 169 | Broad relationship graph, index, workflow, schema, test, and evidence surface; path count includes different kinds of assets |
| Paths matching `registry` in the filename/path | 34 | Registry-named assets only; does not include all catalogs or implicit registries |
| Paths matching `reconcil` or `drift` | 34 | Narrow filename heuristic; a broader `recon` match returns 490 and includes unrelated/reconstructed/session assets |
| Paths matching `credential` or `secret` | 24 | Name-based subset; secret/config references also exist in workflows and other documents |
| Paths containing `approxination` | 7 | Skill, cohort, and integration proposal surfaces are tracked |
| Paths matching Foundry, reverse-engineering, or browser-lane import names | 18 | Foundry/campaign/import surface; overlapping taxonomies must be reconciled, not duplicated |
| Paths containing `resource-registry` | 5 | Research/resource registry family; not automatically the canonical service CMDB |

These counts are reproducible only against the recorded tree SHA. They should be regenerated when the baseline ref changes.

## 2. Field-level source-of-truth map (initial)

“Authority” is scoped to the fact class in the row. A document that describes a contract is not automatically authoritative for runtime state. Freshness, observation, and ownership must remain separate dimensions.

| Fact class / capability | Existing source to consult first | Authority boundary | Known integration / gap to verify |
|---|---|---|---|
| Skills inventory and primary agent entrypoints | `docs/ops/SKILLS-INVENTORY.md`, `CLAUDE.md`, `SKILLS.md`, actual `.agents/skills/**/SKILL.md` and `.github/skills/**/SKILL.md` | Inventory doc is a catalog; tracked files and explicit upstream/pin metadata establish what is present in this ref | Reconcile inventory rows, entrypoint counts, duplicate names, version/pin state, tests, and source/upstream provenance |
| Approxination lane | `.agents/skills/approxination-lane/SKILL.md`, `docs/ops/APPROXINATION-LANE.md`, `docs/evaluations/approxination/COHORT.md`, `docs/proposals/active/approxination-integration/**` | Lane doc says skill + cohort are live; gitlink pin is optional backlog (APPROX-005) | Verify exact source/pin and cohort evidence; do not claim external benchmark is vendored |
| Antigravity research / provisioning | Issue [#1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497) and any associated PRs/source references | Issue title is “AntiGravityCLI Use Cases && Initial Provisioning Proposal & initial {seed}Research”; proposal text alone is not proof of deployed integration | The master tree has no path with “antigravity” or “anti-gravity” in its name. This is a filename-only result, not proof of no references or implementation. Search issue/PR history and upstream links before classifying |
| Service and dependency catalog | `docs/ops/ROUTING-ORCHESTRATION-MAP.md`, `docs/schemas/provider-capabilities.md`, `llm_api_hub/schemas/provider-capabilities.md`, provider manifests, `ops/quota/registry.json`, workflow/config files | Routing map and provider capability doc define partial contracts; provider/workflow manifests define configured state; successful runs and probes are separate observations | Establish one stable ID per entity and typed relationships; map each field to its owning source and scope |
| Quota and provider availability | `ops/quota/registry.json`, `docs/ops/QUOTA-REGISTRY.md`, `ops/quota/provider-managers.json`, `.github/workflows/provider-availability.yml`, `.github/workflows/provider-batch.yml` | Registry is configured metadata; poller/run output is time-bound observation, not permanent truth | Preserve observation time, provider/scope, poll outcome, freshness and provenance; distinguish provider reachability from capability success |
| Credential names and secret/config references | `docs/ops/secrets-and-variables-registry.md`, `docs/ops/CREDENTIAL-INVENTORY.md`, `data/ops/credential-surfaces.jsonl`, `docs/ops/SECRET-NAMING-CONVENTION.md`, workflow secret references | Registry documents names/owner surfaces, not secret values or proof of live validity | Join consumers and scopes without copying values; separate declared reference, presence observation, authentication verification, rotation evidence and unknown/inaccessible |
| Integration and ownership landscape | `docs/ops/INTEGRATION-MESH-MATRIX.md`, repository/project manifests, workflow writers/concurrency settings, `docs/ops/DEVICE-PULL-QUEUE.md`, `ops/devices/registry.json` | Mesh/campaign documents are catalogs and may age; provider APIs, actual workflow configuration, and current run evidence have different authority | Build owner/writer/resource claims with evidence; detect candidates first, label confirmed collisions only with sufficient evidence |
| Reconciliation and drift | `docs/ops/RECONCILIATION-CONTROL-PLANE.md`, `docs/ops/RECONCILIATION-CONTROL-PLANE-INDEX.md`, `docs/ops/GITHUB-GITLAB-GOVERNED-RECONCILIATION.md`, `.github/workflows/reconciliation-engine.yml`, `.github/workflows/context-relationship-reconcile.yml`, `.github/workflows/gitlab-governed-reconciliation.yml` | Existing workflows/ledgers own their declared finding classes; do not create a second ledger until ownership and event/history contracts are checked | Map finding type → current writer/ledger → evidence receipt → owner/disposition; preserve source refs and run IDs |
| Evidence and provenance | `docs/ops/EVIDENCE-PROJECTION-SURFACE.md`, `docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md`, `.github/skills/evidence-provenance/SKILL.md`, `.github/skills/evidence-envelope/SKILL.md` | Evidence envelope and projection contracts describe evidence shape; individual receipts/runs provide actual observations | Every derived claim needs input refs, version/time, transformation, and reproducible output |
| Web reverse-engineering / adapter toolkit | `docs/ops/WEB-ADAPTER-FOUNDRY.md`, `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md`, `ops/web_adapter_foundry/catalog.json`, `ops/web_adapter_foundry/registry.schema.json`, `.agents/skills/web-adapter-foundry/SKILL.md`, `docs/repositories/browser-lane-imports.json` | Foundry catalog describes composed upstream projects; registry schema and runtime define the local operation contract; browser imports are candidate/import tracking | Preserve single-primary-placement plus cross-membership facets; upstream projects are composed, not silently vendored; candidate claims need independent evidence |
| Research resource catalog | `docs/research/resource-registry.yaml`, `docs/research/resource-registry.example.json`, `data/foresight/resource-registry.jsonl`, `data/model-selection-market/resource-registry.json`, `docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json` | These are research/procurement resources, not automatically production infrastructure inventory | Use canonical source + version, evidence status, horizon and decision status; do not conflate a research candidate with an installed dependency |
| Repository inventory / observatory | `docs/repositories/repository-observatory.schema.json`, related repository index/observatory workflows | Schema defines record contract; generated index is a projection whose generation receipt/freshness must be checked | Link external repo identity, pin/ref, import status, license/trust review, owner and update mechanism |
| Service health, SLO, incident and last-known-good | `.github/workflows/provider-availability.yml`, health/incident workflows, `scripts/ci/engineering_health.py`, `docs/ops/incidents/**`, relevant run/artifact records | A health workflow or upstream status is not itself an SLO. A last-known-good observation is scoped and expires in relevance | No single canonical SLO registry was established by this filename sweep. Inspect content and operational telemetry before claiming a gap; define service, measurement, window, target, exclusions and owner for each actual SLO |
| Awesome lists / external skill catalogs | No path name containing “awesome” was found in this master tree snapshot; use relevant curation/ingestion issues, PRs and external source references | Filename absence does not prove no references or no external work | Search issue/PR history and docs for the existing handoff; record upstream, license, exact commit/tag, imported paths, trust review and update method before any import |

## 3. Inventory exclusions and safety boundaries

The recursive tree includes large session stores, browser-profile/state paths, generated outputs, tests, caches and other data-like assets. Their presence in Git does not make them authoritative infrastructure configuration. Do not ingest their contents wholesale into a public CMDB projection. Classify by tracked path and declared purpose first; inspect content only when needed and safe.

- Never ingest secret values, tokens, cookies, private keys, authorization headers, or hashes of low-entropy secrets.
- Do not treat path names, documentation claims, code-search hits, or a successful workflow run as interchangeable proof.
- Do not infer “not present” from a failed/incomplete search. Record the search surface, ref, query and limits.
- Do not treat external upstream projects listed in a catalog as installed or vendored without import/pin evidence.
- Do not make ownership or duplicate-provisioning claims without a source, scope and evidence reference.
- Preserve private vs public projection boundaries for device identities, credentials, and internal operational details.

## 4. P0 unresolved work (ordered)

1. **Reconcile the skills inventory** against the 27 `.agents` and 10 `.github` skill entrypoints, the actual tracked files, and declared upstream/pin records. Resolve naming overlaps without assuming same-name means same authority.
2. **Search issue/PR history and references** for AntigravityCLI, awesome-list intake, external skill catalogs and any related import/pinning proposals. The current tree census is not enough to classify these.
3. **Extract writer/resource ownership claims** from workflows, provisioning scripts, resource manifests and concurrency settings. Build a candidate collision matrix; do not label collisions confirmed without corroborating evidence.
4. **Reconcile provider/quota/credential fields** against the source documents and machine-readable registries. Define authority per field rather than declaring one entire file universally authoritative.
5. **Map current reconciliation outputs** to finding classes, writers, evidence receipts, owners and history stores to avoid parallel ledgers.
6. **Establish health/SLO coverage** by reading actual SLO/telemetry contracts and run artifacts, not filename heuristics. Keep reachability, authenticated requests, capability tests and end-to-end outcomes distinct.
7. **Generate a normalized manifest and validation fixture set** from the agreed field map only after the source ownership decisions above are reviewed.

## 5. P0 exit gate

P0 is complete only when the inventory is regenerated from a recorded ref/SHA, tracked-path counts and exclusions are reproducible, relevant source authorities are mapped per field, duplicate/overlap candidates are documented, inaccessible/external surfaces are listed with reasons, and owners have reviewed unresolved questions. This baseline alone does **not** pass that gate.

## 6. Source snapshot provenance

The census used the GitHub recursive tree endpoint for `master` and fetched the following source files at that ref for focused review:

- `docs/ops/SKILLS-INVENTORY.md`
- `docs/ops/APPROXINATION-LANE.md`
- `docs/ops/WEB-ADAPTER-FOUNDRY.md`
- `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md`
- `docs/ops/QUOTA-REGISTRY.md`
- `docs/ops/CREDENTIAL-INVENTORY.md`
- `docs/ops/secrets-and-variables-registry.md`
- `docs/ops/INTEGRATION-MESH-MATRIX.md`
- `docs/ops/RECONCILIATION-CONTROL-PLANE.md`
- `docs/ops/EVIDENCE-PROJECTION-SURFACE.md`
- `docs/ops/ROUTING-ORCHESTRATION-MAP.md`
- `docs/schemas/provider-capabilities.md`
- `ops/web_adapter_foundry/README.md`
- `ops/web_adapter_foundry/registry.schema.json`
- `ops/web_adapter_foundry/catalog.json`
- `docs/repositories/browser-lane-imports.json`
- `docs/research/resource-registry.yaml`
- `docs/repositories/repository-observatory.schema.json`
- `data/ops/credential-surfaces.jsonl`
- `ops/devices/registry.json`

The source-file blob SHAs are available from the Git tree at the recorded tree SHA. This document is a reproducible starting point, not a claim that every repository resource has been semantically inspected.
