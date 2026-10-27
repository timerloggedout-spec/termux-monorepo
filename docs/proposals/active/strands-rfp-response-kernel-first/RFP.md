# Proposal — Response strategy for the AWS Strands Delphi Oracle RFP — Extend the merged offline kernel along the matrix's recommended experiment order

- **Proposal ID:** strands-rfp-response-kernel-first
- **Kind:** rfp-response
- **Surface:** AWS Free Tier Integration & Strands Decider Engineering Oracle RFP
- **Deadline:** UNVERIFIED — confirm from the official page
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-27T08:51:57Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Make the kernel's own experiments executable pass suites (E-05, E-01, E-03) against the frozen cohort, and publish their receipts as the RFP's first implementation evidence. Nothing else moves: the panel and the deployment stay blocked, recorded specified_not_run.

## 2. Basis in evidence

- The deterministic baseline and frozen fixture corpus already exist and are merged (ITEMS-005 in review), and the kernel's receipt already reports E-01/E-03/E-05 metrics on that cohort. (evidence: `mvppr:pr.merged`, `items.open`)
- The experiment matrix names E-05, E-01, E-03 as the recommended first three, all offline-runnable. (evidence: `matrix.first_three`)
- This strategy closes the kernel side only: the model panel (ITEMS-006) and the deployment (ITEMS-007) stay blocked and are recorded specified_not_run. (evidence: `items.open`)

## Provenance

Generated from 1 evidence set(s), 123 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
