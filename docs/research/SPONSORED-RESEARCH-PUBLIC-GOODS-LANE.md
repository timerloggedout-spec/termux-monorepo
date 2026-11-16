# Sponsored Research & Public Goods Lane

- **Lane ID:** `sponsored-research-public-goods`
- **Host:** Research-Astute (research and domain work); Termux-MonoRepo (engineering, deployment, integration and operational evidence)
- **Status:** Established as an architectural lane; initial domain pilot identified; no grant application or award is implied
- **Management-hub contract:** publish normalized, provenance-bearing evidence; do not make sponsor portals or dashboards canonical

## 1. Mission

Discover, qualify, incubate, deliver, and sustain multidisciplinary research and open projects that create measurable public value. External sponsors (including foundations, public agencies, philanthropic platforms, research programs, and community funding mechanisms) may fund work, but the lane must also support unfunded research and independently useful public goods.

The lane is not a grant-writing department alone. It connects:

1. research questions and domain knowledge;
2. funding and partnership opportunities;
3. technical and non-technical capabilities;
4. project incubation and implementation;
5. open release and downstream adoption;
6. evidence of educational, scientific, social, or infrastructure value.

## 2. Organizational boundary

| Responsibility | Research-Astute | Termux-MonoRepo |
|---|---|---|
| Domain research and synthesis | Lead | Consume and operationalize |
| Taxonomy, ontology and evidence maps | Lead | Schema/tooling support |
| Opportunity discovery and sponsor intelligence | Lead | Opportunity workflow and automation |
| Learning-sciences / subject-matter partnerships | Coordinate | Track capability and integration needs |
| Software architecture and implementation | Contribute | Lead or coordinate build lanes |
| CI, deployment, security, observability | Consume shared standards | Lead |
| Public-good release and adoption evidence | Co-own | Engineering/release support |
| Sponsor reporting | Coordinate factual research inputs | Supply implementation and runtime evidence |

A Research-Astute lane may live in its own repositories. The hub ingests normalized records and public artifacts; it does not need broad write access to sibling organizations.

## 3. Domain taxonomy and ontology model

Use a **federated domain ontology** supported by a hierarchical taxonomy, competency framework, and explicit crosswalks. Do not force all disciplines into one universal tree.

### Initial pilot: education and K-12 AI

- **Education**
  - K-12 education
  - curriculum and instructional design
  - educational measurement and assessment
  - educator professional practice
  - learner experience and accessibility
- **Learning sciences**
  - cognition and conceptual understanding
  - motivation, effort, persistence and self-regulation
  - cognitive load and productive struggle
  - learner variability and inclusive design
  - feedback, scaffolding and pedagogical strategies
- **Formative assessment**
  - eliciting evidence of student thinking
  - interpreting evidence
  - adapting instruction and feedback
  - teacher-AI coordination
  - assessment validity and reliability
- **AI and digital infrastructure**
  - AI tutors and feedback assistants
  - evaluation datasets and benchmarks
  - models and public digital goods
  - harnesses, reference architectures and developer tooling
  - privacy, safety, transparency and human oversight
- **Public-good lifecycle**
  - discovery and provenance
  - license and rights review
  - quality and fitness-for-purpose
  - packaging and interoperability
  - maintenance and governance
  - adoption and impact measurement

Each concept should have a stable identifier, preferred label, definition, parent/related concepts, source framework, version, and evidence status. Competencies should map to concepts and observable evidence. Crosswalks should preserve the source framework's terminology rather than pretending two frameworks are identical.

### Core relationship types

Use explicit predicates rather than ambiguous generic edges:

- `broader_than` / `narrower_than`
- `related_to`
- `requires_competency`
- `measured_by`
- `supported_by_public_good`
- `implemented_by`
- `evaluated_with`
- `funded_by`
- `adopted_by`
- `supersedes` / `superseded_by`

Keep asserted facts, source-attributed claims, hypotheses, and derived inferences distinguishable.

## 4. Opportunity-to-public-good workflow

```text
DISCOVER
  -> verify primary source, dates, eligibility, award, restrictions
SCREEN
  -> mission fit, capability fit, delivery capacity, partner gaps, opportunity cost
MODEL
  -> domain taxonomy, ontology, users, needs, evidence, public-good landscape
FORM
  -> project brief, work packages, owners, partners, budget, risk register
DECIDE
  -> pursue / partner / monitor / decline (explicit owner decision)
DELIVER
  -> milestones, reproducible implementation, privacy/security, documentation
RELEASE
  -> license-cleared public goods, versioned artifacts, FAIR metadata
EVALUATE
  -> quality, adoption, downstream reuse, outcomes, maintenance
LEARN
  -> publish evidence and feed the next research/opportunity cycle
```

Every stage is independently stateful. An opportunity being discovered or screened does not mean it is approved, submitted, funded, or delivered.

## 5. Opportunity record requirements

Capture at minimum:

- stable opportunity ID and lane ID;
- sponsor, official URL, source capture date and source version;
- deadline with timezone and normalized UTC value;
- geography, applicant eligibility, lead-organization restrictions;
- award range, duration, allowable/unallowable costs and match requirements;
- required partners, expertise, letters, registrations and submission artifacts;
- deliverables, licenses, dissemination and reporting obligations;
- evaluation criteria and scoring weights, where published;
- capability fit, missing capabilities, capacity and opportunity cost;
- decision owner, decision timestamp, state and rationale;
- source citations, confidence, unresolved questions and recheck trigger.

Never infer eligibility from organizational form alone. Verify the actual applicant, fiscal sponsor/lead arrangement, jurisdiction, and downstream beneficiaries against the sponsor's current primary-source rules.

## 6. Funding and sponsor independence

