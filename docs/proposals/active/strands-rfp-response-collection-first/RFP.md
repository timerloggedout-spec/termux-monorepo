# Proposal — Response strategy for the AWS Strands Delphi Oracle RFP — Build the DEBATE collection plane so the panel becomes executable when entitlement lands

- **Proposal ID:** strands-rfp-response-collection-first
- **Kind:** rfp-response
- **Surface:** AWS Free Tier Integration & Strands Decider Engineering Oracle RFP
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-27T08:51:57Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Build the ballot collection plane (ITEMS-003) as working code: DEBATE-conformant intake, validation, deduplication, and class-separated collection receipts, proven by the E-06 reconstruction property. Model voting itself stays disabled.

## 2. Basis in evidence

- The collection contract (ITEMS-003) is defined in DEBATE.md — source classes, normalized envelope, workflow states — but no collector exists; intake is the missing piece. (evidence: `debate:file.blob_sha`, `items.open`)
- A collector built now makes ITEMS-006 executable the moment a no-cost entitlement is validated, without enabling model voting today. (evidence: `debate:file.blob_sha`, `rfp:file.blob_sha`)
- E-06 is its natural first test: tallies must be reconstructable from the collection receipt alone. (evidence: `matrix:file.blob_sha`)

## Provenance

Generated from 1 evidence set(s), 123 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
