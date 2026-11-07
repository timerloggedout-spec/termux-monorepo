# T.A.K. — Taktikal Awareness Kit
## Repository-native situational awareness and OODA decision-support architecture

**Status:** architecture proposal; not a claim that every collector, feed, or dashboard is deployed  
**Lens identity:** `tak` — registered in `docs/ops/LENS-FRAME.md`  
**Name:** Taktikal Awareness Kit (T.A.K.; owner-resolved K spelling)  
**Primary role:** evidence-backed common operating picture (COP) for repository, agent-fleet, and approved procurement/registration intelligence.

## 1. Executive definition

T.A.K. is the repository's shared awareness lens: it holds entities, tracks, relationships, and events on one time-aware picture so the team can answer:

- What is happening now?
- What changed, where, and when?
- Which actors, repositories, proposals, agents, or external entities are connected?
- What is known, inferred, disputed, stale, or unknown?
- Which change deserves attention next, and what evidence supports that judgment?

T.A.K. is **not** a new orchestrator, autonomous commander, task ledger, scoring engine, or duplicate data lake. It is a read/compose/interpret layer over existing evidence producers and canonical stores. It informs the existing GitHub Agentic Collaboration control plane; it does not replace or bypass it.

## 2. Naming and source doctrine

The repository's registered lens defines T.A.K. as **Taktikal Awareness Kit**, with the K spelling intentionally distinguishing the fleet's concept from the U.S. Government Team Awareness Kit / Android Tactical Assault Kit namesake. The namesake is a reference domain only; its proprietary or government-specific content is not imported as our doctrine.

The registered lens already establishes:
- one shared picture of entities, tracks, and events: position + time + state;
- awareness, not per-item scoring;
- candidate picture surfaces: dispatch-tree, tracking, and telemetry pages (candidate bindings, not yet formal bindings);
- scope seed #1: actor-network emergence signals from procurement and registration data;
- emergence enters unvalenced; any later competitive SWOT dual-valence is assigned from evidence and remains visible as a dated track change.

This architecture elaborates those established points. It does not silently promote candidate surfaces to canonical T.A.K. implementations.

## 3. Military-derived concepts, adapted with boundaries

### 3.1 Common operational picture → shared repository picture

Military COP doctrine emphasizes a shared, relevant, current picture assembled from common data while allowing views to be tailored to the user's role and information needs. TAK's public product material illustrates interoperable clients, data feeds, shared map objects, and server-assisted or local sharing.

**Repository adaptation:** build one canonical evidence-backed picture with multiple projections:
- operator cockpit: portfolio state, risks, decisions needed;
- lane view: active work, dependencies, owners, blockers, freshness;
- repository view: commits, PRs, issues, branches, releases, workflows;
- actor-network view: organizations/entities, registrations, awards, and evidenced relationships;
- agent-fleet view: provider/model/agent activity, run outcomes, handoffs, and review states.

The picture is logically shared; presentation is tailored. Views must not fork the underlying truth.

### 3.2 OODA → evidence-to-outcome feedback cycle

Use Boyd's Observe–Orient–Decide–Act as a recurring, overlapping feedback process, not a four-step waterfall.

| OODA phase | T.A.K. responsibility | Repository-native inputs / outputs |
|---|---|---|
| **Observe** | Collect and receipt changes without prematurely interpreting them. | GitHub events and bounded API reads; workflow/run outcomes; repo snapshots; approved procurement/registration crawls; source receipts. |
| **Orient** | Correlate evidence into a time-aware, uncertainty-preserving picture. | RIDP evidence/cache; Context Relationship Graph; entity resolution; timelines; freshness, coverage, provenance, conflicts, and competing hypotheses. |
| **Decide** | Present ranked attention candidates, alternatives, impact, confidence, and missing evidence. | Human-reviewed decision cards; priority rationale; dependency impact; explicit decision owner and authorization boundary. |
| **Act** | Route approved work through existing control-plane workflows; capture the result. | Existing Agentic Collaboration conductor, issue/PR workflows, authorized collectors, tests, and review. Outcome events feed the next Observe cycle. |

