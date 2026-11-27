# Coralogix Capability Reconstruction — High-Detail Proposal

**Status:** proposed; reference registration and evidence-contract work in this change  
**Decision:** compare external systems, extract capabilities, then implement repository-owned equivalents behind provider adapters.

## 1. Executive decision

Build a repository-owned, provider-neutral observability and agent-evaluation plane. Use Coralogix as a commercial capability comparator and FOSS candidates as parallel research inputs. Treat My-Jogyo and Docxology as complementary research-method exemplars already registered in refTemplates/15_Research_Repo_Templates/.

Combine the **My-Jogyo research loop** (hypothesis, experiment, finding, adversarial review, report; role-separated agents; persistent computational sessions) with the **Docxology reproducibility loop** (staged pipeline, dependency/toolchain discipline, tests, generated artifacts, provenance). Bind both to the repository evidence spine: canonical JSONL, receipts, immutable Git SHA/run linkage, ATES, Action→Effect attribution, and repository-owned promotion gates.

OpenTelemetry supplies interoperability. SigNoz, HyperDX/ClickStack, OpenObserve, Langfuse, Phoenix, Parca, and Pyroscope remain parallel adapters. Admin Desk presents governed evidence and policy state. The output is our own implementation and integration layer; references do not establish runtime dependency or automatic adoption.

## 2. Outcomes

1. Register selected candidates under the correct refTemplates category with README and SOURCE metadata.
2. Reconcile all 12 tier-A research slots across README, SOURCE-MAP, and inventory.
3. Define one event and experiment contract for provider adapters.
4. Establish comparable FOSS and commercial capability tests.
5. Connect outcomes to ATES, 3L0, Moneyball, and Admin Desk through repository-owned receipts.
6. Add license findings to a consolidated legal-review record, including component exceptions and unresolved upstream checks.
7. Keep deployment, credentials, custom forks, and runtime promotion behind evidence gates.

## 3. Scope

Included: metadata references for OpenTelemetry Collector, SigNoz, HyperDX/ClickStack, OpenObserve, Parca, Grafana Pyroscope, Coralogix, Langfuse, and Arize Phoenix; enhanced My-Jogyo/Docxology comparisons; inventory validation for categories 05, 11, and 15; architecture, evidence, Admin Desk, license, and DoE/MVT specifications.

Later evidence-backed waves: persistent services; full upstream clones/dependency stacks; provider credentials and production export; custom forks/live smods; automatic PR comments, check publication, or merge authority.

## 4. Capability model

| Capability | Candidate references | Repository authority |
|---|---|---|
| Instrumentation | OpenTelemetry | Canonical event contract |
| Ingestion | OTel Collector | Sanitized event pipeline |
| Operational UI | SigNoz, HyperDX, OpenObserve, Coralogix | GitHub receipts + provider-neutral IDs |
| Agent evaluation | Langfuse, Phoenix | DoE registry + evaluation artifacts |
| Profiling | Parca, Pyroscope | Environment fingerprints + profile digests |
| Workflow intelligence | Coralogix + GitHub Actions | Actions run/attempt/SHA records |
| Research execution | My-Jogyo | Research task and evidence records |
| Reproducible pipeline | Docxology | Dual-gate and artifact receipts |

## 5. Operating principles

- Canonical JSONL and receipts remain the evidence authority.
- OpenTelemetry provides interoperability; providers remain replaceable adapters.
- Each experiment uses a declared cohort, variant, environment fingerprint, and acceptance contract.
- High-cardinality identifiers remain in traces/events; metric labels use bounded dimensions.
- Missing observations remain null with explicit evidence status.
- Source claims, inspected code, executed tests, and independently reproduced behavior remain separate evidence classes.
- License status is recorded per upstream/component and consolidated with repository obligations.
- Promotion requires reproducible evidence and the existing dual-gate.

## 6. Delivery phases

| Phase | Deliverable | Acceptance evidence |
|---|---|---|
| 0 — registry | Candidate metadata and reconciled source map | Strict inventory pass; README + SOURCE per slot |
| 1 — contract | Canonical provider event + trace correlation | Schema fixtures; privacy checks |
| 2 — instrumentation | Workflow, task, tool, model, request spans | Exact SHA/run/attempt correlation |
| 3 — adapters | OTel Collector + UI/eval/profile adapters | Same cohort imported by multiple providers |
| 4 — DoE/MVT | Matched manager/provider variants | Reproducible assignment and evaluation records |
| 5 — Admin Desk | Evidence projections and gated actions | Role tests, provenance links, audit receipts |
| 6 — promotion | Select repository-owned components | Dual-gate + validated task outcome + legal review |

## 7. Acceptance criteria

- All candidates appear in the correct refTemplates category.
- All 12 research-template slots agree across README and SOURCE-MAP.
- refTemplates_inventory.py --strict validates categories 05, 11, and 15.
- Event contract carries workflow and request identities with stable correlation.
- Privacy filtering excludes credentials, authorization headers, raw prompts/completions, and private context by default.
- Multiple observability and AI-evaluation providers ingest the same bounded cohort.
- Manager variants receive matched tasks, comparable environments, and identical acceptance criteria.
- Results preserve raw observations, uncertainty, provider/version, and artifact digests.
- Admin Desk presents evidence and policy state without becoming a second evidence authority.
- License reconciliation records upstream license, component exceptions, verification SHA/date, and legal disposition.

## 8. Risks and controls

| Risk | Control |
|---|---|
| Provider lock-in | Canonical schema, exportable artifacts, adapter boundary |
| Telemetry cost | Bounded metric labels; IDs in traces/events |
| Sensitive data leakage | Allowlist-first redaction and fixture tests |
| Misleading leaderboard | Matched cohorts, repetitions, confidence intervals, task outcomes |
| License ambiguity | Exact-revision LICENSE/NOTICE/dependency scan; consolidated legal review |
| Termux resource pressure | Metadata-first references; remote/ephemeral lab; resource preflight |
| Duplicate registries | Extend existing ForeSight/evidence registries; refTemplates remains source index |
| False promotion | Dual-gate, task outcome, provenance, explicit operator decision |

## 9. Immediate implementation

This change adds metadata references, strengthens the reference inventory contract, reconciles the research-template listing, and files the high-detail implementation plan. Runtime adapters form the next wave because each requires pinned upstream revisions, environment/resource checks, and reproducible integration tests.
