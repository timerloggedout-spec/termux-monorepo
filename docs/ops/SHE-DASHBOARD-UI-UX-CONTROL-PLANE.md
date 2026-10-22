# SHE Dashboard UI/UX Control-Plane Contract

**Status:** implementation-ready surface contract  
**Authority:** extends `docs/ops/SHE-DASHBOARD-PRD.md` and `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`  
**Principle:** UI is a read-only projection of evidence, never a second source of truth.

## 1. Surface model

SHE is not one page. It is an operator/research/forensics cockpit with a shared evidence spine.

```text
GitHub truth
   │
   ├── commits / PRs / issues / reviews / checks / runs
   │
   ▼
historical corpus + Actions evidence
   │
   ▼
deterministic SHE reducers
   │
   ▼
versioned snapshot
   │
   ├──────────────┬───────────────┬───────────────┐
   ▼              ▼               ▼               ▼
Overview       Operations       Research       Forensics
   │              │               │               │
   └──────────────┴───────┬───────┴───────────────┘
                           ▼
                    evidence drawer
                           │
                           ▼
                  exact GitHub source
```

## 2. Primary navigation

The interactive surface MUST expose these top-level destinations:

| Surface | Primary question | Required data |
|---|---|---|
| **Overview** | What is the system state now? | coverage, SHA, workflow health, promotion states, freshness |
| **Operations** | What needs attention? | queued/running/failed work, backfill continuation, watchers, blocked lanes |
| **Effectiveness** | What actually worked? | action→effect, realization, retries, conflicts, intervention, quality |
| **Moneyball / 3L0** | Which orchestration performs better? | cohort scores, dimensions, confidence, manager comparisons |
| **Experiments** | What changed and what did it prove? | DOE/MVT cohorts, baseline/treatment SHA, outcomes, promotion |
| **Relationships** | How do artifacts/entities connect? | graph nodes/edges, confidence, temporal state |
| **Provenance** | Can I prove this metric? | run→job→step→event→PR/issue→SHA→artifact |
| **Architecture** | How is the system wired? | Mermaid sources, rendered diagrams, integration boundaries |
| **Research** | What is being investigated? | provider/tool lanes, hypotheses, evidence status, findings |
| **Settings / Surface health** | Is the projection itself healthy? | snapshot freshness, schema version, build status, adapter status |

The navigation must work on desktop and collapse into a compact drawer/bottom navigation on narrow screens.

## 3. Global shell

Every page shares:

- repository/ref identity;
- current source SHA;
- snapshot ID;
- generated-at timestamp;
- coverage state;
- freshness indicator;
- environment/deployment indicator;
- global search;
- evidence/provenance drawer;
- explicit `UNVERIFIED` / partial-data badges;
- link to canonical GitHub evidence.

Never show a dashboard-derived number without its snapshot/provenance context.

## 4. Overview cockpit

### Above the fold

1. **System state banner**
   - `COMPLETE`
   - `PARTIAL_CONTINUATION_REQUIRED`
   - `PARTIAL_BOUNDARY`
   - `FAILED`
   - `UNVERIFIED`

2. **Health strip**
   - corpus coverage;
   - workflow health;
   - ledger status;
   - backfill state;
   - snapshot age;
   - promotion state.

3. **Current change**
   - source SHA;
   - latest meaningful PR/change;
   - what changed;
   - evidence links.

4. **Attention queue**
   - failures;
   - blocked work;
   - stale/unverified surfaces;
   - continuation required;
   - evidence gaps.

### Below the fold

- effectiveness trend;
- recent action→effect timeline;
- orchestration comparison;
- corpus/relationship growth;
- architecture/provenance preview.

## 5. Operations surface

Use a dense operational table plus drill-down drawer.

Required columns:

- state;
- lane;
- workflow/run;
- SHA;
- started;
- duration;
- conclusion;
- owner/actor;
- evidence;
- next action.

States must distinguish:

`QUEUED ≠ IN_PROGRESS ≠ COMPLETED ≠ VALIDATED ≠ PROMOTED`.

Failure/cancellation/skip are separate states.

The UI must not automatically retry work merely because it failed.

## 6. Effectiveness surface

Charts are secondary to inspectable evidence.

Required views:

- action→effect funnel;
- realization ratio;
- useful cycles;
- retry/conflict burden;
- human-intervention rate;
- WTCV/TCV/TPV/RPI/ATES where available;
- longitudinal comparison.

Every chart supports:

- time window;
- cohort;
- manager/policy;
- provider;
- confidence;
- evidence drill-down.

No `MIN_ATES_THRESHOLD` merge gate is implied. Quality/correctness evidence remains primary.

## 7. Moneyball / 3L0 surface

The default comparison is **manager/policy**, not raw model popularity.

Comparison dimensions:

- outcome;
- integration;
- time;
- useful cycles;
- context efficiency;
- retries;
- conflicts;
- human intervention;
- attribution confidence.

Display:

- cohort definition;
- sample size;
- baseline;
- treatment;
- missing dimensions;
- confidence;
- provenance.

Never rank a manager using activity volume alone.

## 8. Experiments surface

Each experiment card must identify:

`experiment_id`, baseline SHA, candidate SHA, treatment/policy, fixed validation suite, observation window, outcomes, confidence, promotion state.

Experiment UI must distinguish:

- proposed;
- admitted;
- running;
- observed;
- validated;
- promoted;
- rejected;
- inconclusive.

## 9. Relationships / graph surface

The graph is a navigation and reasoning aid, not a replacement for the corpus.

Required interactions:

