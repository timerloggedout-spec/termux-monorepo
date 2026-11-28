# Actions Architecture Evolution — Versioned Classification, Evidence, and Display

**Version:** 0.1.0  
**Status:** proposal design baseline  
**Proposal:** `actions-architecture-evolution`  
**Baseline:** `master` @ `3f082e1306169f914a8fda2b444e83ddc608dfe0` (2026-11-22)  
**Design decision:** A + B + C approved in conversation; automated GitHub Pages publishing is the highest-priority delivery lane. Repo-Story remains an existing concept and is outside this MVP.

## 1. Purpose

Establish one versioned architecture model for repository Actions, reusable workflows, composite actions, agent skills, AppID execution identities, modularization history, DoE evidence, and BRR/QUE operational receipts. Deliver a Tribute-style read-only display feed as the first user-facing projection.

The programme uses existing owners: GitHub Actions for execution, the automation catalog for generated inventory, AppID registries for identity and migration, DoE for experimental design and results, BRR/QUE for reconciliation and intake, and Tribute for presentation.

## 2. Decision record

| Decision | Selected design | Boundary |
|---|---|---|
| A — architecture | One typed automation architecture model with stable IDs and explicit lineage | Generated inventory remains a projection of source contracts |
| B — evidence | Versioned DoE factors, AppID migration receipts, and BRR evidence contract | Each owner keeps its own canonical records |
| C — display + publication | Tribute display-feed MVP, automatically refreshed and published through our existing GitHub Pages pipeline | Feed has no execution, promotion, or identity authority; GitHub Pages is the primary production target |
| Existing concept | Repo-Story remains an existing concept/reference in the architecture landscape | This programme does not create a replacement Repo-Story product or treat it as a new MVP dependency |

## 3. Classification model

### 3.1 Entity types

| Type | Identity | Canonical source | Version boundary |
|---|---|---|---|
| Workflow | Repository + workflow path; registry ID added in the next catalog schema | `.github/workflows/*` | Workflow file revision / catalog schema |
| Reusable workflow | Workflow path + declared callable interface | `.github/workflows/*` with `workflow_call` | Interface and implementation revision |
| Composite action | Action path + declared inputs/outputs | `.github/actions/*/action.yml` | Action metadata and implementation revision |
| Agent skill | Skill path + declared name/version | `.agents/skills/*`, `.github/skills/*` | Skill version and content digest |
| AppID identity | AppID + role + permission profile + installation scope | `ops/github-apps/*` | Manifest and permission-profile revision |
| Execution receipt | Workflow/run/job/attempt identifiers + source SHA | GitHub Actions run/job evidence | Immutable run/attempt |
| DoE observation | Experiment ID + run identity + configured treatment | DoE experiment record | Design version + treatment identity |
| BRR observation | Repository + branch + tip SHA + baseline SHA + disposition | BRR registry/artifact | Registry schema + observation snapshot |
| Display event | Source type + source record ID + source revision | Derived feed | Feed schema version |

### 3.2 Stable classification fields

The next automation catalog schema adds the following typed fields:

- `automation_id`: stable ID independent of path and display name.
- `entity_type`: `workflow | reusable_workflow | composite_action | skill`.
- `domain`: governed taxonomy value.
- `owner`: owning lane or subsystem.
- `lifecycle_state`: `active | deprecated | superseded | archived | candidate`.
- `authority_class`: `read_only | advisory | bounded_write | writer | promotion_authority`.
- `trigger_contract`: normalized event, schedule, dispatch, and callable triggers.
- `permission_profile`: effective workflow/job permissions, including inherited defaults.
- `identity_refs`: AppID role and credential-class references; names and IDs only.
- `input_contract` / `output_contract`: declared reusable-workflow or action interface.
- `depends_on` / `called_by`: typed dependency edges.
- `lineage`: predecessor, successor, extraction, replacement, deprecation, and retirement links.
- `source_revision`: source SHA and content digest.
- `evidence_refs`: PR, commit, run, job, artifact, migration receipt, and DoE record references.

Existing catalog classifications remain available as compatibility fields while schema v2 is introduced. The current 326-entry inventory is a workflow-file count, not a count of active production executions.

### 3.3 Classification pipeline

1. Discover source files across workflow, action, reusable-workflow, and skill roots.
2. Parse YAML front matter and declared interfaces.
3. Assign stable IDs from an explicit registry; preserve path as a locator.
4. Classify domain, owner, lifecycle, trigger contract, authority, permissions, and identity references.
5. Resolve dependency and caller edges.
6. Attach versioned lineage and evidence references.
7. Validate schema, referential integrity, and source fingerprints.
8. Generate JSON, Markdown, graph, and dashboard feed projections.

Static analysis produces declared capability and inferred hints as separate fields. Runtime state comes only from attributable GitHub run/job receipts. Unknown permission, owner, identity, or lineage values remain `unknown` / `unresolved` with a gap entry.

## 4. Organization and modularization history

Represent each modularization as an immutable architecture epoch:

`epoch_id + effective_at + baseline_sha + catalog_schema + component_manifest_digest`

