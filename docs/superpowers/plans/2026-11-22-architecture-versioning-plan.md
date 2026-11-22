# Architecture Versioning and Automated Refresh — Implementation Plan

**Design:** [architecture versioning design](../specs/2026-11-22-architecture-versioning-design.md)  
**Implementation branch:** docs/architecture-versioning-automation-20261122  
**Base at branch creation:** f649cd9094c2bbc9e468f77c24edc022ac253e03  
**Method:** test-first, small commits, existing workflow reuse, evidence-backed reconciliation

## Tasks

1. Add focused tests for manifest determinism, source coverage, missing renders, stale output, SemVer, changelog, and required version bumps.
2. Implement the deterministic manifest generator and version-delta gate.
3. Establish the initial version and changelog, then document the semantic version policy.
4. Add the architecture-governance Markdown map and Mermaid source.
5. Extend the root architecture entry and both architecture navigation indexes.
6. Extend the existing automation path classifier and its regression tests.
7. Extend the existing continuous-refresh workflow for architecture flow SVGs, manifest validation, review artifacts, and trusted master refresh.
8. Register the work under REPO-ARCH-007 and update proposal evidence.
9. Run focused tests, syntax checks, repository gates, and PR Actions; WAIT, WATCH, RE-FETCH, and compare the final head and generated artifacts.

## Verification record

- Local test-first check: the new test module initially failed because scripts/ci/architecture_docs.py was absent.
- Local implementation check: 7 focused tests passed after the generator was implemented.
- Local Python compilation: passed.
- Repository Actions, Mermaid CLI, repository gate, Termux smoke, and trusted master refresh remain pending until the branch is pushed and the PR validation cohort completes.

## Execution constraints

This session has GitHub connector access and no network-enabled local Git checkout. An isolated GitHub feature branch is used as the working branch. Repository Actions provide the authoritative integration environment and runtime evidence. The existing BRR inventory is read-only and remains the branch-reconciliation source; this plan does not mutate other branches.