**Critical design rule:** Orient is not optional. Raw events do not become facts about intent. Every interpretation must retain the observations and assumptions that produced it. A fast but ungrounded decision is not a successful loop.

### 3.3 Mission command → decentralized execution under explicit intent

Adapt the useful software-team principle: teams can act independently inside a clear objective, scope, and permission boundary. T.A.K. can expose intent, dependencies, constraints, and current state; the existing conductor and repository permissions determine who may execute what.

T.A.K. must never:
- grant credentials or expand token scopes;
- authorize merges, deployments, releases, or destructive actions;
- convert an inference into an instruction;
- silently reassign ownership or override an active claim;
- initiate external outreach or procurement action without explicit authorization.

### 3.4 Continuous assessment → feedback and recalibration

Every material action should feed an observed outcome back into the picture. Separate task completion from correctness, integration, regression, and resource cost. Record unsuccessful attempts and reversals; do not rewrite the timeline to make the final state look inevitable.

## 4. System placement

```text
                  APPROVED EXTERNAL SOURCES
        procurement / registrations / public records
                         |
                         v
GITHUB + CI ---> existing collectors / event observers <--- agent fleet
                         |
                         v
               RIDP evidence data plane
       receipts · immutable evidence · cache · freshness
                         |
              +----------+-----------+
              |                      |
              v                      v
     Context Relationship      Existing repo/ops
       Graph (CRG)              state projections
              |                      |
              +----------+-----------+
                         v
              T.A.K. awareness model
       entity tracks · event timeline · COP projections
       uncertainty · emergence · relationships · alerts
                         |
             human decision / prioritization
                         |
                         v
          EXISTING Agentic Collaboration
        claims · dependencies · routing · execution
          review · integration · permissions
                         |
                         v
               outcomes / new observations
                         +--------------------> Observe
```

**Ownership boundaries**
- **RIDP:** source acquisition evidence, freshness, cache and reusable context. It is the data plane.
- **CRG:** repository-native relationship graph and evidence-linked navigation.
- **T.A.K.:** domain lens and awareness projections over those sources.
- **Agentic Collaboration:** control plane for claims, coordination, execution, review, and integration.
- **SHE / ATES / dispatch-tree / tracking / telemetry:** existing measurement and state surfaces; T.A.K. consumes their supported outputs and only claims a formal binding after it is recorded.

## 5. Canonical picture model

T.A.K. should be an append-only evidence/event model with rebuildable projections, not a mutable spreadsheet of "current truth".

### 5.1 Core records

**Entity**
- `entity_id`: stable internal identifier;
- `entity_type`: repository, organization, person/agent identity, provider, model, proposal, issue, PR, workflow, procurement entity, registration, award, or other declared type;
- `identifiers[]`: source-scoped identifiers; never merge solely on name similarity;
- `display_name`: presentation label;
- `status`: active, inactive, candidate, unresolved, or unknown;
- `first_seen_at`, `last_seen_at`.

**Observation**
- `observation_id`, `entity_id`, `predicate`, `value`;
- `source_id`, `source_uri`, `captured_at`, `observed_at`;
- `source_version` / source SHA or cursor when available;
- `collector_id`, `method`, `coverage`;
- `evidence_hash`, `license_or_access_basis`;
- `epistemic_status`: observed, inferred, reported, disputed, or unknown.

**Relationship**
- `subject_entity_id`, `predicate`, `object_entity_id`;
- `valid_from`, `valid_to`, `recorded_at`;
- supporting observation IDs; confidence and resolution state;
- relationship changes are events, not destructive overwrites.

**Track event**
- event ID, entity/relationship IDs, event time, ingestion time;
- prior state → new state;
- evidence references, reason, actor/collector, and schema version.

### 5.2 Evidence and uncertainty are first-class

Every rendered claim must be traceable to one or more observations. The UI and APIs distinguish:
- **VERIFIED:** direct source evidence with a resolvable reference;
- **OBSERVED:** source reported the value; independent truth not asserted;
- **INFERRED:** derived relationship or interpretation with method and confidence;
- **CANDIDATE:** plausible link awaiting validation;
- **DISPUTED:** sources conflict; show both readings and provenance;
- **STALE:** last evidence exceeds its declared freshness window;
- **UNKNOWN / NOT ESTABLISHED:** evidence absent; never convert absence into zero or false.

