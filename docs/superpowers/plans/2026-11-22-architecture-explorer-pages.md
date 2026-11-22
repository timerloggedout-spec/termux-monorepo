# Architecture Explorer Pages Implementation Plan

> **For agentic workers:** Execute the proposal tasks in order. Use test-driven development for the inventory builder and UI contracts.

**Goal:** Publish a read-only architecture explorer under the existing GitHub Pages project hub.

**Architecture:** A Python builder inventories canonical Markdown/Mermaid/SVG/PNG inputs, copies them into a static bundle, and emits a provenance-bearing JSON catalog. The existing Pages workflow renders Mermaid sources to SVG and publishes the new route with the project hub.

**Tech Stack:** Python 3 standard library, static HTML/CSS/JavaScript, pinned Mermaid CLI 11.4.2, GitHub Actions Pages publisher.

**Spec:** `docs/superpowers/specs/2026-11-22-architecture-explorer-pages-design.md`

## Global Constraints

- Git-tracked Markdown, Mermaid, and SVG files remain canonical sources.
- Generated SVG/PNG files are presentation artifacts.
- GitHub Actions remains the publisher; the browser remains read-only.
- The browser contains no credentials and performs no repository mutations.
- Pages publication stays on the existing `gh-pages` branch and project-hub route.
- Build identity records the actual source SHA/ref and actual build timestamp.

## Review Focus

- Missing optional source directories: inventory generation remains successful and records the actual discovered item count.
- Unsafe or symlinked paths: the builder rejects paths outside the repository root.
- Mermaid renderer failure: publication fails before deploying a partial architecture bundle.
- Markdown content containing raw HTML: sanitize before rendering.
- SVG files containing active content: display as image assets and keep raw source available as a download/link.

---

### Task 1: Register the proposal and design

**Files:** create proposal MANIFEST/ITEMS, design, plan; update registry.

- [x] Create proposal item IDs ARCH-EXP-001..006.
- [x] Register proposal against the isolated feature branch.
- [x] Record selected route and publication boundary.

### Task 2: Build source inventory and bundle

**Files:**
- Create: `scripts/ci/build_architecture_portal.py`
- Create: `tests/test_build_architecture_portal.py`

**Interface:** `build_portal(root: Path, output: Path, source_ref: str, source_sha: str) -> dict[str, object]`; `verify_rendered(output: Path) -> list[str]`.

- [ ] Test source inventory, file copying, metadata, path containment, and Mermaid render mapping.
- [ ] Run focused unit tests and observe the expected missing-function failure.
- [ ] Implement inventory and bundle generation with standard-library modules only.
- [ ] Run focused tests and full test file.

### Task 3: Build the architecture explorer UI

**Files:**
- Create: `apps/project-pages-hub/architecture/index.html`
- Create: `apps/project-pages-hub/architecture/architecture.css`
- Create: `apps/project-pages-hub/architecture/architecture.js`
- Create: `apps/project-pages-hub/architecture/index.md`
- Modify: `apps/project-pages-hub/index.html`
- Modify: `apps/project-pages-hub/index.md`

- [ ] Add semantic HTML shell, responsive navigation, search, reader, viewer, and provenance slots.
- [ ] Add nested tree rendering, item selection, Markdown rendering, and safe local-link routing.
- [ ] Add diagram zoom/pan/fit/fullscreen and source toggles.
- [ ] Add project-hub route links and the Markdown mirror.

### Task 4: Integrate the Pages publication pipeline

**Files:**
- Modify: `.github/workflows/tribute-dashboard-deploy.yml`
- Modify: `scripts/ci/verify_agent_readability_surfaces.py`

- [ ] Add architecture source paths to the Pages workflow triggers.
- [ ] Copy the page shell and build the source bundle under `_site/architecture/`.
- [ ] Render each catalogued Mermaid source to SVG using pinned Mermaid CLI.
- [ ] Verify every Mermaid SVG exists before the Pages publish step.
- [ ] Extend readability and workflow-copy assertions.

### Task 5: Reconcile navigation and operating documentation

**Files:**
- Modify: `docs/ops/SITE-MAP.md`
- Modify: `docs/DEPLOYMENT-LANES.md`
- Modify: `docs/ops/DEPLOYMENT-LANES.md`
- Modify: `.agents/skills/github-pages-operator/SKILL.md`
- Modify: `docs/ops/SHE-DASHBOARD-INDEX.md`

- [ ] Add the canonical architecture route and owner boundaries.
- [ ] Keep publication state marked unverified until deployment evidence exists.

### Task 6: Verify current head and publication

- [ ] Run focused builder tests.
- [ ] Run the readability verifier and relevant static-site tests.
- [ ] Run repository dual gates where the execution environment supports them.
- [ ] Open PR with `Implements: ARCH-EXP-002`.
- [ ] WAIT for terminal Actions results; re-fetch SHA, jobs, steps, and artifacts.
- [ ] Verify the published route and its embedded source SHA.
- [ ] Record deployment state as configured/verified only when supported by evidence.
