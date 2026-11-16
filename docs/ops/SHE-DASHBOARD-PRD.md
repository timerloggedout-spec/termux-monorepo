# SHE Dashboard PRD

**Status:** proposed implementation contract — dashboard may ship before historical backfill is complete, but it must never present partial data as complete.

## 1. Product

Build a GitHub-native **SHE (System Health & Effectiveness) dashboard** that projects the repository's evidence corpus into an interactive operational surface. SHE is a measurement/projection layer, not a source-of-truth database.

The dashboard answers:

> **What happened, what changed, what worked, what did not, how certain are we, and which orchestration policy should improve next?**

It serves three audiences:

1. **Operator:** current health, blocked work, backfill coverage, workflow/ledger state.
2. **Researcher:** longitudinal Moneyball/3L0, DOE/MVT cohorts, manager comparisons.
3. **Forensic reviewer:** exact SHA, run, PR, review/comment, artifact, and provenance links.

## 2. Existing evidence plane

The canonical historical corpus remains `workspace/llm_map/context_relationships/`. Its current contract explicitly says the committed index is a historical seed and currently has `next_start_page = 2`; it is not yet the complete all-time corpus. The dashboard must surface that state rather than hide it.

The GitHub observability architecture already defines a three-layer pipeline:

`raw dated snapshots → normalized facts → derived aggregates`

and explicitly requires that dashboards not become the only authority.

`pr-production-ledger.yml` remains a measurement/evidence producer. It is not replaced by SHE.

## 3. Source-of-truth hierarchy

```text
Git commits / PRs / issues / reviews / checks / Actions
                         │
                         ▼
                 historical corpus
                         │
                         ├── observations
                         ├── action→effect events
                         ├── attribution/provenance
                         └── experiments/learning
                         │
                         ▼
                  SHE pure reducers
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Vercel     GitHub Pages   Hex
         interactive     static     analysis
```

Rules:

- GitHub corpus is authoritative for durable evidence.
- Actions artifacts are transport/build products, not the sole historical store.
- Vercel is the preferred interactive application surface already connected to this repository.
- GitHub Pages is an optional reproducible static mirror.
- Hex is an optional research/analysis consumer. Hex must not be required for collection, scoring, or historical preservation.
- No dashboard writes back inferred facts as if they were evidence.

## 4. Hex export contract

A prior Hex `*.zip` export/package is **not established by the current repository evidence**. Do not claim that a historical Hex ZIP has been incorporated until its actual artifact/file is located and checksum/provenance are recorded.

When Hex access is available, the supported exchange should be a versioned snapshot bundle:

```text
hex-export/
  manifest.json
  observations.jsonl
  metrics.jsonl
  experiments.jsonl
  learning.jsonl
  README.md
```

The manifest must contain:

- source Git SHA;
- corpus snapshot identifier;
- generated-at timestamp;
- schema versions;
- source file hashes;
- coverage state;
- experiment/cohort identifiers.

A ZIP may package this bundle for convenience, but the ZIP itself is not the canonical record.

## 5. Dashboard information architecture

### Overview

- corpus coverage state;
- current master SHA;
- last successful ledger observation;
- workflow health;
- backfill continuation state;
- COMMITTED / EXECUTED / VALIDATED / PROMOTED status counts;
- explicit `UNVERIFIED` indicators.

### Effectiveness

- action yield;
- resolution yield;
- realization ratio;
- no-op rate;
- regression rate;
- alignment delta;
- useful cycles;
- retries;
- conflicts;
- human intervention.

### Moneyball / 3L0

Score integrated outcomes, not activity volume. Dimensions remain:

- outcome;
- integration;
- time;
- useful cycles;
- context efficiency;
- retries;
- conflicts;
- human intervention;
- attribution confidence.

Managers/orchestration policies compete on comparable cohorts.

### DOE / MVT

Each experiment shows:

- experiment ID;
- baseline SHA;
- candidate SHA;
- treatment/policy;
- fixed validation suite;
- observation timestamps;
- outcomes;
- confidence;
- promotion state.

### Provenance

Every metric must resolve to evidence identifiers where available:

`run → job → step → event → PR/issue → SHA → timestamp → artifact/evidence URL`

Unknown attribution remains unknown/low-confidence.

## 6. Partial-data UX

The dashboard must make incomplete evidence visually unavoidable.

Required states:

- `COMPLETE`
- `PARTIAL_CONTINUATION_REQUIRED`
- `PARTIAL_BOUNDARY`
- `FAILED`
- `UNVERIFIED`

No synthetic zeroes. Missing is missing. A metric without sufficient provenance is marked unavailable or low-confidence.

## 7. Free-scope deployment strategy

**Do not make Render a dependency.** Render Blueprints are useful learning/templates, but requiring billing for the dashboard violates the current free-scope objective.

Preferred sequence:

1. **Vercel** — primary interactive dashboard, using the existing GitHub-connected hobby project.
2. **GitHub Pages** — static snapshot if Pages is enabled; generated entirely by Actions.
3. **Hex** — optional analysis cockpit when account access permits.
4. **Render/n8n** — reference/template lane only unless a genuinely free, non-expiring deployment path is verified.

The public `render-examples/n8n` pattern is useful as a template for declarative deployment (`render.yaml` + service/database), but it is not evidence that Render is our required runtime.

## 8. Drag-and-drop / visual lane

The architecture should support a visual composition layer without making the runtime depend on a visual editor.

Canonical visual artifacts:

- `.mmd` architecture/source diagrams;
- generated `.png` previews for human review;
- workflow definitions that map one-to-one with documented collectors/reducers/publishers;
- optional n8n workflow examples as importable teaching/reference material.

The visual layer is a projection of the evidence pipeline, not a second orchestration truth.

## 9. Implementation phases

### Phase A — now

- land this PRD and architecture contract;
- build a read-only dashboard shell;
- consume committed corpus/observability artifacts;
- show coverage and provenance state;
- do not require Hex or Render.

### Phase B — historical mechanics

- execute `context-relationship-backfill.yml` page by page;
- continue from `next_start_page` until `null`;
- retain page bounds and timestamps;
- validate corpus after each bounded continuation.

### Phase C — operational telemetry

- prove `pr-production-ledger.yml` runtime publication;
- connect action/effect observations to corpus snapshots;
- expose longitudinal deltas.

### Phase D — research

- freeze cohort snapshots;
- run DOE/MVT comparisons;
- export stable bundles to Hex when available;
- record learning against observation IDs.

### Phase E — visualization

- Vercel interactive dashboard;
- optional Pages static mirror;
- generated `.mmd` + `.png` architecture views;
- optional n8n drag/drop examples.

## 10. Acceptance criteria

The dashboard is production-worthy when:

1. it is useful while corpus coverage is partial;
2. every displayed metric identifies its evidence snapshot/version;
3. it never converts missing evidence into zero;
4. it distinguishes COMMITTED / EXECUTED / VALIDATED / PROMOTED;
5. it shows backfill continuation state;
6. it can render without Hex access;
7. it can render without Render;
8. it has a deterministic static-data build path;
9. it preserves exact SHA/time provenance;
10. a future Hex ZIP can be imported without becoming the system of record.

## 11. Explicit non-goals

- Replacing GitHub Actions with n8n.
- Making Hex the database.
- Making Render mandatory.
- Treating a dashboard score as causal attribution.
- Treating PR volume as effectiveness.
- Claiming historical completeness before the backfill contract reaches `next_start_page = null`.
- Claiming a historical Hex ZIP exists until the artifact is located and verified.
