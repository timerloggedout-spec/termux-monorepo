# Domain Atlas — Design Record

**Work item:** CRG-16  
**Parent proposal:** context-relationship-graph  
**Status:** implementation on feature branch  
**Source baseline:** master at 084cffa6155f3e22dc0d9d687b4064a5fb0d9090

## Intent

Add an optional domain-level interaction surface to the existing Historical Corpus Explorer. The Atlas maps the repository's major evidence, orchestration, measurement, and analytics domains without creating a second graph store or authority plane.

## Layers

- **Semantic:** domain meaning and typed domain-to-domain relationships.
- **Operational:** producer/consumer and control-flow relationships.
- **Evidence:** source document, repository path, immutable revision URL, and concise supporting claim for each mapping.

Evidence is a view over the same relationships. It is not a separate relationship store.

## Initial domain set

1. GitHub Evidence — source events and durable records.
2. Context Relationship Graph — metadata-only relationship substrate.
3. SHE Dashboard — read-only projection for operations, research, and forensic review.
4. Agent Team Control Plane — BIUDL and team operating lanes.
5. Execution Telemetry — metadata-first task/tool/handoff observations.
6. Moneyball / 3L0 — sanitized evidence analytics and outcome evaluation.

## Relationship contract

Each relationship has a stable ID, source domain, target domain, typed relation, one or more layers, classification, and evidence references. Direction is always source → target. Verified edges require one or more supporting source records. Candidate and unknown states remain explicit.

The initial curated graph includes four verified mappings and one candidate mapping. The Execution Telemetry → Moneyball/3L0 link remains candidate pending an exact run/attempt/source-SHA join between the throughput-event stream and Moneyball records. These mappings express documented architecture and data flow; they do not assert causality or agent identity.

## Interaction

The Explorer presents domain cards and a relationship table. All, Semantic, Operational, and Evidence controls filter or expose the same curated graph. Controls use keyboard-accessible buttons with aria-pressed. Repository text is inserted as text nodes; links require HTTPS and open with noopener/noreferrer.

## Provenance and validation

The projection pins its source to a full Git commit SHA. A checked-in JSON Schema defines the contract. A deterministic, network-free validator checks stable IDs, domain endpoints, relationship types/layers/classifications, full source SHA, HTTPS evidence, and evidence presence for verified relationships. Focused tests exercise valid data and failure cases.

## Authority boundary

The Atlas is a read-only projection. Canonical repository files, the context-relationship corpus, and SHE contracts remain authoritative. The Atlas does not collect data, dispatch work, change routing, write back graph facts, or authorize GitHub actions.
