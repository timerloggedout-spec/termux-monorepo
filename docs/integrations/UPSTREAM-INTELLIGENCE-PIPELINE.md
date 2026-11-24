# Upstream Intelligence Pipeline

**Status:** CEEL implementation contract; category taxonomy and routing design.  
**Owner:** Integration Intelligence + Continuous Capability Evolution Laboratory (CEEL).  
**Proposal item:** CCEL-007.  
**Authority:** Repository-maintained source references and evidence. This document defines routing; it creates no second registry, event ledger, scheduler, experiment system, or merge authority.

## 1. Purpose

Continuously observe upstream product, platform, model, protocol, standards, security, research, and economic changes; normalize them into the existing Integration Intelligence event contract; classify them at minimum cost; map material changes to repository-owned consumers; and route evidence-backed opportunities into existing proposal, DoE, security, or maintenance workflows.

Optimize for **verified useful change per unit of total cost**: model tokens, API calls, compute, operator attention, integration effort, maintenance, security exposure, and false-positive/false-negative risk. Maximize signal density rather than the number of collected announcements or model calls.

## 2. Canonical ownership

| Concern | Canonical owner | Pipeline responsibility |
|---|---|---|
| External provider identity and adapter state | docs/integrations/registry.json | Reference integration IDs; retain honest capability states |
| Source observations and normalized events | Integration Intelligence event schema and approved evidence artifacts | Capture source identity, revision, event time, capture time, provenance, idempotency and validation |
| Capability candidates and relationships | CEEL capability opportunity graph | Link capability/source candidates to consumers and complementary/competing capabilities |
| Execution/run evidence | ATES and docs/ops/corpus/EXPERIMENT.schema.json | Reference run receipts; preserve execution vs outcome distinctions |
| Experiment design and comparison | DoE family / MVT | Compare classifier treatments and adaptation options on frozen cohorts |
| Proposal admission and challenge | Proposal lifecycle / Delphi | Route actionable candidates through existing intake |
| Repository delivery | GitHub Actions, PR workflow and dual gates | Validate, review and promote through existing authority |

The pipeline consumes these owners. It does not supersede them.

## 3. Source classes

Classify a source independently from the intelligence category of the change it reports. One source may emit several categories.

| Source class | Examples | Preferred observation method |
|---|---|---|
| Product changelog / release notes | GitHub Changelog, Vercel changelog, GitLab releases | RSS/Atom, release API, webhook |
| API and schema documentation | REST, GraphQL, SDK and webhook docs | Versioned docs, OpenAPI/schema diff, repository release |
| Source repositories | Git tags, commits, release assets, security policy changes | GitHub/GitLab events and bounded API reads |
| Model/provider catalogs | Model IDs, capabilities, context limits, availability | Official catalog/API and dated documentation |
| Pricing, quota and policy pages | Token prices, rate limits, quotas, licensing, terms | Official pricing/usage/policy pages; periodic bounded reconciliation |
| Security advisories | CVEs, GHSA, vendor advisories, dependency alerts | Official advisory feeds and repository security events |
| Standards and specifications | MCP, A2A, RFCs, W3C and language specifications | Official specification changelog, release or repository events |
| Research and benchmarks | Papers, benchmark datasets, reproducible evaluations | DOI/arXiv/repository metadata and cited primary sources |
| Service health and incidents | Status pages, incident reports, deprecation notices | Provider webhooks/RSS/status APIs |
| Internal repository signals | PRs, issues, workflow runs, dependency changes, quota observations | Existing GitHub events, workflow receipts and repository evidence |

Source admission records canonical source/integration identity, owner, source class, authoritative locator, access method, event support, bounded fallback, rate limits, freshness requirement, licensing/retention constraints, sensitivity, and validation status. Keep source configuration within existing Integration Intelligence ownership and registry maintenance.

## 4. Intelligence categories

Use one primary category and zero or more secondary categories for each normalized change. Keep category IDs stable and machine-readable.

