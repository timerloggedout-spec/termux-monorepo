# Gemini Visual Language — canonical tree/DAG packet (viz)

Provenance: extraction ↦ Gemini lane [MUSEai]@{role:{gemini}}, owner order
2026-10-30, from Gemini Notebook `termux-monorepo`
(`fcf38c29-61d1-41cb-ac25-c7a7b1e85bcc`), extract-first via notebook search
(alias-aware). Routed ↦ viz-dispatch-tree as the canonical tree/DAG visual
language for the fleet's web surfaces.

**Rule: REUSE, ¬ reinvent.** Any lane rendering trees, DAGs, or state graphs
on a web surface designs in this language; deviations cite a reason in the
PR that introduces them.

## 1. Radial visual language — Orbital Syntax

Source: "Designing Radial Visual Language" (2026-10-04),
gemini.google.com/app/9a146c1da1517452

- Orbital Syntax: Anchor Node / Orbital Modifiers / Relational Tethers
  (solid = direct, dashed = passive) / Macro-Gestalt ring.
- Focal Locking + Semantic Zoom.
- AR/HUD foveated zoom spec: Peripheral >5° ring-only · Parafoveal 2–5°
  tethers · Foveal 0–2° QR-matrix unpack; gaze-break = GC.
- X-ref: Linguist Admin (chat cb34a236) — phonetics ↦ radial geometry.

## 2. DAG branch algorithms & viz

Source: "DAG Branch Algorithms & Viz" (2026-10-02),
gemini.google.com/app/badb74d8c3f98389

- LCA incl. criss-cross; Tarjan offline; bitset reachability; Kahn topo.
- Sugiyama layered layout.
- 3-way merge matrix + CRDT (LWW graph / op-DAG append).
- Markov propagation through DAG ranks.

## 3. Markov tree viz — three architectures

Source: "Exploring Markov Tree Viz" (2026-10-01),
gemini.google.com/app/230640bf630f376f

- Unfolded State Trees (glow = probability, edge = transition).
- Collapsed State-Transition Graphs (steady-state heatmap).
- Particle Flow walkers.
- Interactive Markov Sandbox (Idle / Scan / Process / Sync).
- ArchWiz DAG/Markov Trunk Explorer: L[Past] → C[NOW gate] → R[Future];
  React + Canvas implementation notes.

## 4. Tron ArchWiz SVG DAG tree

Source: "Tron ArchWiz SVG DAG Tree" (2026-10-02),
gemini.google.com/app/45828b54adaf9a49

- Native SVG, framework-free.
- Glow: feGaussianBlur + feComposite — cyan branch / orange dashed merge
  (stroke-dasharray 5 5).
- Cubic Bezier DAG pathing.

## In-repo kin (verified present on master, 2026-10-30)

- docs/graph/CROSS-PLANE-GRAPH.md + graph-edges.schema.json — the
  cross-plane graph this language renders.
- docs/proposals/active/archwiz-markov-trellis-lab ∘
  docs/proposals/active/archwiz-ui-protocol ∘
  docs/proposals/active/archwiz-hyperforge-gemini-review —
  proposal-side ArchWiz work.
- experiments/archwiz-markov-lane — the Markov experiment lane.
- Consumers when scheduled: dispatch-tree ∘ cross-plane graph ∘
  Repo Replay views.

## Search warning (Gemini lane, verbatim discipline)

Gemini search is account-wide, first-list only; ∅-match ≠ absence
(v1sual = 0 hits vs visual = 13); branch-prefixed duplicates are
under-surfaced; leet body forms (ArchW1z / 4rchW1z / 4πchw1z) are
unsearchable. Verify against the notebook list, never search alone.

## Status

Extraction summary as routed — the underlying chats live at the Gemini
app refs above; this record is the fleet-side landing of the packet, not
a transcription of the full chat bodies.
