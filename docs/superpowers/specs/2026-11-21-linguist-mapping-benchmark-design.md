# Linguist Mapping Benchmark — Design

Date: 2026-11-21
Proposal item: NSE-024
Status: proposed implementation design

## Intent

Create a reproducible retrieval benchmark over source-backed Linguist mapping assertions. Use the existing canonical panel feed as an input surface while preserving the feed's authority, provenance, semantic distinctions, and snapshot age.

## Goals

- Preserve the curated Fleet ⇔ Lean/Mathlib and nomenclature crosswalk evidence.
- Project enumerated feed records into deterministic, unique benchmark record IDs and stable source identity keys.
- Retain exact, approximate, analogue, lossy, and unverified grades without promoting candidate relations.
- Generate deterministic corpus/query/qrels/candidate/hard-negative artifacts and score rankings only when ranked outputs exist.\n- Enforce query-specific candidate-pool boundaries during evaluation.
- Keep experiment artifacts separate from the dashboard's runtime feed contract.

## Non-goals

- Replacing the canonical panel feed or runtime mapping sources.
- Embedding full corpora, qrels, or hard-negative lists into `linguist.html`.
- Claiming retrieval accuracy without evaluated rankings.
- Enumerating count-only pointer inventories or inferring semantic equivalence from token frequency.
- Changing the page renderer in this implementation slice.

## Approaches

1. **Project the canonical feed through a benchmark adapter — selected.** The page already consumes the generated feed as its source of record. A Python adapter can preserve feed provenance and snapshot metadata while producing reproducible experiment records.
2. **Read mapping sources independently in the page.** Rejected because it duplicates source selection and bypasses the existing feed-only page contract.
3. **Embed the full benchmark dataset in the feed or page.** Rejected because retrieval artifacts are experimental data; the page should receive a compact, evidence-backed summary in a separate follow-on item.

## Design decisions

- Use `mapping_id` or `label_id` when present; otherwise use the family-scoped entry ID.
- Keep a family-scoped source identity key; append a digest of the canonical source record to create a snapshot-scoped unique benchmark record ID.
- Collapse exact duplicate source records and preserve their occurrence count.
- Preserve semantic mapping grade independently from codec round-trip status; round-trip success does not imply exact semantic equivalence.
- Preserve evidence state, relation, confidence, kernel, provenance, and `generated_at`.
- Exclude families marked `entries_included: false`.
- Keep the dashboard projection separate from the benchmark generator.

## Acceptance

NSE-024 acceptance criteria in `docs/proposals/active/notation-sets/ITEMS.md` govern this design. Required checks are focused benchmark tests, proposal registry validation, repo-gate, and Termux smoke on one immutable PR head.
