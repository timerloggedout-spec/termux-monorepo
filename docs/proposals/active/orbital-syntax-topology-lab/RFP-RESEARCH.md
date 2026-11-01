# Independent RFP Research — Technology Foresight & Landscape Platforms

**Status:** Research initiated; no vendor selected and no procurement commitment  
**Relationship:** Independent evaluation workstream; related to, but not a dependency of, the Orbital Syntax implementation proposal  
**Evaluation owner:** Research-Astute / termux-monorepo  
**Decision rule:** evidence-led shortlist, with build/adapt/buy assessed separately

## 1. Purpose

Evaluate whether the technology foresight and landscape-exploration capability should be:
1. extended from the existing monorepo Foresight Radar and Evidence Spine;
2. assembled from one or more FOSS components;
3. procured as a hosted research/foresight service; or
4. delivered as a hybrid (portable local evidence store plus optional hosted research).

This RFP is for market research and capability assessment, not a request to purchase or a commitment to issue a vendor contract.

## 2. Operational outcomes

The evaluated solution should help a research team:
- define a research question and bounded scan;
- discover candidate signals and technologies across multiple domains;
- verify each signal against traceable sources, including supporting and contradicting evidence;
- preserve dated observations, confidence, horizon, maturity, impact and decision status as distinct fields;
- curate, deduplicate and revise records without losing history;
- explore the same records as radar, table, cards, hierarchy/tree and relationship graph;
- compare snapshots over time and export portable records;
- operate with role-aware collaboration and auditable changes where required;
- support FOSS-first, ARM/Linux/Android/Termux workflows and offline/local operation where practical.

## 3. Existing system constraints and integration contract

The monorepo already has a Foresight Evidence Spine v2. Its canonical identities are `resource_id`, `item_id`, and `lane_id`; `canonical_source` must agree with `source.url`. It distinguishes H0-H3 horizon from evidence status (`confirmed`, `research_finding`, `attributed_claim`, `early_signal`, `speculative`, `disputed`). Procurement metadata already covers license, maintenance, portability, offline capability, interoperability, reproducibility, provenance, dependency risk, lock-in risk, security surface, resource cost, operational fit, horizon, confidence and decision status.

Any candidate must map to this contract or provide a documented, lossless export/adapter. It must not become a competing source of truth. Unknown values must remain unknown; contradictory evidence must remain inspectable; repeated model outputs are not independent corroboration by default.

## 4. Candidate landscape — initial desk research

| Candidate | Category | Evidence found | Initial assessment / due diligence |
|---|---|---|---|
| Existing Foresight Radar + Evidence Spine | Internal baseline | Local, portable JSONL evidence interchange; explicit provenance and procurement semantics | Mandatory baseline and likely system of record. Inspect implementation/tests and calculate extension effort. |
| TeraGo | FOSS radar generator | Go tool generates HTML from YAML, supports custom categories/statuses and compares dated radar snapshots; README states MIT | Strong bounded candidate for static radar generation/history. Verify current release activity, security/dependency posture, accessibility, data schema and adapter effort. |
| Thoughtworks Build Your Own Radar | FOSS interactive radar | Accepts Google Sheets, CSV or JSON; D3-based; project/package metadata reports AGPL-3.0 | Useful interaction benchmark and possible standalone deployment. AGPL obligations require legal review before embedding or modifying. Public hosted service may require public data or Google OAuth. |
| Envisioning Signals | Hosted research workflow | Product material describes brief → multi-model signal generation → source checks (supports/contradicts/unrelated/unreachable) → radar/table/cards/detail views; snapshots and editable records | Strongest surfaced hosted workflow comparator. Not FOSS. Assess data residency, retention, export/API, model governance, source access, security, SSO/audit, SLA and total cost before any pilot. |
| Custom multi-view explorer | Build | Existing prototype and local evidence spine provide a starting point | Best fit if portability, schema control, offline use and integration outweigh time-to-market. Estimate full lifecycle cost and maintenance burden. |
| Other commercial horizon-scanning services | Hosted specialist services | Market includes news/regulatory/risk scanning products, but current evidence is insufficient for fit ranking | Expand supplier discovery only after requirements and domain coverage are fixed; do not compare generic media monitoring to strategic foresight without task tests. |

### Public pricing snapshot (indicative, checked 2026-11-01)

Envisioning Signals publishes Starter at €150/month and Pro at €390/month on annual billing; Enterprise is custom. The page describes included AI usage allowances and workspace/editor limits. Prices exclude VAT and are not a quote. Validate current commercial terms directly before any procurement decision.

### Source links

- TeraGo repository and README: https://github.com/ekalinin/terago
- Thoughtworks Build Your Own Radar: https://github.com/thoughtworks/build-your-own-radar
- Thoughtworks radar input model: https://radar.thoughtworks.com/
- Envisioning Signals product: https://www.envisioning.com/signals
- Envisioning Signals pricing: https://signals.envisioning.com/pricing
- Envisioning Signals product workflow: https://signals.envisioning.com/product

## 5. Evaluation criteria and weights

Score each criterion 0-5 (0 = absent/unknown, 1 = materially inadequate, 3 = meets baseline, 5 = excellent and evidenced). Unknown is not a neutral pass: mark **unverified** and carry a risk flag.

