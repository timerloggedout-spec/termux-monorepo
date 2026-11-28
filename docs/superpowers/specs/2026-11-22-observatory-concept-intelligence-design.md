# Observatory Concept Intelligence and Outcome Prediction Design

Status: design proposal; awaiting owner review before implementation.
Date: 2026-11-22
Parent: `docs/ops/DEVPOST-OBSERVATORY-EXPANSION.md`
Scope: Observatory-wide concept discovery and challenge-outcome intelligence. Hackathons are one source surface, not the Observatory's organizing boundary.

## 1. Intent

Build an Observatory that harvests useful concepts from every available, authorized source and separately learns how challenge organizers select winners. The system serves two outputs:

1. **Concept intelligence:** a broad, source-grounded corpus of ideas, products, architectures, schemas, workflows, technical patterns, and unmet needs. Its value is independent of awards.
2. **Outcome intelligence:** a historical dataset linking each challenge's published brief, promotional language, requirements, eligibility, submission format, tracks, judging criteria, prize taxonomy, judge disclosures, submitted projects, and official results.

The prediction question is: given the information available before submission, can we estimate which concept/project attributes are more likely to receive each published award type for a given challenge?

The system reports evidence and calibrated uncertainty. It does not promise winner prediction.

## 2. Existing system and extension boundary

The challenge lane already owns canonical event records in `ops/challenge/coordinator.json`, schema documentation in `docs/ops/CHALLENGE-SCHEMA.md`, public event/project/participant/judge/prize observation in `docs/ops/CHALLENGE-OSINT.md`, append-only page snapshots, and graph import.

Keep those ownership boundaries. Extend the Observatory with a source-neutral concept corpus. Keep Devpost event and directory adapters as one family of source adapters. Preserve event facts and award results in the challenge plane; publish read-only, provenance-bearing links into the Observatory graph.

## 3. Two separate data products

### 3.1 Concept corpus

Capture candidates from all available source surfaces, including:

- hackathon briefs, promotional pages, requirements, event tracks, galleries, and project submissions;
- software directories, staff picks, popular/trending collections, tags, filters, and search results;
- open-source repositories, releases, issues, discussions, technical writeups, demos, and documentation;
- research papers, standards, product launches, public product documentation, and public community discussions;
- internal repository concepts, architecture decisions, reusable components, and observed engineering gaps.

Each concept record carries source identity, canonical URL, source type, observed time, first/last seen, raw evidence references, extraction version, confidence, and lifecycle state. Keep the source excerpt or structured facts with the record where permitted. Keep interpretation in a separate derived layer.

A concept can be valuable when it is non-winning, unsubmitted, early, technically novel, reusable, or aligned with a repo capability gap. Promotion decisions use explicit internal utility dimensions such as strategic fit, user value, feasibility, novelty, reuse potential, evidence strength, and cost. These dimensions remain distinct from competition placement.

### 3.2 Challenge outcome dataset

For each event, collect and version the pre-outcome feature set:

- organizer's promotional framing and stated motivation;
- problem statement and target user;
- requirements, eligibility, constraints, and required integrations;
- deliverables, submission format, and evaluation process;
- tracks, prize categories, award definitions, and prize values;
- judging criteria, published weights, and judging-stage gates;
- public judge roster snapshots and judge-affiliation evidence;
- dates, event format, venue/location when published, and field-size estimates;
- source snapshots and the timestamp at which each fact became observable.

Then collect project-level evidence and official outcomes:

- project concept, problem, user, solution, and claimed impact;
- architecture, stack, integrations, data sources, and execution pattern;
- demo, repository, documentation, test/evaluation evidence, and submission completeness;
- project-team identity only where publicly and explicitly disclosed;
- organizer-published award type, track, placement, finalist status, and result source;
- published judge comments/scores only when explicitly disclosed.

Keep raw source records immutable. Normalize into a versioned feature schema. Preserve unknown values as unknown with a coverage state.

## 4. Outcome taxonomy

Model awards as labels, not as a universal numeric rank. Examples include:

- overall grand prize;
- track/challenge winner;
- category-specific award;
- runner-up or second/third place where explicitly published;
- finalist;
- honorable mention;
- audience choice/community vote;
- sponsor award;
- special recognition;
- no published award;
- outcome unknown or unavailable.

An event's taxonomy is event-specific. Do not map every award into a numeric rank unless the organizer publishes an explicit ordered placement. Multi-award projects can carry multiple labels. Preserve track and award tier separately.

Keep these dimensions separate:

- official outcome;
- directory/editorial placement (Staff Pick, Popular, Trending);
- public engagement (likes, comments, views);
- internal concept utility;
- model-estimated award likelihood.

## 5. Prediction design and evidence gates

### 5.1 What can be predicted

The target is conditional: `P(award_type | event_brief, published_criteria, project_features, event_context)`.

Estimate separate outcomes for each event's award taxonomy, or map to carefully defined cross-event families while retaining the original event-specific label. Produce feature-to-criteria alignment explanations and confidence/coverage indicators.