Each epoch records:

- included workflow/action/skill identities;
- extracted modules and their public interfaces;
- predecessor and successor edges;
- trigger and consumer coverage;
- concurrency and deduplication behavior;
- AppID role and permission profile;
- migration wave and acceptance evidence;
- supersession or retirement decision and effective time.

Lineage edge vocabulary:

`extracted_to | replaced_by | split_into | merged_into | delegates_to | supersedes | retires`

A path rename creates a new locator revision while preserving `automation_id`. A semantic replacement creates a new entity identity and an explicit lineage edge. Historical epochs remain immutable.

The October Actions matrix and current generated inventory retain their original denominators and timestamps. The architecture model records each count with its scope, query, source SHA, and observation time.

## 5. AppID execution identity

AppIDs represent execution identities and permission boundaries. Workflow/action entities reference AppID roles; they do not own or embed credentials.

Migration state remains governed by the existing AppID process and its five gates:

1. reviewed manifest and installation;
2. token-minter wiring;
3. shadow comparison;
4. runtime receipt and independent bucket measurements;
5. previous credential path retained for one full schedule cycle.

The display model exposes role, AppID, installation scope, permission-profile digest, migration item, gate states, and evidence links. It displays credential names and references only.

Identity and topology are independent DoE factors. A workflow extraction can occur under a stable identity; an identity migration can occur without changing workflow topology. The experiment design records both factors independently.

## 6. DoE version amendment

The DoE family keeps its shared experiment record schema and existing campaign ownership. This programme proposes a versioned amendment to the DoE Questions Matrix:

| Dimension | Proposed name | Measurement |
|---:|---|---|
| 41 | Automation topology | Modularization epoch, component boundaries, dependency graph, extraction/replacement pattern |
| 42 | Execution identity | AppID role, permission-profile digest, installation scope, credential class |

Dimension 40, automation binding, remains unchanged. Existing dimensions retain their numbering and historical meaning.

Campaign: `actions-architecture-evolution`.

Factor model:

- Factor A — topology: baseline / modularized epoch.
- Factor B — identity: baseline credential route / role-scoped AppID route.
- Optional blocking factors: workflow domain, trigger class, risk tier, and migration wave.

Treatments preserve the exact catalog manifest digest, topology epoch, AppID role/profile digest, baseline and candidate SHAs, workflow/run IDs, artifact refs, and configured instance identity. Each dispatched run emits one existing-schema experiment record. Design changes create a new design version or cohort.

Response variables: successful task outcome, correctness, regression rate, integration success, duplicate execution, notification volume, API usage, quota utilization, queue latency, human intervention, rollback frequency, and maintenance cost.

Promotion evidence separates execution status → task outcome → correctness → integration → regression → resource cost. Green CI remains a validation signal, not an outcome substitute.

## 7. BRR / QUE evidence contract

BRR remains read-only. QUE/QDesk remains the scheduled intake and bounded self-repair path under its existing policy.

Every BRR observation records:

- repository and observation timestamp;
- default branch name and exact default branch SHA;
- API pagination window and completeness state;
- branch name, API tip SHA, local ref SHA;
- ancestry counts and disposition;
- linked PR identities and head/base SHAs;
- parser omissions, unresolved refs, and API capacity state;
- registry schema and collector revision;
- artifact/run URL and source SHA.

Required integrity rules:

- Every API branch row becomes a record or an explicit parse-error entry.
- `inventory_complete_for_api_pages` derives from verified pagination and parse completeness.
- Ancestry classification binds to the exact captured default-branch SHA.
- API 403/429 capacity outcomes emit structured `DEFERRED_CAPACITY` receipts and preserve the run summary.
- Idempotency remains repository + branch + tip SHA + disposition.
- BRR classification remains observational; promotion remains a separately authorized operation.

The current source review identified these as code-level repair candidates. Runtime reproduction and current scheduled artifact verification remain separate evidence tasks.

## 8. GitHub Pages publishing + Tribute display-feed MVP

### 8.1 Priority and product shape

**P0 delivery priority: our GitHub Pages publishing path.** The feed and page ship through the repository's existing publishing workflows. The existing GitHub Pages publisher remains the deployment authority; this programme adds an automatically refreshed feed and a new Tribute surface inside its established artifact.

Add an **Automation Architecture** surface to Tribute, using the existing dashboard chrome, CSS tokens, navigation conventions, responsive layout, and chartkit standard.

Primary view: a reverse-chronological event feed with compact filters and four summary measures.

Summary measures:
- catalog entities by type and lifecycle;
- AppID migrations by gate/state;
- DoE observations by design version and outcome;
- BRR observations by disposition and completeness.

Feed event families:
- `catalog_changed`
- `modularization_epoch_recorded`
- `appid_gate_advanced`
- `doe_design_admitted`
- `doe_run_recorded`
- `brr_observation_recorded`
- `que_intake_created`
- `automation_superseded`

Each event displays timestamp, category, entity, lifecycle/status, source revision, evidence links, and freshness. Filters cover domain, entity type, lifecycle, AppID role, DoE campaign, and BRR disposition.

