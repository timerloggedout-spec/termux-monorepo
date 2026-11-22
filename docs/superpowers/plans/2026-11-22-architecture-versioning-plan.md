# Architecture Versioning and Automated Refresh Implementation Plan

> For agentic workers: use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Version architecture changes and automatically generate verifiable architecture manifests and diagram projections through the existing documentation workflow.

**Architecture:** Canonical architecture documents and Mermaid sources remain authoritative. A focused Python generator fingerprints the source set and paired diagram renders. The existing Automation Documentation Continuous Refresh workflow validates pull requests and commits generated projections after trusted master pushes.

**Tech Stack:** Python 3.12, unittest, GitHub Actions, Mermaid CLI 11.4.2, Markdown, JSON, SHA-256.

**Spec:** docs/superpowers/specs/2026-11-22-architecture-versioning-design.md

## Global Constraints

- Use stable MAJOR.MINOR.PATCH architecture versions; initial governed baseline is 1.0.0.
- Semantic architecture source changes require VERSION and CHANGELOG updates in the same pull request.
- Domain specifications and source code retain semantic authority; architecture.md is a navigation and synthesis entry.
- Mermaid sources remain canonical; SVG and PNG files remain generated projections.
- Reuse the existing Automation Documentation Continuous Refresh workflow and its trusted master writer.
- Pull-request validation remains read-only and uploads generated evidence.
- The manifest omits timestamps and run-specific metadata to preserve deterministic output.
- BRR remains read-only; branch reconciliation and promotion follow repository governance.

## Review Focus

- Initial baseline where the base branch predates VERSION: require exactly 1.0.0 and a changelog entry; covered by test_version_check_accepts_initial_1_0_0_baseline.
- Invalid or non-increasing semantic versions: fail closed; covered by test_invalid_semver_is_rejected and test_version_check_rejects_non_increasing_version.
- Changelog ordering: require the current version as the first release heading; covered by test_version_check_requires_current_version_at_top_of_changelog.
- Architecture Mermaid source without a paired Markdown map: fail manifest generation; covered by test_manifest_rejects_unpaired_flow_source.
- Missing or changed diagram render and stale manifest: fail validation; covered by test_manifest_rejects_missing_render and test_write_and_check_detect_stale_manifest.
- Generated architecture files must classify as projections rather than canonical source changes; covered by test_architecture_sources_and_generated_manifest_are_classified.

---

### Task 1: Specify manifest and version-gate behavior

**Files:**
- Create: tests/test_architecture_docs.py
- Modify: tests/test_automation_docs.py

**Interfaces:**
- Tests consume build_manifest(root), write_manifest(root), check_manifest(root), and check_version_bump(root, base_ref).
- Tests consume automation_docs.classify_material_paths(values).

- [x] Write the focused tests before implementation.
- [x] Run the test module while the generator is absent; expected failure was the missing scripts/ci/architecture_docs.py module.
- [x] Add cases for determinism, source coverage, render presence, paired flow mappings, stale manifests, SemVer, initial baseline, required bump, and generated-path classification.
- [x] Run the fixture suite after implementation; 10 tests passed locally.
- [x] Commit tests first on the predecessor branch; replay with action-first subjects on the successor branch.

### Task 2: Implement deterministic manifest generator

**Files:**
- Create: scripts/ci/architecture_docs.py
- Test: tests/test_architecture_docs.py

**Interfaces:**
- build_manifest(root: Path) -> dict[str, object]
- manifest_text(root: Path) -> str
- write_manifest(root: Path) -> None
- check_manifest(root: Path) -> bool
- check_version_bump(root: Path, base_ref: str) -> bool

- [x] Implement stable SemVer parsing and source-set discovery.
- [x] Include per-file and source-set SHA-256 fingerprints.
- [x] Include architecture-flow SVG and operational-diagram PNG source/render fingerprints.
- [x] Require paired Markdown mapping files for architecture flow Mermaid sources.
- [x] Enforce same-change VERSION and CHANGELOG updates and a strictly increasing version.
- [x] Run all 9 focused tests and Python compilation locally.
- [x] Commit the generator and pairing guard on the successor branch with action-first subjects.

### Task 3: Establish the version contract

**Files:**
- Create: docs/architecture/VERSION
- Create: docs/architecture/VERSIONING.md
- Create: docs/architecture/CHANGELOG.md

- [x] Set the initial architecture version to 1.0.0.
- [x] Define MAJOR, MINOR, and PATCH semantics.
- [x] Define same-PR version/changelog requirements and the initial-baseline rule.
- [x] Define deterministic manifest fields and the trusted refresh lifecycle.
- [x] Commit the version contract on the successor branch with action-first subjects.

### Task 4: Extend architecture maps and navigation

