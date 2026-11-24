# FOSS Procurement Research Matrix

**Research-only record.** This matrix captures technical procurement observations and source metadata. Qualified counsel owns legal interpretation and license compatibility conclusions; engineering admission decisions follow their technical workflows.


Use this matrix for inspectable dimensions and source evidence; keep vendor ranking as a separate decision.

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

Keep dimensions inspectable so later decisions can be audited; aggregate scores remain optional.

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

Vendor-specific persistence and UX remain adapters; the canonical evidence store remains the source of truth.

## Procurement rule
Select components from reproducible evidence, technical fit, and operational cost. Preserve the raw evidence,
source/version, date observed, and unresolved risks so later decisions can be
recomputed without rewriting history.
