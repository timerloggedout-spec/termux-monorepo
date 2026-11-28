# Ingestion contract

## Lifecycle

| Stage | Input | Output | Completion evidence |
|---|---|---|---|
| DISCOVER | Provider query, repository, patent/paper index | Candidate source | Provider, query, retrieval timestamp |
| RESOLVE | Candidate URL or identifier | Canonical source identity | DOI, patent publication number, repository ID, or canonical URL |
| CLASSIFY | Resolved source | Collection and source type | Taxonomy version and rationale |
| FETCH | Authorized source | Original artifact | HTTP/provider status, MIME type, byte count |
| HASH | Original bytes | Integrity record | SHA-256 and exact byte size |
| EXTRACT | Supported artifact | Text, metadata, links | Extractor/version, status, warnings |
| LINK | Extracted metadata | Graph edges | Typed edge, source evidence and locator |
| VALIDATE | Source + extraction + graph | Validated record | Schema and provenance checks |
| INDEX | Validated record | Searchable graph/document index | Index version and record ID |
| DOCUMENT | Snapshot | Markdown + JSON reports | Generator version, source snapshot hash |

## State model

`discovered → resolved → classified → fetched → hashed → extracted → linked → validated → indexed → documented`

Terminal or recoverable states include `skipped`, `restricted`, `unsupported`, `partial`, `retryable_failure`, and `permanent_failure`. Each transition records `observed_at`, actor/workflow identity, source ID, and a reason.

## Storage accounting

Record original `size_bytes`, extracted-text `size_bytes`, normalized metadata `size_bytes`, and total stored bytes independently. Record MIME type, encoding, compression, object URI, SHA-256, retention class and storage tier. Deduplicate byte-identical artifacts by SHA-256 while preserving every source URL and citation relationship.

## Source and claim provenance

Each claim stores its text, subject, predicate, object/value, evidence source ID, source locator (page, section, paragraph, patent claim, repository path, commit or dataset row), extraction method, observation timestamp, and confidence/verification state. Separate source-authored statements from generated summaries and system inferences.

## Access and licensing

Store access mode (`open`, `registration_required`, `restricted`, `metadata_only`, `unknown`), license identifier/text, rights URL, and permitted operations. Metadata-only records remain useful when full-text retention is unavailable. Preserve publisher URLs and use authorized APIs or downloads.

## Documentation output

Every snapshot emits:
- `sources.json` and `sources.md`
- `entities.json` and `entities.md`
- `relationships.json` and `relationships.md`
- `storage-manifest.json` and `storage-manifest.md`
- `INGESTION-REPORT.md`

The Markdown view explains all Siglary operators in plain language. The machine view records canonical operator IDs, glyphs, signatures, constraints and version.
