# UI Surface & Version-Lane Map

**Status:** documentation consolidation / implementation map  
**Scope:** Help-Wanted dashboard navigation, SHE cockpit surfaces, evidence/version identities, and nested evaluation lanes.  
**Authority:** this is an index and mapping layer. Existing page contracts, schemas, source files, GitHub evidence, and deployment receipts remain authoritative.

## Executive summary

The current Help-Wanted shell exposes a long, flat set of links. Treating every link as a peer hides the information architecture and confuses product surfaces with measurement/version lanes.

Normalize the observed inventory into six category groups while preserving existing URLs as stable leaf routes:

1. **Entry & operations** — Marketing, Ops · Tribute, Desk, Tracking.
2. **Lane discovery & coordination** — Lane matrix, PR Lanes, Dispatch Tree.
3. **Capacity & service health** — Quota, Quota Usage, Quota Graphs, Free-tier value, Countdowns.
4. **Evaluation & decision science** — 3L0, MoneyBall, MVT, DoE, ATES, Oracle.
5. **Governance, research & proposals** — Admin, Admin Graph, Linguist, Delphi RFP, Delphi Ledgers, Proposals, Telemetry.
6. **Publication & repository** — Vercel deployment, Sitemap, Monorepo.

This is a **logical grouping proposal**, not a claim that the current HTML already implements grouped menus. The live shell currently renders a single primary navigation list; regrouping should preserve leaf links, aria-current, deep links, and mobile reachability.

## 1. Current header inventory → category map

| Category | Current leaf surfaces | Primary question | Authority / contract |
|---|---|---|---|
| Entry & operations | Marketing; Ops · Tribute; Desk; Tracking | What is happening and what needs an operator? | Help-Wanted feed contracts, GitHub issues/PRs, run/evidence receipts |
| Lane discovery & coordination | Lane matrix; PR Lanes; Dispatch Tree | Which lane owns the work, and how does it progress? | Lane matrix / lane contracts; dispatch intake and pipeline evidence |
| Capacity & service health | Quota; Quota Usage; Quota Graphs; Free-tier value; Countdowns | What capacity, usage, expiry, or timing constraints apply? | Provider-originated quota evidence; freshness and attribution rules; explicit unknowns |
| Evaluation & decision science | 3L0; MoneyBall; MVT; DoE; ATES; Oracle | What worked, under which cohort/policy, and with what confidence? | Versioned evaluation records, baseline/treatment SHAs, telemetry schemas, source-linked outcomes |
| Governance, research & proposals | Admin; Admin Graph; Linguist; Delphi RFP; Delphi Ledgers; Proposals; Telemetry | What is configured, proposed, researched, or measured? | Admin controls/contracts, proposal registry, research lane records, telemetry/event schemas |
| Publication & repository | Vercel deployment; Sitemap; Monorepo | Where is the surface published and where is its source? | Deployment receipts, generated sitemap, GitHub source and commit identity |

**Cross-cutting navigation items:** the Autonomous AI Employees brand/home link is the global entry point; it is not a separate operational lane. The GitHub repository link is a source-of-truth destination, not a dashboard data store.

### Grouping constraints

- Do not remove or rename existing leaf routes as part of a navigation-only refactor.
- A category is navigation taxonomy, not a new system of record or workflow.
- Preserve direct URLs and external links.
- Mark the current leaf with aria-current="page" and ensure grouped navigation remains keyboard accessible.
- On narrow screens, collapse category groups without making deep leaves undiscoverable.
- Never imply that an Admin/Oracle view has write authority unless its own contract explicitly grants it.
- Publication reachability is not deployment provenance; show source SHA/run/receipt where available.

## 2. SHE cockpit surfaces are a separate, related map

The Help-Wanted header and the SHE dashboard are related navigation systems, but they are **not the same surface taxonomy**. SHE's contract defines these top-level destinations:

| SHE surface | Main concern | Evidence source |
|---|---|---|
| Overview | Current system state and coverage | Snapshot, source SHA, workflow health, freshness |
| Operations | Queued/running/failed work and blockers | GitHub Actions runs/jobs/steps and watcher receipts |
| Effectiveness | Action → effect and realization | Validated event records and reducer outputs |
| Moneyball / 3L0 | Manager/policy comparison | Cohort snapshots, confidence, attribution |
| Experiments | Baseline/treatment and outcomes | Experiment records and fixed validation suite |
| Relationships | Entity/artifact/temporal connections | Historical corpus and relationship snapshots |
| Provenance | Reconstruct a metric or claim | Run → job → step/event → PR/issue → SHA → artifact |
| Architecture | System wiring and boundaries | Authoritative .mmd sources plus derived renders |
| Research | Hypotheses and candidate integrations | Explicitly classified research-lane records |
| Settings / Surface health | Projection/build/adapter health | Snapshot/schema/build/deployment metadata |

Use the SHE surface map for the SHE cockpit and the six category groups above for the Help-Wanted shell. Cross-link concepts where useful, but do not silently merge their navigation or contracts.

## 3. Version lanes: keep identities orthogonal

“Version” refers to several different identities. Store and display them separately; never collapse them into one generic version badge.

| Version lane | Identity | What it versions | Required display / invariant |
|---|---|---|---|
| **Source lane** | repository + ref + commit SHA | Code and configuration that produced a result | Exact immutable SHA; branch name alone is insufficient |
| **Surface/build lane** | surface ID + build/deployment ID + source SHA | A deployed UI or static projection | Environment and deployment receipt; reachability alone is not proof |
| **Snapshot lane** | snapshot ID + snapshot schema version + generated-at | A point-in-time projection of source evidence | Coverage, freshness, source SHA, schema version, and partial/unverified status |
| **Event/evidence lane** | event schema version + deterministic event ID + run ID/attempt where applicable | Immutable observation records | Idempotent replay; distinct run attempts remain distinct |
| **Experiment lane** | experiment ID + cohort/task/arm/repetition + baseline SHA + candidate SHA | A controlled comparison | Fixed suite/window, environment fingerprint, outcomes, confidence, promotion state |
| **Metric/reducer lane** | metric contract/version + reducer version + input snapshot/event set | Derived measures and scores | Preserve raw inputs, formula/provider version, missingness, and reproducibility |
| **Research/integration lane** | lane ID + hypothesis + integration status + evidence status | A candidate tool/provider or research track | Research findings never become production dependencies without an explicit gate |
| **Navigation/API lane** | route/leaf ID + feed/API schema version | UI entry point and the data contract it consumes | Route identity is not data/schema identity; backward-compatible leaf URLs |

### Versioning rules

1. **SHA is provenance, not a product version.** A source SHA answers which code produced an observation; a schema version answers how to interpret its shape.
2. **Snapshot schema and event schema are independent.** A new UI snapshot shape must not silently rewrite historical event meaning.
3. **Metric versions are explicit.** If a formula, complexity provider, reducer, or normalization changes, record the new version and retain prior raw observations.
4. **Experiment identity is immutable.** Baseline, candidate, environment, task cohort, repetition, and validation suite must be captured before comparing outcomes.
5. **Unknown stays unknown.** Missing versions, unavailable provider usage, missing evidence, and unobserved runtime state must not be represented as zero or as the current version by assumption.
6. **Promotion is a separate state.** PROPOSED → ADMITTED → RUNNING → OBSERVED → VALIDATED → PROMOTED is not a version sequence and must not be conflated with COMMITTED / EXECUTED / VALIDATED / PROMOTED provenance states.
7. **Derived visual assets are not canonical.** Mermaid .mmd is source; rendered .png is a review artifact identified by source/render hashes.
8. **External adapters are optional consumers.** Vercel, Pages, Hex, Grafana, and n8n do not replace canonical GitHub/source/evidence contracts.

## 4. Nested evaluation lanes

The following hierarchy makes relationships visible without pretending the metrics are interchangeable:

```text
Evaluation & decision science
├── 3L0 / Moneyball — manager/policy decision and longitudinal comparison
│   ├── MVT — controlled baseline/treatment trials
│   ├── DoE — factor/cohort design and analysis
│   └── ATES / TCV / WTCV / TPV / RPI — execution/throughput evidence dimensions
└── Oracle — operator-facing interpretation/decision surface
    └── must link back to cohort, source evidence, and confidence
```

This is a **navigation and conceptual nesting proposal**. Keep each lane's existing schema and semantics. ATES is not a correctness substitute or automatic merge gate; Moneyball scores managers/policies using integrated outcomes, quality, effort, conflicts, retries, human intervention, and attribution confidence.

## 5. Evidence spine shared by every surface

```text
GitHub / Git / Actions / artifacts (authority)
                  ↓
        validated event/evidence records
                  ↓
         deterministic reducers
                  ↓
      versioned snapshot / experiment rows
                  ↓
     Help-Wanted / SHE / Pages / Vercel
                  ↓
          optional analytics adapters
```

A displayed claim should expose, where applicable:

- source repository/ref/SHA;
- snapshot or event ID and schema version;
- observed-at/generated-at timestamp and freshness;
- status and coverage (COMPLETE, partial, unverified, unavailable, failed);
- metric/reducer version and cohort definition;
- evidence link back to canonical source.

The UI remains a read-only projection. If a projection conflicts with source evidence, rebuild the projection; do not edit the projection to manufacture truth.

## 6. Documentation ownership and update map

| Concern | Canonical document/source | Update required when |
|---|---|---|
| Help-Wanted live navigation | apps/help-wanted-dashboard/index.html (shared nav also appears in leaf pages) | A leaf route is added/renamed/retired or category membership changes |
| SHE information architecture | docs/ops/SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md | A SHE surface, interaction, responsive behavior, or acceptance gate changes |
| SHE index/navigation | docs/ops/SHE-DASHBOARD-INDEX.md | A new contract or map is added |
| Snapshot contract | docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md | Snapshot fields, status, identity, or schema version changes |
| Evidence projection | docs/ops/EVIDENCE-PROJECTION-SURFACE.md | Event envelope, provenance, idempotency, or consumer boundary changes |
| Lane ownership | docs/ops/LANE-MATRIX.md and lane-specific contracts | Ownership, admission, state transitions, or evidence source changes |
| Experiment/metric records | Relevant schema + metric/evaluation contract | A metric, formula, cohort identity, or event schema changes |
| Architecture diagrams | Authoritative .mmd source; generated asset manifest | Architecture or integration boundary changes |

### Acceptance checklist for the next UI pass

- [ ] Six category groups are represented in the design without deleting existing leaf routes.
- [ ] All existing header links remain reachable by keyboard and mobile navigation.
- [ ] Current-page state and accessible labels are preserved.
- [ ] Each version lane is shown as a distinct field/badge where relevant, not one ambiguous “version”.
- [ ] Source SHA, snapshot/schema identity, freshness, coverage, and provenance are visible on evidence-backed surfaces.
- [ ] Partial, unknown, unavailable, cancelled, and failed states remain distinct.
- [ ] Every experiment identifies baseline/candidate SHA, cohort, environment, suite, and observation window.
- [ ] Navigation refactor does not grant write authority or introduce new canonical storage.
- [ ] Docs and any generated diagrams are updated in the same change set.
- [ ] CI validates links, schemas, and any changed navigation contract before promotion.

## 7. Related contracts

- docs/ops/SHE-DASHBOARD-INDEX.md
- docs/ops/SHE-DASHBOARD-PRD.md
- docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md
- docs/ops/SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md
- docs/ops/EVIDENCE-PROJECTION-SURFACE.md
- docs/ops/LANE-MATRIX.md
- docs/ops/AGENT-EVALUATION-LANE-REGISTRY.md

## Source inspection note

The current Help-Wanted shell (apps/help-wanted-dashboard/index.html) contains a single flat primary navigation list. The six groups above normalize that observed inventory into a maintainable taxonomy; they are not asserted to exist as grouped DOM elements today. SHE's ten-surface model is already explicitly defined in the UI/UX control-plane contract.