The system may identify:
- concepts strongly aligned to the stated challenge and judging criteria;
- recurring patterns among projects receiving a particular award family;
- under-served requirements or tracks;
- promising project archetypes for future challenge participation.

### 5.2 Historical-data sufficiency

Start with descriptive cohort analysis. Promote to a predictive model only when there are enough independently observed events and projects per outcome class to support temporal validation.

Minimum gates before publishing predictive probabilities:
- stable, versioned event and project feature definitions;
- verified official result labels with source provenance;
- explicit missingness and selection/coverage accounting;
- train/test separation by event, with time-based holdout for generalization;
- baselines (class frequency and criteria-alignment heuristic) reported beside any learned model;
- calibration and per-class precision/recall or ranking metrics;
- confidence intervals or uncertainty bands;
- model card describing sample size, event coverage, known bias, drift, and intended use.

If evidence is sparse, publish descriptive findings and qualitative fit bands only. Label predictions as experimental until validation gates pass.

### 5.3 Leakage and bias controls

- Freeze pre-submission features at the latest timestamp before the relevant outcome became knowable.
- Keep post-submission engagement, judge comments, winner announcements, and directory popularity out of pre-submission predictors unless the prediction task explicitly occurs after those facts are available.
- Group splits by event to prevent sibling projects from the same event leaking across train and test.
- Preserve event, organizer, platform, track, and award family as context features and report their influence.
- Account for unobserved submissions, hidden judging panels, private scores, and incomplete galleries.
- Treat directory exposure and scraping coverage as selection mechanisms, not random samples.
- Avoid identity-based prediction. Judge or organizer history may be analyzed at event level only when public, relevant, and evaluated for fairness; individual participant identity is not a proxy for project merit.
- Publish only aggregate and source-supported conclusions.

## 6. Observatory architecture

Use a layered, source-neutral design:

1. **Source adapters:** Devpost event connector, Devpost directory observer, other hackathon platforms, GitHub/public code sources, research/documentation sources, product/community sources, and internal repo observations.
2. **Immutable observation ledger:** append-only source snapshots, fetch timestamps, hashes, parser versions, access/coverage status, and canonical identities.
3. **Entity resolution:** explicit canonical URL/ID joins; evidence-backed project, event, organization, concept, repository, and person relationships.
4. **Normalization:** concept schema and challenge-outcome schema with versioned transformations.
5. **Analytical views:** concept clusters, emerging tags, reusable patterns, challenge criteria maps, award cohorts, and model evaluation reports.
6. **Decision interface:** internal improvement candidates, related project opportunities, reference templates, and optional hackathon strategy briefs.
7. **Graph projection:** read-only derived links with provenance; source planes remain authoritative.

The concept corpus and outcome dataset share source observations and entities, but have separate labels, scoring logic, and success measures.

## 7. First implementation slice

Deliver the first slice in bounded stages:

A. Define the concept and challenge-outcome schemas plus sample fixtures using existing DataHub and UGREEN records where source facts are available.

B. Add a challenge brief extractor that preserves original promotional text, requirements, criteria, award taxonomy, source URL, fetch timestamp, and evidence coverage. Keep it source-agnostic; Devpost is the first adapter.

C. Add project/concept records from directory and event gallery surfaces, including non-winners and unranked projects. Preserve discovery surface and position as observation metadata only.

D. Add a result normalizer for official award labels and a comparison report joining event brief → project evidence → outcome.

E. Add descriptive cohort analysis and leakage-safe dataset export. Defer probabilistic prediction until evidence gates in §5.2 pass.

F. Add Observatory graph projections and cadence only after adapters and schema tests pass.

## 8. Acceptance criteria

- A challenge's promo/brief, requirements, criteria, tracks, prize taxonomy, and results can be compared in one provenance-backed record set.
- Award labels retain event-native meaning; the system does not fabricate a universal podium.
- Non-winning and unranked concepts remain discoverable and eligible for internal promotion.
- Concept utility and competition outcome are independent fields and independent ranking processes.
- Pre-outcome feature snapshots are reproducible and exclude later evidence.
- Dataset exports support event-grouped and temporal evaluation.
- Sparse history yields descriptive analysis, not unsupported probability claims.
- All source adapters preserve access boundaries, rate limits, source timestamps, and explicit coverage gaps.
- Graph projections remain derived and read-only.

## 9. Non-goals

- Automated entry, submission, voting, judging, or account actions.
- Treating public popularity as quality or as official placement.
- Predicting individual judge behavior or participant success from personal identity.
- Crawling private, authenticated, blocked, or access-restricted content.
- Launching a model before historical coverage and validation support it.
- Restricting the Observatory to hackathons; hackathons are one discovery surface among many.

## 10. Decisions reserved for implementation

- Exact source-neutral concept schema fields and controlled vocabularies.
- Storage partitioning and retention for raw snapshots versus normalized records.
- Which additional public source adapters join the first implementation slice.
- Model family selection after dataset profiling; start with interpretable baselines.
- Dashboard/report surface and recurring cadence after source reliability is measured.