| Criterion | Weight | Evidence required |
|---|---:|---|
| Evidence provenance, source verification and contradiction handling | 15% | Record-level sources, dated checks, supports/contradicts/unreachable states, audit history |
| Data portability, open formats and API/export | 12% | Complete export sample, stable identifiers, schema documentation, no vendor lock-in |
| FOSS/license and deployment rights | 10% | SPDX license, dependencies, SaaS/embedding/derivative obligations, SBOM |
| Security, privacy and data governance | 12% | Data flow, residency, retention/deletion, encryption, SSO/MFA, audit, incident process, subprocessors |
| Research discovery and source coverage | 10% | Source corpus, domain/language coverage, query controls, citations, freshness |
| Assessment methodology and uncertainty | 10% | Separate horizon/maturity/confidence/impact/priority; transparent scoring and calibration |
| Multi-view exploration and accessibility | 8% | Radar/table/tree/graph/detail, keyboard, screen reader, mobile, dense-data fallback |
| Collaboration and workflow | 6% | Roles, review, comments, versioning, notifications, team workspaces |
| Offline, local and ARM/Termux portability | 7% | Reproducible local install, offline operation, resource footprint, supported architectures |
| Interoperability and integration cost | 5% | Evidence Spine adapter, GitHub workflows, machine-readable API, migration effort |
| Total cost and operational support | 5% | License, seats, AI usage, hosting, support, implementation and 3-year TCO |

**Gating requirements:** exportability without proprietary lock-in; acceptable data governance; no silent conversion of unknown/contradictory evidence; and a viable Evidence Spine adapter. A high weighted score cannot override a failed gate.

## 6. Required supplier response / RFI questions

1. Provide architecture, deployment options, data-flow diagram and subprocessor list.
2. Identify all licenses and restrictions for software, models, datasets and generated outputs.
3. Demonstrate export of full records, source metadata, revisions, relationships and attachments in documented open formats.
4. Explain source verification, contradiction handling, source reachability failures and provenance retention.
5. Explain how model-generated findings are checked and how repeated findings are prevented from being misrepresented as independent corroboration.
6. Define scoring methodology, calibration, human review and separation of maturity, confidence, impact and priority.
7. Demonstrate radar, table, card, tree and graph views on one shared dataset.
8. Provide accessibility conformance evidence and known limitations.
9. State hosting regions, encryption, retention, deletion, backup, incident response, SSO/MFA, audit logs and role model.
10. Describe API/webhook support, rate limits, versioning, data import/export and integration support.
11. Provide offline/self-hosted support, ARM64 compatibility, resource requirements and update mechanism.
12. Provide pricing, usage caps, overages, renewal terms, support SLAs, exit assistance and 3-year cost model.
13. Provide security attestations and independent penetration-test summary where available.
14. Provide a test tenant or reproducible evaluation environment with synthetic data.

## 7. Evaluation protocol

**Stage A — Requirements validation:** confirm users, domains, source languages, data sensitivity, deployment constraints, expected volume, collaboration model and budget ceiling.

**Stage B — Desk research:** verify license, release/maintenance activity, architecture, supported formats, dependencies, security posture and published pricing from primary sources.

**Stage C — Scripted demonstration:** give every candidate the same synthetic dataset containing weak signals, contradictory sources, duplicate findings, missing values, long labels, dependency relationships and dated revisions.

**Stage D — Task-based assessment:** measure successful completion and time for (a) find a technology, (b) verify a claim, (c) inspect a contradiction, (d) compare snapshots, (e) identify a dependency, (f) export a complete record, and (g) work offline/accessibly.

**Stage E — Risk and TCO:** complete weighted scorecard, gate assessment, implementation estimate, 3-year TCO and exit/migration plan.

**Stage F — Recommendation:** recommend build, adapt, buy or hybrid; document rejected alternatives and uncertainty. A pilot requires explicit approval and must use synthetic or approved non-sensitive data.

## 8. Deliverables

- requirements and assumptions register;
- supplier longlist and shortlist;
- completed weighted scorecard with evidence links and unverified flags;
- license/security/privacy review;
- architecture and data portability assessment;
- scripted demo results;
- 3-year total-cost-of-ownership model;
- build-vs-adapt-vs-buy recommendation;
- pilot plan, success criteria and exit strategy.

## 9. Initial recommendation — provisional

Do not procure a full platform yet. First benchmark the internal Evidence Spine against TeraGo and Thoughtworks for visualization/export, while evaluating Envisioning Signals as the hosted end-to-end research workflow comparator. The likely architecture worth testing is **local canonical evidence store + replaceable research/visualization adapters**. A hosted service should only be considered if it demonstrates material discovery/verification gains and provides acceptable data export, governance and exit terms.

This is a provisional desk-research position, not a final vendor ranking. No candidate has completed the scripted demonstration, security review or weighted evaluation.

## 10. Research separation and governance

- This RFP remains separate from Orbital Syntax implementation scope and PR.
- No vendor code, hosted API, data upload or paid trial is authorized by this document.
- No supplier receives confidential or operational data during desk research.
- Update this document with dated evidence and preserve prior decision rationale.
- Procurement object fields in the Foresight Evidence Spine are the preferred machine-readable representation of supplier assessments.