Confidence is not a substitute for provenance. A high-confidence inference remains an inference.

### 5.3 Time and change

Store source event time separately from capture/ingestion time. Keep superseded values and conflict records. Every projection declares its "as of" timestamp and source coverage. A late-arriving event must not silently rewrite historical ordering.

## 6. Scope seed #1 — actor-network emergence

The registered T.A.K. lens names actor-network emergence detection over procurement and registration data as its first scope seed. Initial source candidates include SAM.gov procurement records and other approved procurement/registration sources.

Detection should identify evidence-bearing signals such as:
- a newly observed entity or registration;
- a newly observed award, solicitation, or procurement relationship;
- a newly observed link between previously separate entities;
- a material change in a known entity's attributes or relationship network;
- repeated appearances that suggest an emerging cluster.

A signal is **not** proof of a strategic relationship, intent, capability, or affiliation. Name collisions, subsidiaries, shared addresses, intermediaries, and incomplete records must remain explicit resolution risks. Keep contradictory source records visible.

The repeat-crawl / change-detection / version-pinned ingest concept in Issue #4496 is a relevant dependency candidate. Its filing describes a proposed pipeline and acceptance evidence; it is not, by itself, proof that the pipeline is already deployed.

### 6.1 Composition with competitive SWOT

A newly emerged actor network enters T.A.K. unvalenced. If a later filing uses a competitive frame, the existing lens doctrine requires dual valence (threat and opportunity) on the same track. The conversion motion is a dated, evidenced state transition—not a silent relabel. T.A.K. displays the track; the SWOT lens evaluates it.

## 7. Event-to-awareness pipeline

1. **Acquire:** use existing authorized collectors and incremental event observers; avoid per-view re-fetches.
2. **Receipt:** record source, capture time, cursor/version, collector, scope, and evidence hash.
3. **Normalize:** map source-specific records to versioned entity and relationship types; preserve raw-source identifiers.
4. **Resolve:** deterministic identifier matches first; candidate/fuzzy matches remain candidates until verified.
5. **Diff:** detect new, changed, missing, superseded, and conflicting observations.
6. **Orient:** update bounded graph/timeline projections and compute freshness/coverage; attach explicit reasoning to derived signals.
7. **Surface:** generate role-specific COP views and actionable attention cards, with evidence links and uncertainty.
8. **Decide:** human/operator selects, defers, rejects, or requests more evidence.
9. **Route:** existing Agentic Collaboration handles authorized execution and review.
10. **Assess:** ingest outcome and compare expected versus observed result; update the next cycle.

## 8. Alerting and prioritization

An alert is useful only if it explains:
- what changed;
- why it matters to a declared objective;
- what evidence supports the signal;
- how fresh and complete that evidence is;
- what is uncertain or contradictory;
- what dependency or owner is affected;
- what decision, if any, is requested.

Use a transparent prioritization model with separate dimensions (impact, urgency, confidence, freshness, reversibility, and dependency fan-out). Do not collapse them into a mysterious single "threat score". Missing data must lower confidence or widen uncertainty, not create a false alarm.

## 9. Resilience, security, and governance

- Least-privilege, source-specific collection; no credential or session material in evidence records.
- Respect source terms, access restrictions, rate limits, retention rules, and applicable privacy requirements.
- Treat all external records and agent output as untrusted data, never executable instructions.
- Partition views by authorization and sensitivity; a shared picture does not mean every user can see every source.
- Keep immutable evidence references and auditable transformations; never store secrets or unnecessary personal data.
- Show degraded/offline/stale states explicitly. A disconnected feed is not an empty feed.
- Provide exportable snapshots with schema version, generated time, source coverage, and source SHAs.
- Keep a human-readable fallback report/table when live UI or network access is unavailable.

## 10. Delivery sequence

