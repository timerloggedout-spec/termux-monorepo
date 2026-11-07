# Independent RFP Research — Technology Foresight & Landscape Platforms

**Status:** research initiated; no vendor selected, purchase, integration or pilot authorized.  
**Workstream:** independent procurement research. Not part of Orbital Syntax PR #2980 or its branch.  
**Baseline:** current Foresight Evidence Spine v2 on master.

## Purpose and outcomes

Assess build / adapt / buy / hybrid options for horizon scanning, technology signal discovery, evidence verification, curation, temporal comparison, multi-view exploration and team workflows. Preserve traceable sources, contradictory evidence, uncertainty, revision history and portable exports.

## Existing-system constraints

The monorepo Evidence Spine uses stable `resource_id`, `item_id`, `lane_id`, canonical source identity, H0-H3 horizon and separate evidence status. Procurement metadata already includes license, maintenance, portability, offline capability, interoperability, reproducibility, provenance, dependency risk, lock-in risk, security surface, resource cost, operational fit, horizon, confidence and decision status.

Candidates must provide a lossless adapter/export. Do not replace the canonical store or silently conflate horizon, maturity, confidence, impact and priority.

## Initial candidate set

| Candidate | Evaluation role | Initial disposition |
|---|---|---|
| Existing Foresight Radar + Evidence Spine | Internal baseline / canonical record store | Mandatory baseline; estimate extension effort |
| TeraGo (https://github.com/ekalinin/terago) | FOSS YAML-to-HTML radar and snapshot comparison; repository states MIT | Evaluate license, maintenance, schema, accessibility, export and adapter cost |
| Thoughtworks Build Your Own Radar (https://github.com/thoughtworks/build-your-own-radar) | FOSS interactive radar using CSV/JSON/Sheets; AGPL-3.0 | UX/component comparator; legal review required before embedding/modification |
| Envisioning Signals (https://www.envisioning.com/signals) | Hosted scanning and sensemaking workflow comparator | Evaluate source checking, contradiction states, data governance, export/API, security, SLA and TCO; do not assume FOSS |
| Custom multi-view explorer | Build option | Compare lifecycle cost and integration fit against adapting FOSS |
| Other commercial horizon-scanning services | Supplier discovery | Expand after requirements are fixed; distinguish strategic foresight from generic media monitoring |

Envisioning Signals' published pricing page has listed Starter €150/month and Pro €390/month on annual billing, with Enterprise custom. Treat as indicative, verify directly; not a quote and may change: https://signals.envisioning.com/pricing

## Weighted scorecard

Score 0-5, with 0 = absent/unknown, 1 = inadequate, 3 = baseline met, 5 = excellent and evidenced. Unknowns are marked **unverified**, not assumed to pass.

| Criterion | Weight |
|---|---:|
| Evidence provenance, source verification and contradiction handling | 15% |
| Data portability, open formats and API/export | 12% |
| FOSS/license and deployment rights | 10% |
| Security, privacy and data governance | 12% |
| Research discovery and source coverage | 10% |
| Assessment methodology and uncertainty semantics | 10% |
| Multi-view exploration and accessibility | 8% |
| Collaboration and workflow | 6% |
| Offline, local and ARM/Termux portability | 7% |
| Interoperability and integration cost | 5% |
| Total cost and operational support | 5% |

**Gating requirements:** complete export without proprietary lock-in; acceptable privacy/security; preservation of unknown and contradictory evidence; viable Evidence Spine adapter. A weighted score cannot override a failed gate.

## Supplier RFI questions

1. Provide architecture, deployment modes, data-flow diagram and subprocessors.
2. List software, model, dataset and output licenses and restrictions.
3. Demonstrate complete export of records, sources, revisions, relationships and attachments in documented open formats.
4. Explain source verification, contradiction handling, unreachable-source handling and provenance retention.
5. Explain controls against repeated model findings being counted as independent corroboration.
6. Explain scoring, calibration, human review and separation of horizon/maturity/confidence/impact/priority.
7. Demonstrate radar, table, cards, tree, graph and detail views against one shared dataset.
8. Provide accessibility conformance and known limitations.
9. State hosting region, encryption, retention/deletion, backup, incident response, SSO/MFA, audit and roles.
10. Document API/webhook, rate limits, versioning, import/export and integration support.
11. Demonstrate offline/self-hosted operation, ARM64 support, resource requirements and updates.
12. Provide seat/usage pricing, overages, renewal, support SLA, exit assistance and 3-year TCO.
13. Provide available security attestations and independent penetration-test summary.
14. Provide test tenant or reproducible evaluation environment using synthetic data.

## Evaluation protocol

- **A — Requirements:** users, research domains/languages, source coverage, sensitivity, deployment, volume, collaboration and budget ceiling.
- **B — Desk research:** verify license, maintenance, architecture, formats, dependencies, security and published pricing from primary sources.
- **C — Scripted demo:** same synthetic fixture for every candidate: weak signals, contradictions, duplicate findings, missing fields, long labels, dependencies and dated revisions.
- **D — Task tests:** find technology; verify claim; inspect contradiction; compare snapshots; discover dependency; export full record; operate offline and accessibly.
- **E — Risk/TCO:** scorecard, gates, implementation estimate, three-year TCO, exit/migration.
- **F — Recommendation:** build/adapt/buy/hybrid with evidence, rejected options, uncertainty and pilot conditions.

## Deliverables

Requirements/assumptions register; supplier longlist and shortlist; evidence-backed scorecard; license/security/privacy review; portability and integration assessment; scripted demo results; three-year TCO; recommendation; pilot success criteria and exit plan.

## Provisional recommendation

Do not procure yet. Benchmark the internal Evidence Spine against TeraGo and Thoughtworks for visualization/export; evaluate Envisioning Signals as the hosted workflow comparator. Test the architecture **local canonical evidence store + replaceable research and visualization adapters**. A hosted platform must demonstrate material research-quality gains and acceptable export, governance and exit terms.

No candidate has completed the scripted demo, security review or weighted assessment. No supplier receives confidential data. A pilot requires explicit approval and approved test data.

## Separation and governance

This RFP is its own research workstream and branch. It does not depend on Orbital Syntax, PR #2980, or the implementation branch. No vendor code, hosted API, data upload or paid trial is authorized. Preserve dated evidence and decision history.
