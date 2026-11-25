# Central Flywheel Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a central nested Flywheel hub that links registered channels and cross-channel work topics to their canonical artifacts.

**Architecture:** A curated Markdown hub lives beside the canonical Flywheel policy and registry. Root architecture and ICM routes point to it; channel stores, protocol documents, GitHub work records, commits, and tests remain authoritative. The Context Relationship Graph remains a supplemental metadata-only index.

**Tech Stack:** Markdown, JSON registry, GitHub links, repository proposal validation.

**Spec:** `docs/superpowers/specs/2026-11-25-central-flywheel-navigation-design.md`

## Global Constraints

- Preserve FLY-001…FLY-006 IDs, scopes, participants, cadence, and append-only stores.
- FLY-005 remains exports/backup coordination; FLY-006 remains non-export pair work; FLY-003 remains confirmations of record.
- Link to JSONL stores; keep message bodies in their registered stores.
- Use exact paths, GitHub IDs, and commit SHAs.
- Distinguish verified, candidate, and unknown relationships.
- Keep the Context Relationship Graph metadata-only and disclose its 2026-10-26 partial-history snapshot.
- Cite `Implements: REPO-ARCH-007` in commits and PR context.

## Review Focus

- FLY-005 pointer resolves to the actual FLY-006 protocol/store and linked report.
- All six registry rows appear exactly once with correct channel boundaries.
- Topic-to-artifact links target exact existing paths and IDs.
- The hub does not imply that PR #5893 is merged or that branch-only NSE-021 design is implemented.
- The stale Context Relationship Graph is described as historical/partial rather than current.

---

### Task 1: Create the central Flywheel hub

**Files:**
- Create: `docs/ops/flywheel-comms/README.md`

**Interfaces:**
- Consumes: `POLICY.md`, `REGISTRY.json`, FLY-005/006 protocol and store paths, exact GitHub artifact links.
- Produces: the canonical navigation entry for channels, topics, and evidence links.

- [ ] **Step 1: Write the hub** with sections for operating model, channel map, FLY-005 → FLY-006 handoff, topic index, artifact relationship pattern, source authority, and freshness.
- [ ] **Step 2: Verify every cited channel and topic record** against its canonical registry row, protocol, store, document, issue/PR, commit, or test.
- [ ] **Step 3: Review scope labels** for FLY-003, FLY-005, and FLY-006.
- [ ] **Step 4: Commit** the hub with `Implements: REPO-ARCH-007`.

### Task 2: Route repository navigation to the hub

**Files:**
- Modify: `docs/icm/cards/flywheel-comms.md`
- Modify: `docs/icm/CLAUDE.md`
- Modify: `architecture.md`

**Interfaces:**
- Consumes: the hub from Task 1.
- Produces: discoverable root architecture and ICM routes.

- [ ] **Step 1: Update the ICM card** to list FLY-001…FLY-006 via the canonical registry and make the hub its primary route.
- [ ] **Step 2: Add an ICM route** for navigating Flywheel channels and cross-channel work artifacts.
- [ ] **Step 3: Add the hub** to the architecture canonical source index and documentation taxonomy.
- [ ] **Step 4: Verify** every new internal route resolves.
- [ ] **Step 5: Commit** with `Implements: REPO-ARCH-007`.

### Task 3: Record design, plan, and proposal linkage

**Files:**
- Create: `docs/superpowers/specs/2026-11-25-central-flywheel-navigation-design.md`
- Create: `docs/superpowers/plans/2026-11-25-central-flywheel-navigation.md`
- Modify: `docs/proposals/active/repository-architecture-entry/ITEMS.md`

**Interfaces:**
- Consumes: accepted proposal `repository-architecture-entry`.
- Produces: durable design, implementation sequence, and REPO-ARCH-007 lifecycle record.

- [ ] **Step 1: Register REPO-ARCH-007** as executing under the accepted proposal.
- [ ] **Step 2: Save this design and plan** with exact source paths and acceptance criteria.
- [ ] **Step 3: Validate proposal registry** with `python3 scripts/proposals/validate_registry.py`.
- [ ] **Step 4: Commit** with `Implements: REPO-ARCH-007`.

### Task 4: Verify the complete navigation graph

**Files:**
- Test: repository documentation/link checks and proposal validation.

- [ ] **Step 1: Run** `git diff --check`.
- [ ] **Step 2: Run** `python3 scripts/proposals/validate_registry.py`.
- [ ] **Step 3: Run** `python3 scripts/ci/repo_gate.py`.
- [ ] **Step 4: Run** `python3 scripts/ci/termux_smoke.py`.
- [ ] **Step 5: Inspect the final diff** for exact links, scope accuracy, confidence labels, and no channel payload duplication.
- [ ] **Step 6: Record the tested SHA** in the PR and WAIT for required checks on that exact SHA.