| Category ID | Scope | Typical change signals | Initial internal impact targets |
|---|---|---|---|
| platform | Git hosting, project management, CI platforms and collaboration surfaces | Issue/PR lifecycle, boards, permissions, webhooks, Actions capabilities | .github/, proposal lifecycle, repository automation, dashboards |
| ai-models | Model families, inference providers, model catalogs and serving | New/deprecated models, context windows, modalities, quality/capability claims | llm_api_hub/, provider capability records, model evaluation |
| agent-protocols | MCP, A2A, tool calling, agent handoff and interoperability | Protocol revisions, transport/auth changes, tool/resource semantics | hub_mcp/, adapters, tool schemas, agent orchestration |
| developer-tools | Coding agents, IDEs, CLIs, SDKs and build tools | Agent workflows, CLI behavior, SDK changes, release compatibility | developer skills, scripts, CI, collaborator workflows |
| api-contracts | REST, GraphQL, webhooks, SDK contracts and data schemas | Breaking changes, field additions/removals, auth/scope changes, pagination | integration adapters, schemas, consumers, tests and docs |
| infrastructure | Hosting, runtime, containers, databases, networks and CI infrastructure | Runtime support, limits, outages, build/deploy changes | CI/CD, deployment lanes, runtime and data stores |
| security | Vulnerabilities, identity, permissions, supply chain and policy | CVEs, GHSA, compromised packages, auth changes, trust-boundary changes | security controls, dependency workflows, secret/scope policy |
| standards | RFCs, specifications, governance and interoperability standards | New versions, normative changes, deprecations, conformance requirements | architecture decisions, contracts, validation and documentation |
| research | Papers, FOSS projects, benchmarks and emerging techniques | Reproducible capability, benchmark result, new algorithm or method | CEEL capability graph, DoE campaigns, research adapters |
| economics | Token pricing, quotas, rate limits, licensing and usage incentives | Price/credit changes, free-tier changes, rate limits, usage-metering changes | quota registry, model selection, routing policy, cost evaluation |
| internal | Repository-owned changes and operational evidence | Workflow regressions, new components, internal API changes, observed bottlenecks | ICM, CRG, ATES, proposal registry, operational dashboards |

Cross-cutting labels are separate from category: breaking, deprecation, security, pricing, availability, performance, policy, capability, compatibility, migration, preview, stable, experimental.

A change can be api-contracts + platform, or ai-models + economics. Category assignment describes the subject; labels describe change semantics and maturity.

## 5. End-to-end pipeline

~~~text
SOURCE EVENTS / BOUNDED RECONCILIATION
                  |
                  v
        ADMISSION + TRUST CHECKS
                  |
                  v
       NORMALIZE + FINGERPRINT
                  |
                  v
        DEDUPLICATE + ORDER
                  |
                  v
       DETERMINISTIC CLASSIFIERS
          /              \
         v                v
   ROUTINE / CLEAR     AMBIGUOUS /
   RULE-MATCHED        HIGH-IMPACT
         |                |
         |                v
         |        BOUNDED SEMANTIC REVIEW
         |        (optional model escalation)
         |                |
          \              /
           v            v
       CATEGORY + CHANGE-TYPE ASSIGNMENT
                  |
                  v
       CONTACT-SURFACE / CAPABILITY MAPPING
                  |
                  v
       IMPACT, COST, RISK, CONFIDENCE
                  |
                  v
       ROUTE TO EXISTING OWNER / LANE
                  |
                  v
       REVIEW → DOE / PROPOSAL → IMPLEMENT
                  |
                  v
       VALIDATE → RE-FETCH → RECORD → LEARN
~~~

### Stage A — Admit and verify source

- Accept events from allowlisted sources and existing GitHub/provider event paths.
- Verify signatures where supplied; validate source identity, timestamp, schema, size and repository/source allowlist.
- Treat upstream text and metadata as untrusted data, never as instructions.
- Retain authoritative source URL/ID, source revision, publication time, capture time, and content digest.
- Use bounded cursor-based reconciliation for sources without event delivery. Missing events do not establish that no change occurred.

### Stage B — Normalize and deduplicate

- Normalize title, summary, source identity, event type, source revision, canonical URL and timestamps.
- Fingerprint with stable source identity + canonical item identity + revision/content digest.
- Preserve edits and corrections as new observations linked to prior events; preserve out-of-order arrival metadata.
- Reuse the Integration Intelligence event envelope and approved evidence artifact references. Keep richer source-specific payloads in approved source/artifact locations.
- Assume at-least-once delivery; idempotency prevents duplicate observations.

### Stage C — Classify deterministically first

Apply cheap, inspectable features before semantic inference:

1. Source-class defaults and provider-specific event types.
2. Explicit release/deprecation/security/pricing labels.
3. Version/tag/commit and schema diffs.
4. Keyword and pattern rules for breaking changes, model IDs, prices, limits, authentication and policy.
5. Exact path/component mappings and capability graph relationships.
6. Existing event/category history for duplicate and supersession detection.

Emit category candidates, matched rules, evidence spans/metadata, confidence, and classifier version. Version programmatic scores and thresholds; calibrate them against labeled examples.