### 8.2 Programmatic refresh and publication chain

Reuse the established `surface-feeds-collect.yml` refresh pattern: scheduled collection, `workflow_dispatch`, and source-path push triggers; deterministic collector; stable refresh branch; refresh pull request; CI validation; merge through the normal repository gates.

The architecture feed collector reads committed canonical catalog, migration, DoE, and BRR records. API-derived observations enter through stamped snapshots produced by their owning collectors. The feed collector and browser page remain network-free.

After the feed PR merges to `master`, `.github/workflows/tribute-dashboard-deploy.yml` publishes through the existing GitHub Pages process. Its `pages` job updates the monorepo `gh-pages` project hub + matrix artifact. Its `user-site` job mirrors the Tribute dashboard to `timerloggedout-spec.github.io` under `/tribute/` and the compatibility `/help-wanted/` route. The dashboard path trigger already covers `apps/tribute-dashboard/**`, including the new page and feed. GitHub Pages is the primary target; Vercel remains optional and outside the MVP critical path.

End-to-end chain:

`canonical source change → scheduled/source-triggered collector → refresh PR → CI + review → merge master → tribute-dashboard-deploy → GitHub Pages artifact → live URL/source-SHA verification`.

The collector proposes updates by PR and never commits directly to `master`. The deployment workflow runs after merge and publishes the merged source revision. A successful workflow is followed by a live URL check against the deployed version manifest/source SHA.

Feed entries carry stable `event_id`, `event_type`, `occurred_at`, `entity_ref`, `status`, `source_ref`, `source_sha`, `evidence_refs`, and `freshness`. The collector sorts deterministically and records missing sources in `gaps`.

### 8.3 Display rules

- Match Tribute's existing dark control-surface style and responsive navigation.
- Render evidence links beside the event they support.
- Render unknown and unresolved states explicitly.
- Render design-only, proposal-only, and unexecuted states exactly as recorded.
- Render stale source status beside each affected feed block.
- Render charts exclusively from feed-carried values and stamp each chart.
- Keep the feed read-only; link to canonical source records for actions and decisions.
- Preserve keyboard navigation, semantic headings, accessible status labels, and mobile single-column event cards.

### 8.4 MVP acceptance

1. Feed validates against the shared dashboard envelope.
2. Collector output is deterministic for a fixed source set.
3. Source-path changes and the scheduled cadence invoke the collector automatically; manual dispatch remains available.
4. Collector emits a refresh PR only when feed content changes; repeated unchanged runs are clean no-ops.
5. Each event resolves to a canonical source and source revision; unknown/missing evidence produces an explicit gap.
6. Page consumes only the feed; tests pin that boundary.
7. Merging the feed/page change to `master` automatically invokes the existing GitHub Pages publisher.
8. The deployed `/tribute/` URL and compatibility `/help-wanted/` URL expose the expected manifest/source SHA; publication remains pending until live verification passes.
9. Charts meet `DASHBOARD-CHART-STANDARD.md`.
10. No credential values, prompt bodies, private traces, or session artifacts enter the feed.
11. Tests cover schema validity, stable event IDs, sort order, unresolved refs, stale status, idempotent refresh, stale status, and empty-state rendering.

## 9. Existing Repo-Story concept boundary

Repo-Story is an existing concept in the repository's broader architecture landscape, with its own historical concept artifacts and RepoStory pilot identity records. This programme records a cross-reference only. It does not re-scope, rebuild, promote, or productize Repo-Story. Any future implementation decision belongs to Repo-Story's own concept and governance path.

## 10. Delivery sequence

| Stage | Output | Exit evidence |
|---|---|---|
| A1 | Typed architecture and lineage contract | Schema, validator, source crosswalk |
| B1 | DoE matrix amendment and campaign design | Versioned dimensions 41–42; experiment design record |
| B2 | AppID and BRR evidence crosswalk | Gate/evidence mapping; BRR regression fixtures |
| C1 (P0) | Programmatic collector and refresh PR | Scheduled + source-triggered collection, deterministic feed, clean no-op, refresh PR |
| C2 (P0) | GitHub Pages publication path | Existing publisher deploys the merged feed/page; live URL and source-SHA verification |
| C3 | Tribute page and chartkit integration | Feed-only UI + accessibility and freshness tests |
| C4 | Operational observation | Current-SHA run/artifact receipts and review |

## 11. Source-of-truth boundaries

| Concern | Owner |
|---|---|
| Workflow/action/skill source | Repository source files |
| Generated automation inventory | `scripts/ci/automation_docs.py` and generated catalog |
| AppID identity and migration | `ops/github-apps/` and AppID process docs |
| DoE campaign and experiment records | DoE family and shared experiment schema |
| BRR observations | BRR collector and registry artifacts |
| QUE intake and repair | QUE/QDesk existing workflow and policy |
| Contextual verified history | Context Relationship Index |
| Presentation | Tribute page and generated feed |

This design adds a cross-domain projection and explicit contracts while preserving each source owner's authority.
