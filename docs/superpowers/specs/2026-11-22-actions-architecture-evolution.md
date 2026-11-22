# Actions Architecture Evolution — Versioned Classification, Evidence, and Display

**Version:** 0.1.0  
**Status:** proposal design baseline  
**Proposal:** `actions-architecture-evolution`  
**Baseline:** `master` @ `3f082e1306169f914a8fda2b444e83ddc608dfe0` (2026-11-22)  
**Design decision:** A + B + C approved in conversation; Repo-Story reserved as a potential future extension.

## 1. Purpose

Establish one versioned architecture model for repository Actions, reusable workflows, composite actions, agent skills, AppID execution identities, modularization history, DoE evidence, and BRR/QUE operational receipts. Deliver a Tribute-style read-only display feed as the first user-facing projection.

The programme uses existing owners: GitHub Actions for execution, the automation catalog for generated inventory, AppID registries for identity and migration, DoE for experimental design and results, BRR/QUE for reconciliation and intake, and Tribute for presentation.

## 2. Decision record

| Decision | Selected design | Boundary |
|---|---|---|
| A — architecture | One typed automation architecture model with stable IDs and explicit lineage | Generated inventory remains a projection of source contracts |
| B — evidence | Versioned DoE factors, AppID migration receipts, and BRR evidence contract | Each owner keeps its own canonical records |
| C — display | Tribute dashboard MVP with a generated, read-only event feed | Feed has no execution, promotion, or identity authority |
| Future candidate | Repo-Story narrative reconstruction and commit replay | Candidate only; excluded from MVP dependencies |

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

## 8. Tribute display-feed MVP

### 8.1 Product shape

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

### 8.2 Feed contract

Use the existing `dashboard-surface-feed/v1` envelope for the MVP:

`{schema, surface, generated_at, sources, honesty_rules, data, gaps}`

The MVP feed path is `apps/tribute-dashboard/data/actions-architecture-feed.json`. The page consumes only this feed. A deterministic collector reads committed catalog, migration, DoE, and BRR records. Any API observation enters through an existing stamped snapshot/receipt path; the page and collector remain network-free.

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
3. Each event resolves to a canonical source and source revision.
4. Unknown/missing evidence produces an explicit gap.
5. Page consumes only the feed; tests pin that boundary.
6. Charts meet `DASHBOARD-CHART-STANDARD.md`.
7. No credential values, prompt bodies, private traces, or session artifacts enter the feed.
8. Tests cover schema validity, stable event IDs, sort order, unresolved refs, stale status, and empty-state rendering.

## 9. Repo-Story — future candidate

Repo-Story is a potential future C: a narrative and temporal reconstruction layer that explains how an automation entity evolved across commits, PRs, modularization epochs, and operational outcomes.

Candidate responsibilities:
- compose a human-readable lineage narrative from verified GitHub history;
- link architecture epochs to exact commits and PRs;
- replay state transitions from immutable receipts;
- distinguish verified events from inferred narrative candidates.

Repo-Story remains outside the MVP execution graph. The Context Relationship Index remains the metadata evidence substrate; Repo-Story may consume its verified references and temporal snapshots. The candidate receives a separate proposal/item and DoE admission before implementation.

## 10. Delivery sequence

| Stage | Output | Exit evidence |
|---|---|---|
| A1 | Typed architecture and lineage contract | Schema, validator, source crosswalk |
| B1 | DoE matrix amendment and campaign design | Versioned dimensions 41–42; experiment design record |
| B2 | AppID and BRR evidence crosswalk | Gate/evidence mapping; BRR regression fixtures |
| C1 | Feed collector and contract tests | Deterministic JSON feed + tests |
| C2 | Tribute page and chartkit integration | Feed-only UI + accessibility and freshness tests |
| C3 | Operational observation | Current-SHA run/artifact receipts and review |

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
