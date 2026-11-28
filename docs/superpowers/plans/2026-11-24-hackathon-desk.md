# Hackathon Desk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build a full teammate-facing Hackathon Desk with GitHub-owned contribution authentication, source-backed opportunities/challenges/pipelines, guides, and accessible responsive UI.

**Architecture:** Static Tribute page with a focused feed/render module. Public repository feeds remain canonical; browser actions navigate to GitHub for authentication and writes. Existing proposal, challenge, QUE, and dispatch systems remain authoritative.

**Tech Stack:** HTML, CSS, browser JavaScript, Python/pytest tests, existing GitHub Pages deployment.

**Spec:** docs/superpowers/specs/2026-11-24-hackathon-desk-design.md

## Global Constraints

- Keep the portal read-only; GitHub owns authentication and repository write permissions.
- Use ops/que/feeds/opportunity-priority.json for ranked opportunities.
- Use ops/challenge/coordinator.json for challenge event, participant, and gate state.
- Use apps/tribute-dashboard/data/challenge-countdowns-feed.json for published countdown instants and prize projection.
- Use desk traversal, QUE queue, and dispatch feeds as read-only evidence.
- Exclude metrics_internal, win_probability, admin-only metrics, credentials, and unconsented contact details.
- Preserve visible provenance and explicit missing/stale states.
- Reuse apps/tribute-dashboard/dashboard.css and current Tribute deployment.
- Target WCAG 2.2 AA; preserve keyboard and reduced-motion behavior.
- Cite Implements: HD-<ITEM-ID> in commit/PR context.

## Review Focus

1. Missing or malformed feeds — show a clear unavailable state and preserve the rest of the page.
2. Stale opportunity feed — show its timestamp and stale status while retaining the source data.
3. Expired or unrecorded event deadlines — derive countdown from recorded instants and label absent dates truthfully.
4. Malicious feed text or external URLs — escape text and allow only approved HTTPS destinations.
5. Small screens, keyboard-only use, zoom, and reduced-motion preferences — preserve all content and interaction paths.

---

### Task 1: Feed normalization and source freshness

**Files:**
- Create: scripts/dashboards/challenge_public_feed.py (allowlisted public projection from the coordinator)
- Modify: .github/workflows/challenge-countdowns-feed-collect.yml (generate and publish both challenge feeds in the same refresh PR)
- Create: apps/tribute-dashboard/data/challenge-public-feed.json (generated dashboard artifact)
- Create: apps/tribute-dashboard/hackathon.js
- Create: tests/hackathon-desk.test.cjs
- Create: tests/test_hackathon_desk.py

**Interfaces:**
- Produces: an allowlisted `challenge-public-feed/v1` artifact plus HackathonDesk.normalizeOpportunityFeed(payload, now), normalizeChallengeFeed(payload), normalizeCountdownFeed(payload), normalizePipelineFeed(payload), and safeExternalUrl(value).
- The browser fetches `https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/que/feeds/opportunity-priority.json` for ranked opportunities and `./data/challenge-public-feed.json` for challenge events/gates. It fetches countdown, desk, QUE queue, and dispatch mirrors from `./data/challenge-countdowns-feed.json`, `./data/desk-feed.json`, and `./data/que-queue-feed.json`. Pipeline dispatch evidence is read from the `dispatch_claims` object embedded in the QUE queue feed; the separate `dispatch-state-feed.json` is empty on master and stays outside browser requests until it contains a valid published contract.
- The browser MUST NOT fetch `ops/challenge/coordinator.json`. The generator copies only explicitly allowlisted public fields, recursively excludes `metrics_internal` and `win_probability`, and tests the exclusion at every nesting level. The generated artifact is deployed with the dashboard tree.
- Returns normalized records with source, generated_at, freshness, and explicit status values.

