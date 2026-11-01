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

## 8. UI development surfaces & rendering lanes

This is a **separate taxonomy** from both the six Help-Wanted header categories and the ten SHE cockpit destinations. Those describe information architecture; this section describes the user-facing modality, target device, renderer, and interaction runtime in which any product surface may be implemented.

### 8.1 Surface families

| Surface family | Target / experience | Representative sub-surfaces | Primary constraints |
|---|---|---|---|
| **Terminal UI (TUI)** | Text-mode interactive applications in terminals and terminal emulators | ASCII-only; Unicode/box-drawing; ANSI color/style; full-screen keyboard TUI; split-pane/multiplexer TUI; mixed text + graphics protocols | Terminal capabilities, width/height, color depth, Unicode/font support, input protocol, SSH latency, accessibility |
| **Command-line interface (CLI)** | Command invocation, scripting, automation, pipelines | POSIX-style commands; interactive prompts; REPL; shell completion; machine-readable output | Stable exit codes, stdin/stdout/stderr, composability, non-interactive mode, predictable output |
| **Web GUI** | Browser-based interactive applications | Semantic HTML/CSS; DOM; SVG; Canvas 2D; WebGL/WebGPU; responsive web; PWA | Browser support, network/offline behavior, responsive layout, accessibility, security boundaries |
| **Desktop GUI** | Installed desktop applications | Native toolkit; Electron/Tauri; embedded webview; cross-platform desktop | OS integration, packaging, updates, window management, filesystem permissions |
| **Mobile** | Phone and tablet applications | iOS/iPadOS; Android; native; cross-platform; hybrid; mobile web/PWA | Touch, gestures, safe areas, lifecycle, permissions, battery, offline/cache, variable viewport |
| **eReader / e-paper** | Reading-first and low-refresh displays | EPUB reflow; fixed-layout EPUB; PDF; HTML reader; e-ink companion UI | Reflow, pagination, font scaling, grayscale/limited color, refresh latency, low-power operation, annotations and bookmarks |
| **TV / large-screen / kiosk** | Lean-back, public, or shared-screen interaction | TV apps; 10-foot UI; signage; kiosk; controller/remote navigation | Distance legibility, focus navigation, session reset, unattended operation, restricted input |
| **Wearable / ambient** | Glanceable, constrained personal devices | Watch UI; notification/complication; sensor display; heads-up display | Tiny viewport, short interactions, battery, sensor/privacy permissions, glanceability |
| **Voice / audio** | Speech-first and audio-first interaction | Voice UI; spoken prompts; screen-reader-compatible audio flow; audio player; voice agent | Turn-taking, latency, interruption, transcripts, discoverability, noisy environments |
| **XR / spatial computing** | Immersive or spatially anchored interfaces | VR; AR; MR; spatial windows; world-locked and head-locked panels; hand/controller/eye interaction | Comfort, motion sickness, tracking loss, spatial legibility, input ergonomics, safety boundaries |
| **Print / export** | Durable, portable, or offline reading artifacts | PDF; print CSS; paginated reports; static image/export | Pagination, selectable text, metadata, contrast, archival stability |

### 8.2 Rendering and implementation lanes

Surface family is not a framework choice. Track the renderer/runtime independently so the same product capability can have multiple implementations.

