# Delphi Oracle Harmonious Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Ship a separate, source-backed Delphi Oracle intake with research checkboxes, Harmonious Reconciliation, Question Matrix settings, optional oversight, selection review, and registry-catalogue PRs.

**Architecture:** A new GitHub Issue Form feeds a deterministic stdlib-only normalizer that reads the existing research and DoE registries. A dedicated issue workflow records normalized selections, triggers review idempotently, and opens a separate catalogue PR when requested; the legacy quota RFP gate remains isolated.

**Tech Stack:** GitHub Issue Forms YAML, GitHub Actions, Python 3.9+ standard library, GitHub REST via actions/github-script.

**Spec:** `docs/superpowers/specs/2026-11-24-delphi-oracle-harmonious-intake-design.md`

## Global Constraints

- Preserve `.github/ISSUE_TEMPLATE/delphi-rfp.yml` and the legacy quota gate.
- Use the existing research participant, silo, DoE component, proposal, and RFP-segment registries as authorities.
- Preserve independent research segments; do not aggregate cross-silo scores.
- Prior default = 12 baseline research participants only.
- Every normalized selection has `execution: false`.
- Registry catalogue writes open a PR to `master`; intake automation does not write directly to master.
- Python implementation uses the standard library only and supports Python 3.9+.
- Optional WebView oversight remains optional and metadata-only.

## Review Focus

1. A malformed or multiply checked selection mode must fail closed with a precise validation error.
2. Missing issue numbers in a source catalogue must remain explicit nulls rather than becoming fabricated IDs.
3. Re-edited issues must update the same normalized comment and avoid duplicate review/catalogue entries.
4. Concurrent catalogue submissions must use isolated per-issue branches and preserve all prior catalogue records.
5. Every selection mode must preserve research-silo independence and the immutable execution=false boundary.

---

### Task 1: Proposal and design contracts

**Files:**
- Create: `docs/proposals/active/delphi-oracle-harmonious-intake/MANIFEST.md`
- Create: `docs/proposals/active/delphi-oracle-harmonious-intake/ITEMS.md`
- Modify: `docs/proposals/registry.yaml`
- Modify: `config/context_relationships/scope_registry.json`
- Create: this spec and plan

**Interfaces:** Proposal ID `delphi-oracle-harmonious-intake`; item IDs DORI-001 and DORI-002.

- [x] Register proposal and item ledger before implementation.
- [ ] Validate proposal registry and scope JSON in CI.

### Task 2: Intake form and normalizer

**Files:**
- Create: `.github/ISSUE_TEMPLATE/delphi-oracle-intake.yml`
- Create: `scripts/delphi/intake.py`
- Create: `tests/test_delphi_intake.py`

**Interfaces:**
- `parse_issue_body(body: str) -> dict[str, str]`
- `normalize_intake(issue: dict, body: str, root: Path) -> dict`
- `load_catalogues(root: Path) -> dict`
- CLI: `python3 scripts/delphi/intake.py --issue-json <path> --output <path>`

- [ ] Write tests for default, All, DoE Decides, specific selection, invalid multi-selection, and unknown IDs.
- [ ] Run focused tests and observe expected failures.
- [ ] Implement normalizer using source JSON registries.
- [ ] Add form checkbox groups for 12 participants, four DoE components, related RFPs, projects, and panel/reconciliation choices.
- [ ] Add dropdowns for request, method, rounds, matrix strategy, and disposition.
- [ ] Run focused tests and form/catalogue consistency checks.

### Task 3: Review and registry catalogue workflow

**Files:**
- Create: `.github/workflows/delphi-oracle-intake.yml`
- Create: `ops/delphi/selection-catalogue.json`
- Modify: `tests/test_delphi_intake.py`

**Interfaces:**
- Workflow trigger: issue opened/edited when the body contains the new form's unique headings.
- Normalized record schema: `delphi.oracle-intake.v1`.
- Comment marker: `<!-- delphi-oracle-intake-record:v1 -->`.
- Catalogue schema: `delphi.selection-catalogue.v1`.

- [ ] Write workflow contract tests for issue-only trigger, permissions, idempotent marker, and execution=false.
- [ ] Implement normalized comment update/create and selection-review label.
- [ ] Implement per-issue catalogue branch and PR creation/update against master.
- [ ] Ensure no `delphi:rfp` label is added by the new form/workflow.
- [ ] Run focused tests.

### Task 4: Verification, documentation, and promotion

**Files:**
- Modify: proposal ITEMS and MANIFEST as evidence lands.
- Modify: focused tests if required by review.

- [ ] Run focused Delphi intake and legacy gate tests.
- [ ] Run proposal registry validation.
- [ ] Run repo-gate and Termux smoke through PR Actions.
- [ ] Fetch every required check, job, step, and review against the same immutable head SHA.
- [ ] Resolve Critical/Important review findings and rerun affected tests.
- [ ] Merge to master only after all required gates and review are green.
- [ ] Re-fetch master and verify the merge commit and availability of the new Issue Form.

## Completion Evidence

PR URL, merged SHA, exact-head check receipts, review disposition, focused test result, proposal registry status, and new form path.