- [ ] Write Python tests first for the projection allowlist, nested forbidden-key exclusion, deterministic output, and coordinator input failures.
- [ ] Write Node tests for fresh/stale/missing/malformed opportunity feeds, public challenge projection states, closed events, null deadlines, and safe URL validation.
- [ ] Assert the deployed opportunity URL and all three dashboard-relative feed URLs resolve from the deployed Hackathon Desk origin; treat unavailable feeds as explicit unavailable states.
- [ ] Run pytest -q tests/test_hackathon_desk.py and node --test tests/hackathon-desk.test.cjs; verify each new behavior fails for its expected reason.
- [ ] Implement the allowlisted projection generator and wire it into the existing challenge-countdowns-feed-collect workflow so coordinator changes regenerate both feeds in one refresh PR.
- [ ] Implement pure normalizers and escaping/link validation in hackathon.js.
- [ ] Run focused Node tests and pytest -q tests/test_hackathon_desk.py.
- [ ] Commit with Implements: HD-002.

### Task 2: Hackathon Desk shell and navigation

**Files:**
- Create: apps/tribute-dashboard/hackathon.html
- Create: apps/tribute-dashboard/hackathon.css
- Modify: apps/tribute-dashboard/index.html
- Modify: apps/tribute-dashboard/desk.html
- Modify: apps/tribute-dashboard/countdowns.html
- Modify: apps/tribute-dashboard/sitemap.xml
- Test: tests/test_hackathon_desk.py

**Interfaces:**
- Consumes: normalized feeds from Task 1.
- Produces: stable module IDs for overview, opportunities, challenges, hackathons, teammates, proposals, pipelines, guide, and accessibility.

- [ ] Write failing page-contract tests for landmarks, skip link, nav, module headings, sitemap entry, and shared CSS.
- [ ] Run pytest -q tests/test_hackathon_desk.py and verify expected failures.
- [ ] Implement responsive shell, semantic sections, and navigation links.
- [ ] Run focused tests and HTML/link checks.
- [ ] Commit with Implements: HD-003.

### Task 3: Data-backed opportunities, challenges, and hackathons

**Files:**
- Modify: apps/tribute-dashboard/hackathon.html
- Modify: apps/tribute-dashboard/hackathon.js
- Modify: apps/tribute-dashboard/hackathon.css
- Test: tests/hackathon-desk.test.cjs, tests/test_hackathon_desk.py

**Interfaces:**
- Consumes: normalized opportunity, coordinator, and countdown records.
- Produces: rendered public opportunity, challenge, and hackathon modules with source stamps and truthful empty/stale states.

- [ ] Write tests for ranked opportunity ordering, public gate state, expired/closed events, and null dates.
- [ ] Verify RED with focused Node/Python test commands.
- [ ] Implement renderers with escaped text and validated source links.
- [ ] Run focused tests and privacy scan.
- [ ] Commit with Implements: HD-002, HD-003.

### Task 4: Teammate onboarding and GitHub contribution flow

**Files:**
- Modify: apps/tribute-dashboard/hackathon.html
- Modify: apps/tribute-dashboard/hackathon.css
- Test: tests/test_hackathon_desk.py

**Interfaces:**
- Produces: onboarding checklist and GitHub navigation for profile, repository, issue, branch/PR, and review actions.

- [ ] Write failing tests for GitHub destination links, consent-based Discord guidance, and absence of embedded credentials or browser write methods.
- [ ] Verify RED.
- [ ] Implement onboarding and permission explanations; keep the supplied Discord identity out of public markup until teammate consent.
- [ ] Run focused tests and credential/privacy scans.
- [ ] Commit with Implements: HD-004.

### Task 5: Proposal and pipeline views

**Files:**
- Modify: apps/tribute-dashboard/hackathon.html
- Modify: apps/tribute-dashboard/hackathon.js
- Modify: apps/tribute-dashboard/hackathon.css
- Test: tests/hackathon-desk.test.cjs, tests/test_hackathon_desk.py