| Rendering lane | Technologies / patterns | Typical target surfaces | Engineering notes |
|---|---|---|---|
| **Plain text** | ASCII, UTF-8 text, line-oriented output | CLI, basic TUI, logs, eReader fallback | Lowest common denominator; preserve semantic structure without color |
| **ANSI terminal** | ANSI/ECMA-48 control sequences, 16/256/truecolor, cursor addressing | Rich TUI, terminal dashboards | Detect capabilities; provide NO_COLOR/plain mode; avoid assuming every terminal supports every sequence |
| **Rust terminal UI** | ratatui + crossterm or termion | Full-screen Rust TUI | Treat backend, terminal restoration, event loop, layout, and widgets as explicit dependencies |
| **Go terminal UI** | Bubble Tea + Lip Gloss (and compatible components) | Model-driven Go TUI | Keep update/view state deterministic; degrade styles when color/TTY support is absent |
| **Mixed terminal** | Text + ANSI + Unicode; optional sixel/Kitty/iTerm graphics where supported | Advanced terminal cockpit | Feature-detect graphics protocols; text-only fallback is mandatory |
| **Web semantic** | HTML + CSS + DOM + JavaScript/TypeScript | Web GUI, PWA, eReader web reader | Semantic controls and progressive enhancement; keyboard and assistive technology support |
| **Vector / 2D / GPU web** | SVG, Canvas 2D, WebGL, WebGPU | Charts, diagrams, editors, spatial previews | Choose by interaction/rendering need; keep accessible textual alternatives and data provenance |
| **Native platform** | Swift/SwiftUI, UIKit; Kotlin/Compose, Android Views; platform desktop toolkits | Mobile, desktop, wearable | Platform lifecycle, accessibility APIs, signing and distribution are first-class |
| **Cross-platform shell** | Tauri, Electron, React Native, Flutter, Kotlin Multiplatform | Desktop/mobile | Record shared-core vs platform-specific code and runtime version separately |
| **Publishing / document** | EPUB 2/3, PDF, HTML, print CSS | eReader, print/export | Validate reflow, navigation landmarks, metadata, pagination and font scaling |
| **XR runtime** | OpenXR, WebXR, platform spatial APIs; Unity/Unreal where applicable | VR, AR, MR, spatial | Record device/runtime capabilities and interaction modalities; never infer support from platform name alone |
| **Game / real-time engine** | Unity, Unreal, Godot, custom real-time renderer | XR, simulation, visualization, kiosk | Track engine, rendering pipeline, asset bundle and device profile independently |

**TUI clarification:** ASCII, ANSI, ratatui, Go Lip Gloss, and mixed terminal output are not five peer device surfaces. They are overlapping format, capability, framework, and composition lanes within the Terminal UI family. ratatui is a Rust TUI framework; Lip Gloss is a Go styling/layout library commonly paired with Bubble Tea. CLI remains a distinct command-and-pipeline interface even when it shares terminal output code with a TUI.

### 8.3 Cross-surface capability dimensions

Every surface implementation should declare a capability profile rather than assuming that all devices in a family behave alike:

- **Input:** keyboard, pointer, touch, stylus, remote/controller, hand tracking, eye gaze, voice, switch access.
- **Output:** text, color, vector, raster, audio, haptics, spatial overlays.
- **Viewport:** dimensions, density, orientation, safe areas, terminal cell geometry, e-ink page geometry.
- **Runtime:** OS, browser/engine, terminal emulator, renderer/backend, API level, XR runtime.
- **Connectivity:** online, intermittent, offline-first, local-only, SSH/remote.
- **Accessibility:** semantic structure, focus order, keyboard operation, screen reader, captions/transcripts, contrast, reduced motion, scalable text.
- **Resource envelope:** memory, CPU/GPU, battery, bandwidth, thermal budget, refresh rate.
- **Security / privacy:** permission model, data locality, session isolation, shared-device behavior, sensor consent.

Capabilities should be recorded as SUPPORTED, PARTIAL, UNSUPPORTED, or UNKNOWN with evidence and tested version. UNKNOWN must not silently become SUPPORTED.

### 8.4 Product capability → surface projection

A capability may be projected to more than one surface, but each projection is its own implementation and conformance target.

```text
Product capability / domain contract
├── Web GUI projection
├── Desktop GUI projection
├── Mobile projection
├── TUI projection
│   ├── Plain / ASCII fallback
│   ├── ANSI-enhanced
│   ├── ratatui (Rust)
│   ├── Bubble Tea + Lip Gloss (Go)
│   └── Mixed terminal protocols
├── eReader / EPUB / PDF projection
├── Voice / audio projection
└── XR / spatial projection
    ├── VR
    ├── AR
    └── MR
```