| Phase | Deliverable | Exit evidence |
|---|---|---|
| 0 — Contract | T.A.K. architecture, entity/observation/relationship/event schema, source register, freshness policy | Schema validation; no unsupported status promotion; source-to-claim traceability tests |
| 1 — Repository picture | Read-only projection of existing GitHub, CI, dispatch-tree, tracking, telemetry, and CRG evidence | One pinned SHA/run cohort; source coverage and stale-state visible; no duplicate collectors |
| 2 — Procurement emergence | Integrate approved procurement/registration feeds through the existing crawl/receipt pipeline | Two or more registered sources; versioned diffs; entity-resolution conflicts preserved; reproducible dataset version |
| 3 — OODA workbench | Evidence-backed change cards, timelines, dependency views, and operator decisions | Decisions cite evidence and owner; actions route only through existing conductor |
| 4 — Calibration | Backtest emergence signals and alert usefulness; measure false positives, missed changes, freshness, and decision latency | Frozen evaluation set, adjudicated labels, reproducible metrics; no claim of predictive quality without measured results |

## 11. Metrics

Measure system performance without rewarding noise:
- source freshness and coverage by feed;
- time from source change to receipted observation and to surfaced signal;
- duplicate acquisition avoided / cache and conditional-read rates (from RIDP telemetry);
- entity-resolution precision/recall on an adjudicated sample;
- conflict rate and unresolved identity rate;
- alert precision, recall, and operator-dismissal reasons;
- evidence-link completeness and stale-claim rate;
- time from signal to human disposition;
- action outcome, integration yield, and regression rate;
- resource use per validated signal / useful decision.

Do not report zero when a metric is uninstrumented. Do not claim time saved or predictive accuracy until a measured baseline and comparison exist.

## 12. Acceptance criteria

- T.A.K. consumes existing evidence sources and does not become a second collector, data lake, or conductor.
- Every visible signal has source provenance, capture time, source version, and an evidence link or explicit unavailable state.
- Observed facts, inferences, candidates, disputes, stale data, and unknowns remain distinguishable end-to-end.
- Entity resolution is explainable and conservative; ambiguous matches do not silently merge.
- New and superseded values remain auditable; snapshots can be rebuilt from pinned evidence.
- Candidate picture surfaces remain candidates until formally bound.
- Competitive SWOT tracks preserve dual valence and dated conversion events.
- T.A.K. emits decision-support only; all writes and consequential actions remain under existing authorization and Agentic Collaboration controls.
- Read-only pilot demonstrates repository awareness before procurement feeds are admitted.
- All metrics are sourced from actual telemetry; uninstrumented values remain unknown.

## 13. Reference material

### Repository doctrine
- [Lens Frame — registered T.A.K. doctrine](../ops/LENS-FRAME.md)
- [Lens Template Trigger](../ops/LENS-TEMPLATE-TRIGGER.md)
- [DoE Family — T.A.K. scope seed and emergence → SWOT composition](../ops/DOE-FAMILY.md)
- [Agent Team Development Lanes](../ops/AGENT-TEAM-DEVELOPMENT-LANES.md)
- [Issue #4496 — repeat-crawl ingest/store proposal](https://github.com/timerloggedout-spec/termux-monorepo/issues/4496)

### External research (reference, not imported doctrine)
- [TAK.gov — Products and client ecosystem](https://tak.gov/products): public description of ATAK/WinTAK/WebTAK families and shared situational-awareness products.
- [TAK.gov — operational overview](https://tak.gov/): public description of shared maps, data feeds, local/server-assisted sharing, and planning.
- [U.S. Marine Corps, MCDP 6 — Command and Control](https://www.marines.mil/Portals/1/Publications/MCDP%206.pdf): OODA as a feedback-oriented command-and-control model.
- [U.S. Army, DSCA OODA loop](https://www.army.mil/article/185962/finding_the_right_planning_tools_for_defense_support_of_civil_authorities): multi-actor effects, situational awareness, and orientation/expectations.
- [U.S. Army FM 3-0 (2025), shared understanding and COP](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN43326-FM_3-0-000-WEB-1.pdf): shared understanding, tailored COP, digital/analog resilience.
- [U.S. Army War College, Untying the OODA Loop](https://warroom.armywarcollege.edu/articles/untying-ooda-loop/): contemporary discussion of recognition speed and the risks of collapsing feedback into prediction/action.

---
**Design posture:** faster awareness through better evidence flow, not faster automation through less judgment.
