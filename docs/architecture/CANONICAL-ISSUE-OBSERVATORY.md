# Canonical Issue Observatory

**Implements:** #192

## Purpose

The Observatory is the issue lifecycle evidence plane. It removes the assumption that an issue becomes actionable only because a label was added or Jules was invoked.

`Issue → normalize → relate → refine → route → execute → verify → learn`

GitHub remains the system of record. The Observatory produces **candidates and evidence**, not autonomous facts.

## Evidence graph

Every observed object is keyed by native identity plus timestamp and source:

- Issue / sub-issue / dependency
- Issue comment / review / discussion
- Pull request / commit / changed file
- Workflow / run / job / step / artifact
- Deployment / published surface
- Repository / fork / star-derived research item
- Agent/provider/model execution and attribution evidence

Relations include `same_as`, `near_duplicate`, `implements`, `blocks`, `blocked_by`, `mentions`, `changes`, `touches`, `regresses`, `supersedes`, `depends_on`, `resembles`, and `researches`.

## Similarity + refinement plane

Labels are routing hints, never the primary matcher. Candidate relations are ranked from independent signals:

1. Exact native references: issue/PR/file/commit IDs and URLs.
2. Shared changed paths and symbols.
3. Shared explicit issue/PR references.
4. Normalized lexical similarity of title/body/comments.
5. Shared labels, milestones, actors, workflows, and provider families.
6. Temporal proximity and lifecycle compatibility.

A candidate must carry `score`, `evidence[]`, `source_timestamp`, and `confidence`. High similarity is **not** equivalence. Autonomous merge/close decisions require stronger evidence and existing repository gates.

Sub-issues are first-class work units. A parent may refine into independently verifiable slices; each slice retains lineage to the parent and related evidence.

## Agent routing

Jules is a specialist/escalation worker, not the issue control plane. Routing should select a worker by expected marginal value using the existing evaluation/Moneyball evidence: capability fit, historical correctness, integration success, cost/latency, current capacity, and context availability. No provider receives authority merely from a label.

## Adaptive feedback cycle

Every action follows:

`OBSERVE → CLASSIFY → WAIT/STEER/RETRY → VERIFY → PROMOTE/QUARANTINE → FEED FORWARD → REPEAT`

Verification traverses `run → jobs → steps/logs → artifacts → receipts → resulting SHA/status`. A green workflow is not sufficient evidence of a correct outcome.

## Accuracy watchdogs

The Observatory is itself watched by:

- schema/contract validation;
- source-count and freshness checks;
- deterministic replay of the matcher on bounded fixtures;
- regression comparison against the last known-good Observatory implementation;
- workflow-run incident watcher;
- artifact/receipt presence checks;
- human-review queue for low-confidence or conflicting relations.

Provider-generated Wiki/DeepWiki/Devin context is discovery evidence only. Repository source, GitHub timeline, review records, workflow evidence, and approved documentation are authoritative for change decisions.

## Hex + Wolfram

**Hex** is the analytics/evidence surface: cohorts, dashboards, Moneyball leaderboards, proposal SLA distributions, similarity precision/recall experiments, workflow health, agent/provider ELO, and waste/retry analysis.

**Wolfram** is a computational verification candidate: statistical significance, clustering/distance functions, anomaly detection, Bayesian/uncertainty calculations, optimization, graph measures, and reproducible mathematical checks. The current Wolfram connector was unavailable during this implementation probe, so no runtime Wolfram result is asserted here.

Control boundary: `GitHub evidence → Hex/Wolfram analysis → governed recommendation → GitHub workflow/operator action`.

## Proposal decision SLA

Proposal turnaround is evidence-driven, not a fixed promise. The Observatory records:

`opened → first triage → research complete → decision requested → consensus/review → accepted/rejected/deferred → implementation → verification`

Expected time is estimated from impact class, dependency count, research uncertainty, reviewer availability, and historical cycle time. P0 safety/production blockers outrank calendar age; uncertain/high-impact proposals receive additional research before a final decision. Deferred proposals require an explicit reason and next review condition.

## Research frontier

Starred/added repositories are **research candidates**, not dependencies. The repository investigation lane should record source repo, observed capability, license/compatibility notes, integration pattern, evidence date, adaptation value, and disposition (`adopt`, `adapt`, `watch`, `reject`). `conversational_steganography_fork` belongs in this evidence lane for investigative cipher/obfuscation analysis and future-layer research; it does not authorize operational concealment or bypasses.

## Documentation compression

`AGENTS.md` is the compressed routing map: domain-specific notation expands to canonical paths and contracts. It should not duplicate subsystem prose.

`README.md` is the 1337-style public orientation surface: compact, high-signal, source-linked, and readable. Display dialect must never replace canonical paths or provenance.

## Deployment/publication surfaces

Vercel, GitHub Pages, Render, Cloudflare/Cloudflare Pages, GitHub Wiki, DeepWiki/Devin Wiki, and Hex are separate surfaces. Provider availability is not deployment evidence; reachability is not proof of the expected SHA. Every published surface should expose or retain source SHA, build timestamp, and ownership evidence where the provider supports it.
