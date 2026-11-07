# T.A.K. — Common Operating Picture Contract

**Status:** implementation contract v1; source intake and surface binding remain separate gates  
**Lens:** `tak` (registered in `docs/ops/LENS-FRAME.md`)  
**Canonical spelling:** **Taktikal Awareness Kit** (T.A.K.; fleet-owned K-spelling).  
**Primary question:** *What does the picture show now, and what is moving?*

## 1. Purpose and boundary

T.A.K. is the fleet's shared tactical-awareness / common-operating-picture lens. It holds entities, relationships, tracks, observations, and events on one time-aware picture. Its output is awareness, not a score, rank, award, or decision.

This contract operationalizes the existing lens record; it does not replace or silently expand that doctrine. The registered scope seed is actor-network emergence detection over procurement and registration signals. The DoD TAK namesake is a procurement-concept reference only; its doctrine, datasets, interfaces, and operational assumptions are not imported.

## 2. Existing work to compose with

T.A.K. is a **consumer/projection**, not another crawler, repository tracker, telemetry collector, or orchestration system.

| Existing surface / work | T.A.K. relationship | Boundary |
|---|---|---|
| System review RFP-SYSREV-C2, issue [#4496](https://github.com/timerloggedout-spec/termux-monorepo/issues/4496) | Upstream repeat-crawl, ingest, change-detection, conflict-preserving dataset pipeline | T.A.K. consumes pinned dataset versions; it does not duplicate crawl/store work |
| Repo tracking, `repo-tracking/v1` | Candidate operational-state source | Read through its existing feed/contract; do not modify its single-writer output |
| Dispatch-tree feed, `dispatch-tree-feed/v1` | Candidate dispatch/cadence picture source | Preserve its own scope and timestamps; do not reinterpret admission policy |
| Telemetry / ATES / SHE | Candidate provenance and execution-observation sources | Consume pointers and source evidence; do not copy raw traces or invent live state |
| LENS-FRAME.md + LENS-TEMPLATE-TRIGGER.md | Governing lens doctrine and filing stamp | T.A.K. filings use `lens_id: "tak"` and cite the exact picture snapshot |

Candidate surfaces are not automatically bound to T.A.K. Formal binding requires an explicit recorded act by the owning lane. Until then, they remain candidate inputs.

## 3. Picture model

A published picture is an immutable, versioned projection with four canonical collections; tracks are derived views over the time-ordered observations and events:

1. **Entities** — public organizational actors, agencies, registrations, awards, contracts, and actor networks. Natural-person profiling is out of scope for v1.
2. **Relationships** — evidence-backed edges between entities (for example, registered-with, awarded-to, parent-of, or shared-public-identifier). An edge is not asserted from name similarity alone.
3. **Observations** — source-stamped facts as received or normalized from a pinned source dataset.
4. **Events** — append-only changes to the picture: first-seen, relationship-observed, source-value-changed, conflict-detected, state-changed, assessment-added, and superseded.

The machine contract in `TAK-PICTURE.schema.json` defines the v1 envelope. Each record must retain evidence references back to the source dataset version and source row/locator.

## 4. Time, position, and state

- Every picture has `generated_at`; every observation/event has its own source-observed or event time. These are not interchangeable.
- Position is typed. It may be geographic, registry/administrative, workflow, or unknown. Coordinates are optional and only present when a source actually supplies them.
- State is source-backed. Preserve the source value and identify any normalization. Unknown is null/unknown, never inferred from absence.
- A track answers *where/what/when* from its evidence. It does not imply that an entity is currently active merely because it appears in a historical snapshot.
- Conflicting source values remain simultaneously visible as conflicts until a documented resolution/supersession event. Never overwrite one source's value with another.

## 5. Actor-network emergence

The first detection function is **actor-network emergence signals detection** across procurement and registration records.

A candidate emergence signal may be raised when evidence establishes a new entity, registration, award/contract relationship, or previously unseen relationship among known entities. The signal must include:
- the entity/edge affected;
- the first-observed timestamp and source dataset version;
- source evidence references;
- the exact detection rule/version that emitted it;
- whether the signal is observed or derived;
- known coverage gaps and unresolved conflicts.

A signal is not a finding of wrongdoing, intent, affiliation, or risk. Do not infer beneficial ownership, control, collusion, or identity from co-occurrence alone. Name similarity and shared addresses are candidate-link evidence only, not proof.

## 6. Composition with SWOT duality

The T.A.K. picture and SWOT are separate lenses with a defined hand-off:

- A newly emerged actor network enters the picture **unvalenced**. No threat or opportunity reading is assumed at entry.
- When a competitive-frame assessment is actually made, the SWOT duality doctrine requires both threat and opportunity readings on the same entity track.
- The transition is an evidenced, timestamped event. Never silently reclassify an entity or erase its prior reading.
- Outside competitive frames, duality is available but not forced.
- T.A.K. does not perform the SWOT assessment or score the entity; it preserves the evidence and state transition for the consuming lens.

## 7. Data integrity and safety

- **Pinned inputs:** every build identifies the exact upstream dataset version(s), source snapshot hashes, and collector/detector versions.
- **Append-only evidence:** corrections create new observations/events and explicit supersession links; historical evidence is not rewritten.
- **Conflict preservation:** different source claims remain distinct and queryable.
- **No synthetic certainty:** missing values, incomplete crawls, stale feeds, and unknown coverage remain explicit.
- **Idempotency:** event identity is stable for the same source record + rule version + event type; reprocessing must not create duplicate logical events.
- **Privacy:** v1 covers public organizational/procurement records only. Exclude credentials, secrets, private contact data, personal profiles, and raw agent prompts/completions.
- **No autonomous adverse action:** a signal may inform human review or another registered lens; it cannot itself trigger exclusion, accusation, outreach, procurement action, or a security response.
- **No raw-data duplication:** retain stable source references and hashes; the upstream ingestion store remains the source of record.

## 8. Freshness and coverage

Every picture must expose:
- source dataset version and source snapshot digest;
- generation time and source observation window;
- per-source read/capture time;
- coverage status: `complete`, `partial`, or `unavailable`;
- explicit gaps and conflicts;
- detector/rule version.

A partial or unavailable source cannot be represented as a complete picture. A missing source is not an empty population and must not render as zero entities or zero relationships.

## 9. Delivery sequence and gates

| Phase | Deliverable | Gate |
|---|---|---|
| A — contract | This document + JSON Schema | Review contract with source-ingestion and lens owners |
| B — source adapter | Read pinned dataset versions from #4496 output | At least two registered public sources; source receipts and change detection demonstrated upstream |
| C — projection | Deterministic entity/relationship/event projection | Conflict-preserving, idempotent, reproducible output from pinned inputs |
| D — detection | Versioned actor-network emergence rules | Labeled fixtures, false-positive review, source coverage stated |
| E — surface binding | T.A.K. picture view and explicit candidate-surface bindings | Owner-lane binding record; page consumes feed only |
| F — evaluation | Replay and longitudinal quality measures | Precision/recall only when labeled ground truth exists; no fabricated baseline |

The current contribution lands Phase A only. It intentionally does not claim that SAM.gov or any other live source has been connected, that a crawler is running, that a detection model is validated, or that candidate dashboards are formally bound.

## 10. Acceptance criteria for the first executable slice

1. A pinned upstream dataset can be projected twice with byte-identical output.
2. Reprocessing the same source row does not duplicate an event.
3. A changed source value creates a new observation/event and preserves the previous value.
4. Two conflicting sources remain visible without silent winner selection.
5. A new actor-network signal starts unvalenced.
6. A competitive-frame assessment cannot be emitted with only one SWOT valence.
7. Missing/stale source coverage remains explicit and never becomes a zero count.
8. Every entity, relationship, observation, and event can be traced to source evidence and a dataset version.
9. No raw personal profile, credential, prompt, completion, or secret enters the picture.
10. The projection makes no autonomous adverse decision.

## 11. Ownership seams

- Upstream crawl/ingest/change detection/conflict store: issue #4496 and its owning lanes.
- T.A.K. picture contract, projection, and emergence detector: T.A.K. implementation lane.
- Repo tracking, dispatch-tree, telemetry, and ATES source truth: their existing owning lanes.
- SWOT duality and malformedness: `docs/ops/LENS-FRAME.md`.
- Surface presentation: Web Design / dashboard owner after formal binding.

This separation allows concurrent lanes to advance independently while T.A.K. consumes their versioned evidence through stable contracts.