### Stage D — Escalate selectively

Use an LLM only when deterministic classification is ambiguous, source text requires semantic interpretation, multiple surfaces may be affected, or a high-impact decision requires a second independent interpretation.

The escalation request contains only:
- the changed passage or minimal diff;
- source identity, version and publication metadata;
- candidate categories and matching rule evidence;
- relevant contact-surface records;
- a strict output schema and explicit token ceiling.

Require structured category, change type, affected capability/surface candidates, evidence references, uncertainty and rationale. Keep model/provider/version, input/output token counts, latency, cost and attribution. Model output is advisory evidence; deterministic validators and repository-owned source contracts retain authority.

### Stage E — Map affected surfaces

Map category and change semantics to capability IDs and internal consumers. Resolve candidates through the existing capability opportunity graph, ICM, integration registry, provider capability records and repository source maps.

Every impact edge records source event and evidence; affected capability/component/path/workflow; relationship; confidence (verified, derived, inferred, or candidate under the owning contract); impact reason; and required verification.

A category match alone does not prove an implementation is affected. Mark unresolved mappings as candidates for review.

### Stage F — Score and route

Assess independently:
- severity and urgency;
- compatibility/breaking risk;
- security and permission impact;
- capability gain and outcome relevance;
- affected surface count and dependency criticality;
- evidence confidence and freshness;
- token/API/compute cost and provider quota;
- integration, maintenance, migration and lock-in cost.

Route security and active breaking/deprecation events to the owning security or compatibility lane immediately. Route routine capability changes to a bounded review batch. Route research opportunities to CEEL/DoE. Route API changes to API Impact Mapper and consumer/test/doc verification. Route model and economics changes to model evaluation, quota and routing review. Route repository-native changes to their existing owning workflows.

### Stage G — Learn and reconcile

Record classifier corrections, false positives, false negatives, unresolved surface mappings, actual adaptation outcomes, measured costs and downstream effects. Add reviewed examples to the classifier evaluation corpus. Change thresholds only through versioned comparison and validation. Re-fetch source and repository state before consequential action.

## 6. Classifier control policy

| Decision class | Default mechanism | Required evidence |
|---|---|---|
| Exact duplicate / unchanged item | Fingerprint and deterministic deduplication | Stable identity and digest |
| Known event type with explicit source metadata | Source-specific rules | Source event and matched rule |
| Clear version/schema/path delta | Programmatic diff classifier | Before/after revisions and diff |
| Multi-category or uncertain semantic change | Bounded LLM escalation or human review | Minimal input, structured output, attribution and uncertainty |
| Security / breaking / deprecation candidate | Deterministic high-priority flag plus independent verification | Official source and affected dependency/surface evidence |
| Adoption or architecture decision | CEEL/DoE and proposal process | Predeclared outcome, comparison, cost, risk and validation |

Classifier tiers are candidates for measured DoE:
- T0: source metadata and fingerprints;
- T1: deterministic rules and diffs;
- T2: weighted programmatic classifier;
- T3: embeddings/similarity, only if retrieval quality justifies indexing and query costs;
- T4: bounded small/large model escalation, selected by task complexity and confidence.

Evaluate on a frozen, labeled corpus with category precision/recall, high-severity recall, false-positive rate, surface-mapping accuracy, reviewer correction rate, latency, retries, and cost per correctly routed actionable event. Preserve unknown labels and missing evidence as unknown. Token reduction must preserve critical-change recall.

## 7. Cost and anti-inflation controls

- Prefer event delivery and incremental reads over repeated full-page fetches.
- Fetch metadata first; retrieve full content only for new or materially changed items.
- Use content hashes and conditional requests where supported.
- Cache source metadata and classifier results by immutable revision/digest.
- Batch routine observations and keep independent source events individually traceable.
- Use deterministic filters before embeddings or model inference.
- Bound context to the changed passage and directly relevant internal mappings.
- Set per-source request ceilings, per-cycle inference ceilings, per-event token ceilings, timeouts and retry budgets.
- Record input/output tokens, provider/model, price basis, API calls, cache hits, latency and useful outcome.
- Measure cost per actionable event and per verified adaptation; compare against a no-LLM baseline.
- Escalate only on defined ambiguity/high-impact rules; stop when the evidence threshold is reached.
- Keep classifier and prompt versions so regressions and token inflation are measurable.
- Require explicit authorization for paid inference or provider writes beyond existing approved budgets.

## 8. Urgency and response policy