- Maintain a diversified funding strategy: grants, fiscal sponsorship, philanthropic platforms (including Open Collective where suitable), institutional partnerships, paid services that cross-subsidize public goods, and community contributions.
- Treat each sponsor as a separate constraint set with its own scope, reporting, IP, attribution, data, and conflict-of-interest terms.
- Do not promise a sponsor control over independent findings or unrelated roadmap decisions.
- Do not accept funding terms that silently convert an intended public good into exclusive or proprietary deliverables.
- Review indirect costs, cash-flow timing, reimbursement risk, matching requirements, audit duties, data restrictions, and post-award maintenance before acceptance.
- Separate restricted funds and sponsor-specific reporting from general operating funds.
- A fiscal sponsor is a legal/administrative relationship requiring explicit agreement; a platform account or community page is not automatically a fiscal sponsor.

## 7. Initial opportunity anchor: K-12 AI Infrastructure Program

The initial pilot is the Digital Promise-led K-12 AI Infrastructure Program RFP:

**Integrating Digital Public Goods to Advance AI-Enabled Formative Assessment**

Official sources:
- https://k12-ai-infrastructure.org/harness-rfp/
- https://k12-ai-infrastructure.org/
- https://digitalpromise.org/articles/grant-opportunity-available-integrating-digital-public-goods-to-advance-ai-enabled-formative-assessment/

Published opportunity facts captured 2026-11-16:
- Up to two awards from a total pool of $1 million; maximum individual award $600,000.
- 18-month period, planned across three six-month phases.
- Estimated start: February 1, 2027.
- Published deadline: November 20, 2026, 11:59 p.m. Anywhere on Earth.
- Open to U.S.-based applicants, including for-profit and nonprofit organizations, academic institutions, school districts, and nonprofits under fiscal sponsorship; outputs must clearly serve U.S.-based students.
- Required open licenses: MIT or Apache-2.0 for code; CC-BY-4.0 for datasets and other components (including dependencies).
- The RFP seeks reusable infrastructure for multiple downstream developers, not a proprietary teacher-facing product. A demonstration application is useful, but most effort and outputs must serve multiple developers.
- Phase 1 centers on teacher-AI coordination for formative assessment. The RFP asks for at least four developer-useful tasks, learning-sciences grounding, and plans for engaging multiple public-good creators and at least three downstream developers in Phase 3.
- The RFP describes four equally important review criteria: significance, assets/capabilities, project workplan, and release/dissemination.

The canonical opportunity tracker already contains this as **C13**. This lane must link to and reconcile that record rather than create a duplicate. Re-fetch its current state before any pursue/submit decision; the existence of this charter is not a decision to apply.

### Preliminary fit hypothesis (not an application claim)

A plausible technical direction is an open, education-tuned harness/reference architecture that lets developers discover, inspect, test, and integrate education-specific public goods while preserving teacher agency and learning-sciences intent.

Potential reusable components:
1. Public-good discovery and license/provenance registry.
2. Learning-sciences context and task-planning adapters.
3. Teacher-AI interaction controls and observability.
4. Formative-assessment evaluation harness and benchmark adapters.
5. Learner-variability and accessibility test scenarios.
6. Developer integration starter kit and teacher-facing demonstration.

This is a hypothesis to validate with educators, learning scientists, public-good creators, and downstream developers. Existing Termux-MonoRepo engineering assets may accelerate implementation, but they do not replace missing education-domain expertise or partner commitments.

## 8. Evidence and success measures

Measure more than software completion:

- correctness and provenance of public-good integrations;
- fidelity to learning-sciences constructs;
- teacher understanding, agency, and ability to guide/monitor AI behavior;
- quality of formative evidence and usefulness of feedback;
- performance across learner variability and accessibility scenarios;
- developer time-to-integrate and successful reuse by independent developers;
- reproducibility, documentation quality, security, privacy, and license compliance;
- adoption, maintenance ownership, and sustained downstream use.

Do not collapse these into one opaque score. Preserve raw measures, cohort/context, evaluator, instrument/version, uncertainty, and limitations.

## 9. Governance and lifecycle states

Use explicit states:

`DISCOVERED -> SOURCE_VERIFIED -> SCREENED -> PARTNERING -> PROPOSED -> SUBMITTED -> AWARDED | DECLINED | NOT_SELECTED -> DELIVERING -> RELEASED -> ADOPTED -> MAINTAINED | SUNSET`

States may branch where the sponsor process requires it. Record the evidence for every transition. In particular, `SUBMITTED`, `AWARDED`, `RELEASED`, and `ADOPTED` must never be inferred from one another.

## 10. Initial implementation backlog

1. Reconcile and link existing opportunity C13; preserve its decision history.
2. Add a versioned domain concept/relationship schema and a small education pilot vocabulary.
3. Build a public-good catalog record schema with license, provenance, quality, and maintenance fields.
4. Create an opportunity-to-capability gap matrix for each sponsor.
5. Establish an educator and learning-sciences partner discovery track.
6. Build a proposal readiness gate that blocks unsupported claims and distinguishes missing evidence from negative evidence.
7. Define a standard project brief, milestone plan, budget assumptions, risk register, and release checklist.
8. Publish normalized lane evidence to the Termux-MonoRepo management hub.

## 11. Non-goals and safeguards

- Do not represent an opportunity record as an endorsement or commitment to apply.
- Do not claim grant eligibility, partner participation, educational efficacy, or award success without evidence.
- Do not ingest student-level or personally identifiable educational data into general telemetry.
- Do not let sponsor deadlines override privacy, safety, accessibility, or research ethics.
- Do not create a new teacher-facing product where the funding call is explicitly for reusable infrastructure.
- Do not treat taxonomy labels as proof of disciplinary competence.
