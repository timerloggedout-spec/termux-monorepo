# Common Knowledge Plane — Research-Astute ↔ Termux-MonoRepo

- **Status:** integration contract; adapter implementation remains separately verifiable
- **Research authority:** Research-Astute domain repositories
- **Operational/integration authority:** Termux-MonoRepo
- **Purpose:** one navigable, provenance-preserving knowledge plane across disciplines, opportunities, projects, software artifacts, and program admissions without flattening their source authority.

## 1. The model

Use a federated knowledge architecture, not one giant taxonomy and not a pile of disconnected indexes:

1. **Domain ontology layer (canonical research content).** Research-Astute owns discipline-specific concepts, definitions, taxonomies, competency frameworks, evidence claims, and crosswalks. Each domain can retain its own terminology and versioning.
2. **Shared vocabulary layer.** The repository's notation-sets work supplies stable semantic keys, canonical labels, aliases, cross-domain analogues, domain-specific syntax, provenance, and lifecycle. See `docs/proposals/active/notation-sets/ITEMS.md` (NSE-003 and NSE-005).
3. **Relationship/evidence layer.** The Context Relationship Index connects repository artifacts and bounded GitHub history through verified metadata edges. It is an evidence graph for repository context, not a disciplinary ontology or unrestricted knowledge graph.
4. **Operational navigation and retrieval.** ArchWiz indexes, generated `workspace/llm_map/` projections, and semantic search help discover material. They are projections and retrieval aids; canonical source files and registries remain authoritative.
5. **Opportunity and delivery layer.** The challenge coordinator, opportunity-cycle machinery, PRs, releases, and runtime receipts connect research concepts to funded work and delivered outputs.

## 2. Existing integration points (reuse, do not fork)

| Existing surface | Role in the shared plane | Authority boundary |
|---|---|---|
| `docs/proposals/active/notation-sets/ITEMS.md` | Living vocabulary and cross-domain semantic anchors (NSE-003/NSE-005) | Proposal/specification until implementation is separately accepted |
| `archwiz/CONCEPT_INDEX.md`, `POINTER_INDEX.md`, `METHODOLOGY_INDEX.md`, `TOOL_INDEX.md` | Operational concept, pointer, method, and tool navigation | Navigation catalogs; do not duplicate definitions here |
| `docs/icm/objects/knowledge/context-relationship-index.md` | Contract for verified/candidate relationship evidence | Metadata-only repository graph; source spec wins |
| `config/context_relationships/schema.json` | Node, edge, evidence, and relationship vocabulary | Canonical schema for the Context Relationship Index |
| `workspace/llm_map/context_relationships/` | Generated relationship records, manifest, reports, checkpoint | Generated; never hand-edit |
| `docs/icm/objects/knowledge/navigation-and-indexes.md` | Routing to authoritative indexes and generated maps | Navigation contract |
| `docs/ops/GRAPH-MATRIX.md` | Commits/issues/PRs/branches linkage integrity | GitHub linkage census only; not a semantic knowledge graph |
| `ops/challenge/coordinator.json` | Canonical opportunity and challenge records | Single-writer opportunity record |
| `docs/ops/OPPORTUNITY-CYCLE.md` and `ops/opportunities/cycles/` | Prep-gate receipts, readiness verdicts, and cycle history | Derived readiness evidence; no external submission |
| `ops/que/feeds/opportunity-priority.json` | Prioritized opportunity projection | Generated feed; do not hand-edit |

The Context Relationship Index's own card explicitly says its generated
artifacts are not hand-edited and that candidate edges are not verified facts.
The Graph Matrix has a separate, narrower job. Do not overload either.

## 3. Canonical concept and evidence envelope

A domain record published to the hub should carry:

- `concept_id` or `resource_id` (stable, globally unique within its namespace);
- `lane_id`, domain, preferred label, definition, and concept type;
- parent/related concept IDs and typed relationship predicates;
- source framework or primary-source URI, source version, retrieval/observation date;
- authoring organization/repository and immutable commit or version reference;
- evidence class: `asserted`, `source_attributed`, `hypothesis`, or `derived`;
- confidence/rationale, validation state, unresolved questions;
- license/rights, privacy classification, and lifecycle state;
- optional crosswalk target plus mapping type and equivalence strength.

A hub digest item additionally receives an `item_id` and references one or more
canonical records. Do not copy a domain definition into multiple registries;
link to its canonical record and preserve its version.

## 4. Relationship rules

Use typed, directional predicates. Initial education predicates are listed in
the sponsored/public-goods lane charter. Common cross-lane predicates may
include:

- `broader_than` / `narrower_than`
- `related_to` (non-equivalence)
- `requires_competency`
- `supported_by_evidence`
- `implemented_by`
- `evaluated_with`
- `funded_by`
- `admitted_to_program`
- `adopted_by`
- `supersedes` / `superseded_by`