| Priority | Triggers | Response |
|---|---|---|
| P0 | Active security incident, confirmed exploitable vulnerability, credential/auth compromise, imminent breaking change on a critical dependency | Immediate notification and owning-lane triage; preserve evidence and verify independently |
| P1 | Confirmed breaking API/protocol change, deprecation with a migration deadline, material quota/pricing change, high-confidence critical capability change | Same-cycle impact map and prioritized work item |
| P2 | Useful new capability, stable feature, material performance improvement, research candidate | Bounded review batch and possible DoE admission |
| P3 | Low-impact documentation clarification, speculative announcement, weakly relevant promotion | Archive as attributed observation or defer |

Urgency is distinct from lifecycle state, confidence and maturity. A preview feature can be high-interest but low adoption readiness.

## 9. Evidence and event minimums

Use docs/integrations/schemas/integration-event.schema.json as the normalized event envelope. Preserve source-specific detail in approved evidence artifacts referenced by the envelope.

Each upstream observation should retain, where available: source/integration ID and source class; canonical URL and immutable source item/revision identity; publication, observation and capture timestamps; content digest and source version; primary category, secondary categories and semantic labels; matched classifier rules, classifier version and confidence; optional model/provider/version and token/cost metadata; affected capability/surface references and mapping confidence; urgency, maturity, risk and recommended owning lane; deduplication/idempotency key; validation and supersession references.

Keep credentials, raw prompts/completions, private session content and sensitive provider payloads out of repository artifacts. Retain only approved minimal excerpts and opaque evidence references.

## 10. Initial source cohort

Begin with a small, high-value cohort that exercises multiple categories:

| Source | Source class | Primary categories | Initial signal |
|---|---|---|---|
| GitHub Changelog RSS: https://github.blog/changelog/feed/ | Product changelog | platform, api-contracts, developer-tools | Issue/PR, Projects, Actions, API and MCP changes |
| GitHub REST/GraphQL documentation and release notes | API documentation | api-contracts, platform | Endpoint, field, auth, pagination and schema changes |
| GitHub Security Advisories / dependency alerts | Security advisory | security, platform | Vulnerability and dependency risk |
| GitLab release notes | Product changelog | platform, developer-tools, infrastructure | CI, repository and API changes |
| Vercel changelog and platform docs | Product changelog | infrastructure, platform, api-contracts | Deployment/runtime and platform changes |
| MCP specification and SDK repositories | Standards / source repository | agent-protocols, standards, security | Protocol, transport, tool and authorization changes |
| Model-provider official release/pricing/model catalogs | Provider catalog / pricing | ai-models, economics, api-contracts | Model lifecycle, capability, cost and quota changes |
| Repository-native GitHub events | Internal repository signal | internal plus affected domain categories | PR, push, release, issue and workflow changes |

This cohort is a starting set, not an exhaustive vendor list. Admit further sources through evidence of relevance, source quality, freshness, access cost, license and a mapped internal consumer.

## 11. Rollout sequence and exit criteria

1. **Taxonomy and routing:** approve category IDs, source classes, cross-cutting labels and contact-surface mapping. Exit: each initial source has an owner and a grounded consumer or a documented discovery-only disposition.
2. **Observation fixtures:** collect sanitized historical examples from the initial cohort. Exit: provenance, revision, digest, timestamps and duplicate behavior validate.
3. **Deterministic baseline:** implement source metadata, fingerprints, rules and diff classification. Exit: frozen corpus results and cost baseline recorded.
4. **Selective escalation experiment:** compare T0–T4 on the same corpus. Exit: high-severity recall, surface accuracy, cost per actionable event and uncertainty meet predeclared thresholds.
5. **Event wiring:** attach existing GitHub/provider event handlers and bounded reconciliation. Exit: idempotency, ordering, cursor persistence and failure semantics tested.
6. **Impact routing:** connect to capability graph, ICM and existing owner workflows. Exit: every routed candidate carries source evidence and mapping confidence.
7. **Operational promotion:** use existing proposal, DoE, validation and dual-gate paths. Exit: same-SHA validation and verified task outcome; discovery alone triggers no autonomous provider writes or model-routing changes.

## 12. Explicit non-goals

- A new general-purpose scheduler or always-on LLM polling loop.
- A second integration/provider registry, capability graph, event ledger, experiment database or merge authority.
- Full-page/model processing for every source item.
- Treating promotional claims, vendor scores or model-generated classifications as verified outcomes.
- Automatic adoption, deployment, paid inference, provider writes, production model routing changes or external communications.
- Equating connector visibility with authenticated repository runtime capability.