Do not force identical layouts or interactions across modalities. Share domain logic, API contracts, identity, and evidence where appropriate; adapt navigation, density, input, and presentation to the surface.

### 8.5 Surface identity and versioning

Each shipped projection should carry a stable surface identity and a distinct implementation/build identity:

| Field | Purpose |
|---|---|
| `surface_id` | Stable modality/product projection, e.g. `dashboard.web`, `ops.tui.ratatui`, `reader.epub`, `spatial.xr` |
| `surface_family` | TUI, CLI, web, desktop, mobile, eReader, TV/kiosk, wearable, voice/audio, XR, print |
| `renderer_id` | DOM, SVG, Canvas, ANSI, ratatui, Lip Gloss/Bubble Tea, native toolkit, EPUB renderer, OpenXR/WebXR, etc. |
| `renderer_version` | Framework/engine/runtime version used by the projection |
| `target_profile` | OS/device/browser/terminal/eReader/XR capability profile |
| `interaction_profile` | Keyboard, touch, pointer, remote, controller, hand, gaze, voice, mixed |
| `accessibility_profile` | Declared and tested accessibility capabilities |
| `domain_contract_version` | Shared product/API contract consumed by the surface |
| `surface_schema_version` | Surface-specific view-model or serialized projection schema |
| `build_id` + `source_sha` | Immutable build and source provenance |
| `conformance_suite` | Tests and fixtures passed by this surface/target profile |

A framework upgrade does not automatically change the domain contract. A domain schema change does not automatically imply a renderer upgrade. A new target device profile may require a new conformance run without changing either.

### 8.6 Surface conformance and release gates

- [ ] Surface family, renderer lane, target profile, and interaction profile are declared.
- [ ] Plain/fallback behavior exists where the runtime may not support enhanced rendering (especially terminal color/graphics and network-dependent web features).
- [ ] Keyboard, focus, touch/controller/remote, and assistive interaction paths are tested as applicable.
- [ ] Layout is validated at representative viewport/cell/page sizes and orientations.
- [ ] Offline, reconnect, low-bandwidth, and interrupted-session behavior is tested where applicable.
- [ ] Resource and lifecycle behavior is tested on representative target hardware or a declared emulator.
- [ ] Accessibility claims map to concrete tests and target-specific support evidence.
- [ ] Renderer/framework/runtime versions, domain contract, surface schema, build ID, and source SHA remain separately observable.
- [ ] Screenshots, recordings, golden terminal fixtures, EPUB/PDF samples, and XR captures are treated as derived test artifacts with source/build provenance.
- [ ] Surface-specific failures do not get hidden by aggregate cross-platform pass rates.

### 8.7 Documentation and registry ownership

Maintain the machine-readable starter registry at `docs/ops/ui-surface-registry.json`; its normative JSON Schema is `docs/ops/ui-surface-registry.schema.json` (Draft 2020-12). The registry declares `schema_version` and a relative `schema_ref`; validate changes against that schema in CI or before merging. It indexes projections by `surface_id`, family, renderer, target profile, evidence paths, maturity, confidence, and support status. This is an initial evidence-backed inventory, not a claim that every listed implementation is production-ready or deployed. Empty evidence paths plus `maturity: proposed` mean no implementation was confirmed in the inspected repository tree; they do not prove that no prototype exists elsewhere. Extend the schema as owner, domain contract, conformance suite, build ID, and tested support evidence become available. Update the registry whenever a surface is introduced, retired, changes renderer, or changes its supported target profile.

The current six Help-Wanted categories and ten SHE destinations remain unchanged. They are navigation structures that can link to any of these modality projections; they are not rendering lanes.