Every edge carries provenance and evidence status. A cross-domain analogue
must never be silently promoted to semantic equivalence. Funding, admission,
technical validation, and adoption are separate relations and state machines.

## 5. C13 integration: use the established grant pipeline

The Digital Promise / K-12 AI Infrastructure Program request is already
registered as **C13** in `ops/challenge/coordinator.json`. Its integration
path is:

`C13 coordinator record → opportunity-cycle ingest → QUE priority feed →
entries/c13 prep manifest + submission-requirements census → cycle readiness
receipt → project/PR/release evidence → domain knowledge and impact digest`.

Canonical paths:

- `ops/challenge/coordinator.json#C13` — source record and owner decision.
- `docs/ops/OPPORTUNITY-CYCLE.md` — state machine and prep-first rules.
- `entries/c13/prep-manifest.json` — required stage 0–4 artifact receipts.
- `entries/c13/submission-requirements.json` — requirement census, capacity,
  route-around, landing-time, and first-send evidence.
- `ops/opportunities/cycles/` and `ops/opportunities/cycle-ledger.jsonl` —
  generated readiness history.
- `ops/que/feeds/opportunity-priority.json` — derived priority projection.

**Observed 2026-11-16:** latest cycle
`cyc-20261116T080046Z-43827809644` reports C13
`PREP_INCOMPLETE`. The prep manifest and census are missing; stages 0–4 are
unreceipted and stages 5–7 blocked. The coordinator's separate decision
remains `candidate — VIABLE, eligibility CONFIRMED`, awaiting Manager/owner
slate call. This contract does not change that decision. Only source-backed
artifacts may discharge the gates; no synthetic receipts or inferred
owner-capacity confirmations.

## 6. Google Fairwind Program admission

Google's official name is **Fairwind Program** (singular, not “FairWinds”).
This is a restricted cyber-defender access/admission program, not a grant
or a general cloud-credit program.

Official program page: https://deepmind.google/fairwind-program/
Google launch announcement (2026-09-02):
https://blog.google/innovation-and-ai/technology/safety-security/fairwind-program/

The program describes early access to advanced cyber-defense models and
CodeMender for vetted defenders. Google prioritizes governments, national
cyber authorities, critical-infrastructure operators, and core technology
platforms; it also welcomes academic labs focused on defensive benchmarking.
Applicants are subject to organizational due diligence and must demonstrate
a proven ethical security/research record.

The official application path is to contact the organization's Google Cloud
account team. If the organization is not yet a Google Cloud customer, Google
directs it to the Cloud getting-started path. Admission is controlled:
access is limited to internal cybersecurity, incident-response, or
penetration-testing teams; user-level authentication, phishing-resistant
MFA, access controls, and usage tracking are required. Access may not be
shared, redistributed, or sold. Permitted dual-use activity is limited to
authorized defensive research such as threat simulation, reverse
engineering, malware analysis, and defensive benchmarking; malicious
activity is prohibited.

### Admission workstream

Track Fairwind separately from grant C13:

1. Identify the legal applicant and Google Cloud customer/account-team relationship.
2. Assemble organization profile, security history, defensive research track
   record, and evidence of ethical operations.
3. Define the eligible internal team, named users, user-level authentication,
   phishing-resistant MFA, access-control and audit/usage-monitoring plan.
4. Define authorized defensive use cases, target ownership/authorization,
   isolation boundaries, data handling, and prohibited-use controls.
5. Request admission through the Cloud account team and track the response
   as an external decision; do not claim partner status until Google confirms it.

**Initial fit assessment:** Research-Astute's research and Termux-MonoRepo's
software/security work may provide relevant defensive research and core
technology-platform evidence, but the official criteria do not establish
that either organization qualifies. Priority is given to high-resilience
defenders; organization eligibility, Cloud account status, security history,
and operational controls require evidence. This is a candidate admission
track, not an asserted acceptance.

### Program admission state model

`DISCOVERED → SOURCE_VERIFIED → ORGANIZATION_ASSESSED →
CONTROL_GAPS_IDENTIFIED → ACCOUNT_TEAM_CONTACTED → APPLIED/REFERRED →
UNDER_REVIEW → ADMITTED/DECLINED/NOT_ELIGIBLE → ACCESS_GOVERNED →
RENEWED/SUSPENDED/EXITED`.

The admission record is separate from credentials and secrets. Never place
keys, tokens, private vulnerability details, or sensitive customer data in
the public research registry.

## 7. Operating boundary

Research-Astute publishes domain records and evidence feeds; Termux-MonoRepo
validates schemas, links evidence to implementation and delivery, and
publishes operational receipts. The hub should consume public/read-only
research evidence by default. Write access, private data exchange, program
credentials, and sponsor reporting are separately authorized integrations.

No external program acceptance, Google Cloud account-team contact, C13
submission, award, or partner commitment is implied by this document.
