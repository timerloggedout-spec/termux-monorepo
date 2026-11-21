# Plan — Repository-subject evaluation and certification profile

**Proposal:** `repository-subject-certification-profile`  
**Branch:** `feat/repository-subject-certification-profile-20261114`  
**Base:** `master`  
**Date:** 2026-11-14

## Outcome

Add a standalone, evidence-backed evaluation profile that treats `timerloggedout-spec/termux-monorepo` as the subject under evaluation. Reuse the canonical Agent Evaluation Framework (AEF), DoE, BIUDL, ATES, and existing repository gates. Produce a portable evidence dossier that an external certifying authority can inspect without implying that the repository or ChatGPT has already been certified.

## Scope

- Register a P1 proposal and bounded work items.
- Define subject identity, evaluation boundary, criteria, evidence references, verdicts, limitations, and certification disposition.
- Provide a strict JSON Schema and a blank report template.
- Explicitly separate repository-subject evaluation from a human-assistance service classification.
- Preserve external platform terms and program rules as independent obligations; do not assert an exemption or authorize circumvention.
- Link existing AEF/DoE/ATES and dual-gate authorities rather than duplicating them.

## Non-goals

- No new evaluator, benchmark engine, scheduler, telemetry store, leaderboard, or dispatch path.
- No claim of external certification, accreditation, legal interpretation, or terms-of-service exemption.
- No external submission, account action, credential access, paid service, deployment, or merge.
- No change to existing certification-program assessments or protected exam rules.

## Implementation tasks

1. Register proposal, manifest, and item ledger.
2. Add the evaluation profile and evidence dossier template.
3. Add strict JSON Schema for a single repository-subject evaluation report.
4. Cross-link the canonical evaluation and governance documents.
5. Validate JSON, YAML structure, links, diff hygiene, and required repository gates on the exact PR head.

## Acceptance

- The report pins repository + immutable commit SHA.
- Each criterion has a state and at least one evidence reference for PASS/FAIL/PARTIAL.
- Missing evidence remains UNKNOWN, never silently PASS or zero.
- Internal evaluation and external certification disposition are independent.
- Owner-supplied scope assertions are labelled as assertions until reviewed against the named program's published rules.
- No duplicate source of truth is introduced.
