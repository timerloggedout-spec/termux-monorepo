# FOSS Procurement Matrix

The matrix is a decision-support record, not a vendor scorecard.

## Required fields
- resource_id
- project
- canonical_source
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
