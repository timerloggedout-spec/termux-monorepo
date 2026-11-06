# T.A.K. — Taktikal Awareness Kit
## Proposal source and research synthesis

**Proposal ID:** `taktikal-awareness-kit`  
**Lens ID:** `tak`  
**Status:** posted for review; architecture-first  
**Owner-resolved name:** Taktikal Awareness Kit (K spelling)

## Problem statement

The repository already has a registered T.A.K. lens describing one shared, time-aware picture of entities, tracks, and events, with actor-network emergence detection over procurement/registration data as scope seed #1. The fleet also has candidate picture surfaces (dispatch-tree, tracking, telemetry), but the lens explicitly says candidate status is not formal binding.

The missing hand-off is a concrete architecture tying source observations, provenance, relationship resolution, freshness, conflict handling, and OODA decision support to the existing repository intelligence and Agentic Collaboration systems—without creating a parallel orchestrator or datastore.

## Owner-provided framing

The operator states that T.A.K. is actively scanning awareness. This proposal treats that as the operational intent and designs the integration contract. It does not claim that specific collectors, external feeds, crawl schedules, or runtime coverage have been independently verified in this filing.

## Research-derived design inputs

1. **TAK/COP systems:** public TAK.gov material describes interoperable clients, shared maps, data feeds, and local/server-assisted information sharing. Adopt the architectural pattern of a common evidence-backed picture with multiple role-tailored projections; do not clone the government product or import its restricted content.
2. **OODA:** Marine Corps MCDP 6 presents OODA as a command-and-control feedback cycle. The cycle is iterative and feedback-rich, not a one-way workflow. Preserve Observe, Orient, Decide, Act as separable responsibilities with feedback.
3. **Multi-actor orientation:** the Army's DSCA OODA adaptation explicitly accounts for multiple stakeholders and their expectations/biases. For repository work, orientation must expose actor/entity relationships, assumptions, and competing interpretations.
4. **COP resilience:** Army FM 3-0 describes a COP as shared relevant information tailored to users, and recognizes analog fallback when digital connectivity is degraded. The repo equivalent is one canonical evidence model, multiple projections, and exportable snapshots/fallback reports.
5. **Human decision authority:** mission-command concepts support decentralized execution under intent and explicit authority. T.A.K. supplies awareness and decision support; the existing Agentic Collaboration control plane retains routing, claims, execution, review, and permission boundaries.

## Existing repository evidence

- `docs/ops/LENS-FRAME.md` registers T.A.K. as the shared tactical-awareness/common-operating-picture lens. It defines entities/tracks/events on one live picture (position + time + state), awareness rather than scoring, candidate picture surfaces, actor-network emergence over procurement/registration records, and emergence entering unvalenced.
- `docs/ops/LENS-TEMPLATE-TRIGGER.md` registers lens ID `tak` and requires a `lens_filing` stamp for T.A.K. filings.
- `docs/ops/DOE-FAMILY.md` repeats the T.A.K. scope seed and the emergence-to-SWOT composition.
- `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md` defines existing Builder, Review, Recon, Experiment, Telemetry, and Synthesis lanes plus evidence linkage and security boundaries.
- Issue #4496 proposes repeat crawls, change detection, receipts, conflict preservation, versioned snapshots, and pinned datasets. It is a proposal, not proof of deployed collection.

## Proposed architecture

See [TAKTIKAL-AWARENESS-KIT.md](../../../architecture/TAKTIKAL-AWARENESS-KIT.md).

T.A.K. is the awareness/lens layer; RIDP is the reusable evidence data plane; CRG provides relationship navigation; the existing Agentic Collaboration conductor is the control plane. T.A.K. does not own a new task queue, credentials, write authority, or collector fleet.

## Scope

- Define versioned entity, observation, relationship, and track-event contracts.
- Define provenance, epistemic status, freshness, coverage, and conflict semantics.
- Compose existing GitHub/CI/agent/dispatch/tracking/telemetry/CRG evidence into read-only repository picture projections.
- Design actor-network emergence detection over approved procurement/registration sources.
- Route decisions only through existing human authorization and Agentic Collaboration workflows.
- Establish evaluation and efficiency metrics before claiming predictive value or savings.

## Out of scope

- Replacing the Agentic Collaboration control plane.
- Replacing RIDP, CRG, repo tracking, dispatch-tree, SHE, or ATES.
- A separate general-purpose database or new collector framework.
- Autonomous execution, merging, deployment, external outreach, or procurement action.
- Treating name similarity, co-occurrence, or an inferred edge as verified affiliation or intent.
- Importing government TAK implementation details or restricted datasets.

## Risks and controls

| Risk | Control |
|---|---|
| Duplicate collectors and stores | Reuse RIDP and existing observers; T.A.K. is a projection/lens. |
| Stale or partial picture | Per-source freshness and coverage; stale/disconnected states visible. |
| False entity merges | Source-scoped identifiers; candidate matches remain unresolved pending evidence. |
| Inference presented as fact | Explicit epistemic status, provenance, confidence, and reasoning. |
| Data conflicts silently overwritten | Append-only observations; explicit conflict/supersession events. |
| OODA reduced to speed-only automation | Human orientation and authorization; outcomes feed back. |
| Control-plane duplication | Existing conductor exclusively owns claims, routing, execution, and integration. |
| Sensitive or unauthorized data | Least privilege, source terms, privacy and retention checks; no credentials in records. |

## External references

- https://tak.gov/products
- https://tak.gov/
- https://www.marines.mil/Portals/1/Publications/MCDP%206.pdf
- https://www.army.mil/article/185962/finding_the_right_planning_tools_for_defense_support_of_civil_authorities
- https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN43326-FM_3-0-000-WEB-1.pdf
- https://warroom.armywarcollege.edu/articles/untying-ooda-loop/
