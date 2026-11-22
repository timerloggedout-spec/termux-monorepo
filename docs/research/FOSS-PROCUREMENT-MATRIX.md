# FOSS Procurement Matrix

The matrix is a decision-support record, not a vendor scorecard.

## Required fields
- resource_id
- project
- category
- canonical_source
- source_type
- license
- maintenance
- portability
- offline_capability
- interoperability
- reproducibility
- provenance
- dependency_risk
- lock_in_risk
- security_surface
- resource_cost
- operational_fit
- horizon
- confidence
- decision_status
- version_or_commit
- observed_at
- unresolved_questions

## Decision status
- WATCH: collect evidence only
- INVESTIGATE: verify fit and provenance
- PROTOTYPE: build a bounded experiment
- ADOPT: use in a controlled production path
- REJECT: documented reason; may be revisited
- HOLD: blocked by an explicit dependency or missing evidence

No aggregate score is required. Keep dimensions inspectable so a later decision can be audited.

## Portability contract
Record actual tested targets separately:
- ARM64 Linux
- x86_64 Linux
- Android
- Termux
- offline/air-gapped

"Portable" without a tested target is an unverified claim.

## Lock-in contract
Record both:
- runtime lock-in: dependence on proprietary execution/provider APIs
- evidence lock-in: inability to export raw events/configuration/results

Canonical evidence must remain exportable as JSON/JSONL, Markdown, SQLite, or equivalent open formats.

Vendor-specific persistence and UX remain adapters, never the canonical evidence store.


## Initial candidate registration — 2026-11-22

| Field | Lookyloo candidate record |
|---|---|
| resource_id | `lookyloo` |
| project | Lookyloo upstream + `timerloggedout-spec/lookyloo_fork` |
| category | Web-presence reconnaissance + observability; browser capture and third-party domain/request relationship mapping |
| canonical_source | [Upstream](https://github.com/Lookyloo/lookyloo) · [Local fork](https://github.com/timerloggedout-spec/lookyloo_fork) |
| source_type | Open-source application / self-hosted web reconnaissance |
| license | Fork `LICENSE` text identifies BSD 3-Clause; GitHub API metadata reports `NOASSERTION`. Preserve the text-level finding and verify upstream license provenance before adoption. |
| maintenance | Upstream latest observed commit: `8edc8609360a0340bc89ddc7839b7ad10384ae5d` (2026-11-07). Local fork latest observed commit: `375750b25195605a3e17d2ada2d0c7767d79ac94` (2021-01-29). Fork sync status requires reconciliation. |
| portability | Docker Compose deployment is present. ARM64 Linux, x86_64 Linux, Android, and Termux remain untested. |
| offline_capability | Self-hosted capture/indexing components are present; target-site capture inherently requires network access. Offline analysis capability remains unverified. |
| interoperability | README identifies the `pylookyloo` Python client. API/export formats and integration coverage require verification. |
| reproducibility | Dockerfile and Compose manifest are present. Redis image tags are unpinned; Splash is pinned to `3.5.0`. Build reproducibility requires a pinned dependency/image audit. |
| provenance | Repository metadata, README, LICENSE, Dockerfile, Compose manifest, and commit SHAs inspected 2026-11-22. |
| dependency_risk | Redis ×2, Splash, Python/Poetry dependency graph, browser capture runtime; full SBOM and vulnerability posture pending. |
| lock_in_risk | Self-hosted architecture suggests deployment control; capture export, schema stability, and migration paths require tests. |
| security_surface | Browser-driven remote content capture, proxy/network egress, capture storage, Redis services, and web UI. Fork commit history explicitly records public-by-default capture behavior; validate visibility controls and access boundaries before processing sensitive URLs. |
| resource_cost | CPU, memory, storage, browser runtime, and network cost unmeasured. |
| operational_fit | Candidate comparator for owned-site reconnaissance, page journey capture, third-party domain discovery, and change investigation. Complementary to publishing/hosting and repository-native telemetry. |
| horizon | H1 — bounded investigation |
| confidence | Medium for declared purpose and checked repository artifacts; low for current fork compatibility, runtime security, and operational performance. |
| decision_status | INVESTIGATE |
| version_or_commit | Fork `375750b25195605a3e17d2ada2d0c7767d79ac94`; upstream `8edc8609360a0340bc89ddc7839b7ad10384ae5d` |
| observed_at | 2026-11-22 |
| unresolved_questions | Fork-to-upstream divergence; BSD license provenance; public/private capture controls; supported Python/runtime versions; API and export semantics; ARM/Termux feasibility; image pinning; auth/RBAC; retention/deletion; performance and resource profile. |

### Comparison boundary

Lookyloo is a candidate in the web-presence reconnaissance + observability category. Compare it with tools that inspect browser-visible page journeys, resource/domain dependencies, and web attack surface. Keep it distinct from agent tracing/evaluation platforms such as Langfuse/Phoenix and from publishing/hosting platforms. Treat its output as an observational evidence source; repository-owned receipts and source records remain authoritative.

### Admission sequence

1. Reconcile the local fork against the current upstream tree and identify intentional deltas.
2. Audit capture visibility, authentication, proxy/egress policy, retention, and deletion behavior.
3. Pin runtime images and dependencies; run a reproducible self-host smoke test.
4. Test one explicitly owned, public, low-sensitivity site; retain capture metadata and export evidence.
5. Compare coverage, repeatability, operational cost, and integration effort against at least one adjacent web-recon candidate before any adoption decision.

## Procurement rule
No component is selected from popularity alone. Preserve the raw evidence,
source/version, date observed, and unresolved risks so later decisions can be
recomputed without rewriting history.