- pan/zoom;
- node search;
- edge filtering;
- confidence filtering;
- temporal filtering;
- artifact-type filtering;
- expand/collapse neighborhoods;
- inspect source evidence.

Edge states:

- verified;
- candidate;
- inferred;
- unknown.

Historical views must use immutable L2 snapshots/temporal query surfaces rather than reconstructing past state from the current graph alone.

## 10. Provenance drawer

Every metric/card/table row that has evidence MUST expose an evidence drawer.

Minimum chain:

```text
metric
  → snapshot
  → source SHA
  → corpus/ledger record
  → workflow run
  → job
  → step/event
  → PR/issue
  → artifact
```

The drawer should make the distinction between:

- observed;
- derived;
- inferred;
- unavailable

immediately visible.

## 11. Architecture surface

Architecture is rendered from source.

```text
.mmd source
   ↓
deterministic renderer
   ↓
.png / visual artifact
   ↓
source/render hash manifest
   ↓
UI architecture viewer
```

The UI may show generated PNGs for stable review and optionally render Mermaid interactively, but the source remains the `.mmd`.

The existing `.mmd → .png` automation remains independent from n8n.

## 12. n8n surface

n8n appears as an **adapter/integration surface**, not as the main cockpit.

Display:

- configured/not configured;
- workflow catalog;
- last observed receipt;
- adapter health;
- imported workflow version;
- allowed event schema.

Do not display n8n execution as canonical evidence unless it points back to the originating GitHub/SHE evidence.

The current bridge remains inert when its webhook is not configured.

## 13. Research surface

Research lanes must be visually separated from production truth.

Each lane identifies:

- hypothesis;
- source/research object;
- experiment;
- current evidence;
- confidence;
- integration status;
- promotion gate.

Examples include:

- Bifrost;
- Hindsight;
- Gravitee;
- Temporal;
- Langfuse;
- Phoenix;
- complexity providers;
- Paper2Agent;
- other FOSS procurement/research lanes.

A research result cannot silently become a production dependency.

## 14. Responsive UX

### Desktop

- persistent left navigation;
- compact global status header;
- main analytical canvas;
- optional right evidence drawer.

### Tablet

- collapsible navigation;
- two-column cards;
- tables become horizontally scrollable;
- graph remains interactive.

### Mobile

- bottom navigation for primary destinations;
- stacked cards;
- evidence drawer becomes full-screen;
- charts default to summary + expand;
- destructive/write actions are absent from the read-only cockpit.

## 15. Accessibility and interaction rules

Minimum target:

- keyboard navigation;
- visible focus;
- semantic headings;
- accessible table structure;
- chart summaries available as text;
- status conveyed by text/icon, not color alone;
- reduced-motion support;
- high-contrast partial/unverified states;
- links expose destination purpose.

## 16. Static mirror contract

The same snapshot must be consumable by GitHub Pages.

The static build MUST:

- require no provider credentials;
- render without Hex;
- render without n8n;
- preserve snapshot/provenance metadata;
- expose the same information architecture in read-only form;
- fail closed if the snapshot schema is invalid.

## 17. Free-scope deployment contract

Preferred order:

1. Vercel interactive SHE;
2. GitHub Pages static mirror;
3. Hex optional research consumer;
4. n8n optional adapter;
5. Render remains reference/template unless a genuinely free path is verified.

No external service is allowed to become a hidden collection dependency.

## 18. UI state matrix

| State | Visual treatment | Meaning |
|---|---|---|
| COMPLETE | positive/neutral | evidence boundary complete |
| PARTIAL_CONTINUATION_REQUIRED | prominent warning | more bounded corpus work remains |
| PARTIAL_BOUNDARY | warning | known boundary limits interpretation |
| FAILED | error | observed execution failure |
| UNVERIFIED | neutral warning | no authoritative evidence yet |
| STALE | subdued warning | snapshot/build freshness exceeded |
| UNKNOWN | neutral | insufficient evidence; do not infer |

## 19. Acceptance gates

The UI/UX implementation is ready for promotion only when:

- [ ] every displayed metric maps to a snapshot;
- [ ] source SHA is globally visible;
- [ ] partial data is impossible to mistake for complete data;
- [ ] no missing value becomes synthetic zero;
- [ ] COMMITTED/EXECUTED/VALIDATED/PROMOTED remain distinct;
- [ ] operator/research/forensic journeys are all navigable;
- [ ] provenance is one interaction away;
- [ ] relationship graph supports evidence inspection;
- [ ] architecture source/render provenance is visible;
- [ ] n8n is clearly marked optional;
- [ ] static Pages build works from the same snapshot;
- [ ] Vercel can render without Hex;
- [ ] accessibility checks pass;
- [ ] responsive layouts pass;
- [ ] no credentials are required by the read-only UI;
- [ ] deterministic snapshot fixtures exist for tests;
- [ ] runtime claims are backed by observed evidence.

## 20. Implementation order

```text
1. Snapshot fixture + schema validation
          ↓
2. Read-only shell + global provenance header
          ↓
3. Overview + Operations
          ↓
4. Provenance drawer
          ↓
5. Effectiveness + Moneyball
          ↓
6. Relationships graph
          ↓
7. Experiments / Research
          ↓
8. Architecture viewer
          ↓
9. n8n adapter status/catalog
          ↓
10. Pages static mirror
          ↓
11. accessibility / responsive hardening
          ↓
12. observed runtime validation
```

This order deliberately makes the UI useful before the historical corpus is complete while preventing the UI from hiding evidence gaps.