**Files:**
- Create: docs/architecture/flows/architecture-governance.md
- Create: docs/architecture/flows/architecture-governance.mmd
- Modify: architecture.md
- Modify: docs/architecture/README.md
- Modify: docs/architecture/flows/README.md
- Modify: docs/ops/diagrams/repository-data-flow.mmd
- Modify: docs/ops/diagrams/automation-overview.mmd

- [x] Add the architecture versioning flow as a paired Markdown/Mermaid module.
- [x] Apply the six-step Observe / Choose / Act / Verify / Record / Repeat-or-stop loop.
- [x] Link the new module, current version, versioning contract, and generated manifest from architecture navigation.
- [x] Add the documentation lane to the repository data-flow and automation overview diagrams.
- [x] Commit map and index updates on the successor branch with action-first subjects.

### Task 5: Integrate existing automation

**Files:**
- Modify: scripts/ci/automation_docs.py
- Modify: tests/test_automation_docs.py
- Modify: .github/workflows/automation-docs-continuous-refresh.yml

- [x] Classify architecture sources as material documentation and architecture/generated as generated-only.
- [x] Add regression coverage for both classifications.
- [x] Extend workflow path filters for architecture sources, version contract, generator, and tests.
- [x] Run focused tests in both pull-request and trusted master jobs.
- [x] Render architecture flow diagrams to SVG and retain operational PNG rendering.
- [x] Validate version delta, generate/check manifest, and upload PR review artifacts.
- [x] Refresh generated architecture projections through the existing trusted master job.
- [x] Commit automation integration on the successor branch with action-first subjects.

### Task 6: Register proposal scope and evidence

**Files:**
- Modify: docs/proposals/active/repository-architecture-entry/ITEMS.md
- Modify: docs/proposals/active/repository-architecture-entry/MANIFEST.md
- Modify: docs/proposals/registry.yaml

- [x] Register REPO-ARCH-007.
- [x] Record the new implementation branch and versioning scope.
- [x] Preserve the earlier proposal work items and pending validation gates.
- [x] Commit proposal registration on the successor branch with action-first subjects.

### Task 7: Validate the exact branch and reconcile

**Files:**
- Review all changed files and generated artifacts.
- Review: pull-request checks, workflow run, manifest, rendered SVG/PNG outputs.

- [x] Add workflow contract tests for PR read-only permissions, trusted master write authority, immutable artifact action, and architecture path filters.
- [x] Restrict workflow_dispatch and trusted generated-file writes to refs/heads/master; add a regression assertion for the branch guard.
- [x] Prove generated-only projection refreshes preserve the architecture version.
- [ ] Run the focused repository tests on the exact branch head in GitHub Actions.
- [ ] Run repository gate, Markdown/workflow validation, CodeQL, and Termux smoke where the workflow matrix admits them.
- [ ] Verify the architecture flow pair inventory and Mermaid rendering.
- [ ] Inspect the generated manifest and uploaded artifact.
- [ ] Re-fetch current master and branch heads; compare base/head ancestry and changed paths.
- [ ] Request an independent code review and resolve material findings.
- [ ] Observe the trusted master refresh after promotion and verify the generated manifest and diagram assets on the resulting master SHA.

## Execution record

- Branch: docs/architecture-versioning-automation-20261122-v2.
- Branch base at creation: 697c0a43e57ea16c1503826d48a1f0d7f58c3fa6.
- BRR prior-art finding: the earlier architecture-entry branch was materially stale; compare evidence showed it 1,124 commits behind with two branch-only commits. The predecessor branch was fast-forwarded to its then-current master before implementation; the successor branch starts from the latest master.
- Workspace adaptation: this session has GitHub connector access; the isolated remote feature branch is the working workspace. Local fixture tests provide unit evidence and GitHub Actions supplies integration evidence.
- Loopy adaptation: use Observe → Choose → Act → Verify → Record → Repeat-or-stop. The supplied Loop Library specification provides the six-step workflow contract; published catalog matching remains an open discovery item, so this implementation uses the project-local loop.
- Local verification: 15/15 architecture manifest and workflow tests passed; Python compilation passed.
- PR #5770 was superseded after the DO Statement Style audit identified non-imperative commit subjects. The successor branch starts at current master 697c0a43e57ea16c1503826d48a1f0d7f58c3fa6; the eleven-commit master-side delta contains generated operational records and has zero path overlap.
- The initial combined status records Vercel daily deployment quota exhaustion; adaptive-wait classifies Vercel as an advisory signal. The successor branch uses imperative commit subjects to satisfy the repository style gate.
- Successor PR #5771 is open and ready for review; GitHub PR metadata owns the live head SHA and mergeability state.
- Pending evidence: exact PR-head Actions, independent review, generated artifact inspection, and trusted master refresh.


- Successor delivery branch: docs/architecture-versioning-automation-20261122-v2, created from current master and rebuilt with imperative commit subjects.
- Predecessor PR #5770 is closed as superseded and retained in the proposal registry for provenance.