**Interfaces:**
- Consumes: proposal process links and desk/queue feed normalizers and the embedded dispatch-claims projection.
- Produces: read-only proposal workflow entry points and evidence-backed pipeline states.

- [ ] Write tests for issue form navigation, stale pipeline feeds, and source evidence links.
- [ ] Verify RED.
- [ ] Implement proposal and pipeline sections; link every stage to its source or GitHub workflow.
- [ ] Run focused tests and feed-privacy checks.
- [ ] Commit with Implements: HD-005, HD-006.

### Task 6: User Guide and Accessibility Guide

**Files:**
- Create: docs/teammates/HACKATHON-DESK-GUIDE.md
- Create: docs/teammates/ACCESSIBILITY.md
- Modify: apps/tribute-dashboard/hackathon.html
- Test: tests/test_hackathon_desk.py

**Interfaces:**
- Produces: onboarding, navigation, proposal, contribution, pipeline, permissions, accessibility, and troubleshooting documentation.

- [ ] Write failing tests for guide links and required sections.
- [ ] Verify the deployed guide URLs `https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/teammates/HACKATHON-DESK-GUIDE.md` and `https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/docs/teammates/ACCESSIBILITY.md` return successfully from the canonical deployed route `https://timerloggedout-spec.github.io/tribute/hackathon.html`; source-tree existence alone is insufficient.
- [ ] Verify RED.
- [ ] Write both guides and connect them from the page using the deployed raw-content URLs.
- [ ] Run documentation link, heading, and deployed-URL checks.
- [ ] Commit with Implements: HD-007, HD-008.

### Task 7: Accessibility and responsive verification

**Files:**
- Modify: apps/tribute-dashboard/hackathon.html
- Modify: apps/tribute-dashboard/hackathon.css
- Modify: apps/tribute-dashboard/hackathon.js
- Test: tests/test_hackathon_desk.py

- [ ] Add tests for skip link, semantic landmarks, labels, focus styles, reduced motion, live status announcements, and responsive breakpoints.
- [ ] Verify RED for each new assertion.
- [ ] Implement the minimum changes to pass.
- [ ] Run automated accessibility checks and manual keyboard/zoom/screen-reader review; record unverified manual checks.
- [ ] Commit with Implements: HD-008.

### Task 8: ICM route review and map update

**Files:**
- Modify after approval: docs/icm/CLAUDE.md
- Modify after approval: docs/icm/processes/CONTEXT.md
- Modify after approval: docs/icm/effects/CONTEXT.md
- Modify after approval: docs/icm/objects/operations/challenge-program.md
- Create after approval: docs/icm/processes/hackathon-desk.md

- [ ] Obtain human approval of docs/proposals/active/hackathon-desk/ICM-ROUTE.md.
- [ ] Write failing route/link checks.
- [ ] Apply the approved documentation-only map change.
- [ ] Run ICM cold-walk and link verification.
- [ ] Commit with Implements: HD-010.

### Task 9: Full verification and delivery

**Files:**
- All Hackathon Desk files and tests.

- [ ] Run node --test tests/hackathon-desk.test.cjs.
- [ ] Run pytest -q tests/test_hackathon_desk.py and the repository test suite.
- [ ] Update ITEMS.md with implementation evidence and final state, then commit that update before final-head validation.
- [ ] Run python3 scripts/ci/repo_gate.py and all focused tests/accessibility checks on the resulting head.
- [ ] Termux remains offline; do not invoke a Termux device/session or claim Termux runtime validation. The existing Ubuntu-hosted `termux smoke` PR workflow may appear in checks, but classify it as Linux CI only, never as a Termux runtime test.
- [ ] Verify required GitHub jobs on the same immutable final head SHA; record SHA-dependent run evidence in the PR or an artifact outside the commit.
- [ ] Verify deployed page, feed freshness, GitHub navigation, public projection, and guide routes against that same deployed commit.
