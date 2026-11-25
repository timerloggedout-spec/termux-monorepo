# Legal and licensing research silo

**Purpose:** preserve public-source legal, licensing, copyright, contract, and terms observations in an isolated research area.

## Authority boundary

- Record source-attributed facts, exact source URLs, retrieval dates, source revisions, and uncertainty.
- Quote or summarize the source's own statements; distinguish direct source text from technical observation.
- Mark unavailable, ambiguous, conflicting, or stale evidence as unresolved.
- Route requests for legal interpretation, compliance conclusions, or rights determinations to qualified legal counsel.
- Keep research records separate from production source, CI, runtime routing, deployment, and merge gates.

This silo preserves source-attributed observations, provenance, dates, and uncertainty. Qualified legal counsel provides legal advice, interpretation, compliance conclusions, and rights determinations.

## Production interface

Production engineering consumes technical facts that can be independently tested: public API behavior, protocol and file-format observations, reproducible test results, performance, security findings, and availability evidence.

Production controls remain engineering controls: vulnerability detection, secret scanning, dependency integrity, privacy/data minimization, authentication, explicit operator authorization, and tests.

Production gates consume technical evidence and explicit operator decisions. Legal/licensing research remains an informational source record. The `operator_authorized` field expresses operator intent for a specific provider/model route; qualified counsel owns legal interpretation.

## Independent implementation and reverse engineering

Use public specifications, documented interfaces, templates, observed behavior, and authorized interoperability research as technical inputs. Record source provenance and distinguish observed behavior from hypotheses. Build independent implementations and adapters with original code and tests.

Keep third-party source code, assets, and substantial copied expression in their own provenance records. Technical compatibility findings and legal conclusions remain separate work products. Route legal questions about a particular target, source, or intended use to qualified counsel.

## Record format

Each research record should include:

- source identity and canonical URL;
- source type and exact version, revision, or publication date;
- retrieval timestamp;
- attributed statement or observed fact;
- evidence excerpt or stable locator;
- confidence and freshness;
- conflicting statements and unresolved questions;
- technical implications, when directly testable;
- counsel referral status for legal interpretation requests.

Use explicit states such as `OBSERVED`, `SOURCE_CLAIM`, `CONFLICTED`, `STALE`, and `UNKNOWN`. Keep legal conclusions outside automated agent output.

## Existing research inputs

- [Provider access and source notes](PROVIDER-ACCESS-SOURCE-NOTES.md)
- [FOSS procurement research matrix](FOSS-PROCUREMENT-MATRIX.md)
- [Procurement licensing observations](PROCUREMENT-LICENSE-OBSERVATIONS.jsonl) — legacy recorded values, preserved as unverified repository metadata. Each row pins the original ledger version with `source_record_commit`, `source_record_blob_sha`, and physical 1-based `source_record_line`.
- [FOSS procurement records](../../docs/research/FOSS-PROCUREMENT-RECORDS-2026-10-02.json) — historical source data

**Owner direction:** research informs engineering discovery; qualified counsel owns legal interpretation; production owns technical implementation and verification.
