# Hackathon Desk — Design

**Date:** 2026-11-24  
**Proposal:** hackathon-desk  
**Status:** Operator-authorized scope; implementation plan pending review.

## Intent

Build one accessible teammate-facing page inside the existing Tribute dashboard so a hackathon teammate can discover current opportunities, understand challenge and event state, onboard, submit proposals, contribute through GitHub, and inspect evidence-backed pipeline progress. The page consolidates navigation and context while existing repository systems retain authority.

## Goals

- Present ranked opportunities from the QUE priority feed with provenance and freshness.
- Present challenge events, deadlines, gates, and submission state from canonical challenge records and countdown projection.
- Provide hackathon discovery and status without inventing availability or deadlines.
- Guide teammates through GitHub identity, permissions, branches, commits, pull requests, and review.
- Link proposal creation and review to the existing proposal lifecycle.
- Project existing queue, desk traversal, and dispatch evidence.
- Provide a complete User Guide and Accessibility Guide.
- Target WCAG 2.2 AA and verify keyboard, focus, semantics, contrast, reflow, reduced motion, and status updates.

## Non-goals

- Custom identity provider, OAuth backend, token store, or browser-side write API.
- New challenge, opportunity, proposal, pipeline, or scheduler database.
- Automated teammate permission grants.
- Public rendering of admin metrics or internal challenge estimates.
- Publishing Discord contact information without teammate consent.
- Replacing the existing Admin Desk, Contribution Desk, Challenge Coordinator, QUE, or proposal systems.

## Architecture

The Hackathon Desk is a static page under apps/tribute-dashboard/, using the shared dashboard.css design system. A small browser module validates and normalizes public feeds, renders modules, and exposes source/freshness states. The page consumes the QUE priority feed from `https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/que/feeds/opportunity-priority.json` and a generated `./data/challenge-public-feed.json` projection. It consumes existing dashboard mirror feeds for countdown, desk, QUE queue, and dispatch projections through relative `./data/` URLs.

The browser MUST NOT request or receive `ops/challenge/coordinator.json`. A deterministic build-time generator produces `challenge-public-feed/v1` from an explicit allowlist of public event, status, date, gate, and source fields. The generator recursively excludes `metrics_internal` and `win_probability` at every nesting level; tests scan the entire serialized artifact and fail on either key. The generated projection ships inside the dashboard deployment tree. Missing, invalid, or stale projections render an explicit unavailable state.

All browser actions remain navigational. Sign-in, proposal submission, issue creation, branch/PR contribution, and review actions open GitHub pages; GitHub authenticates the teammate and enforces repository permissions. The portal does not create a separate login session or retain credentials.

## Approaches

1. **Static Tribute projection with GitHub-owned contribution actions — selected.** Reuses the current static dashboard, feeds, navigation, and GitHub Issues/PRs. It has the smallest trust boundary and no new secrets or service. Authentication occurs on GitHub when a teammate acts. A profile URL selected by the teammate is self-asserted and is not proof of account ownership.
2. **Custom OAuth-backed portal.** Could provide an in-page signed-in profile and API actions, but requires a backend, OAuth application, secret custody, session security, and a new permission surface. Those resources and approval paths are outside the current brief.
3. **Standalone public information page with manual links.** Lowest effort, but omits live feed integration and pipeline evidence and duplicates existing navigation without delivering the requested Desk.

## User experience

Primary navigation: Overview, Opportunities, Challenges, Hackathons, Teammates, Proposals, Pipelines, Guide, Accessibility.

- Overview: current summary, feed freshness, next actions, and clear source links.
- Opportunities: ranked QUE records, state, priority, public gate status, source, and freshness.
- Challenges: coordinator event records, verified gates, status, submission evidence, and deadline references.
- Hackathons: event timeline and countdowns derived from recorded instants; expired/closed items remain visible with truthful state.
- Teammates: onboarding checklist, role expectations, a clearly labelled self-selected GitHub profile link (identity ownership remains unverified until a separate approved verification mechanism exists), contribution-history links, and optional contact guidance.
- Proposals: proposal process, active registry link, proposal issue form, and review expectations.
- Pipelines: read-only stage view from existing queue, desk, and dispatch feeds; each state links to evidence.
- Guide and Accessibility: standalone documentation pages.

## Data and trust rules

- QUE priority feed is the ranked opportunity source; render generated_at, freshness horizon, and stale status.
- Challenge coordinator JSON is the challenge event/participant/gate source of truth.
- Countdown feed carries instants; derive time remaining in the browser and label absent instants as “not recorded.”
- Desk feed supplies traversal evidence only; deprecated priority-timebox data is excluded from opportunity ranking.
- Treat missing, malformed, or stale sources as visible evidence states.
- Exclude metrics_internal, win_probability, and the Admin-only metrics feed from public code, feeds, and rendered content.
- Preserve source URLs and last-updated timestamps beside data-driven claims.
- Escape untrusted strings before HTML insertion; validate outbound links and use safe target attributes.

## Teammate identity and permissions

The supplied Discord username is a contact reference only. The teammate links their GitHub account by choosing their GitHub profile and uses GitHub sign-in for repository actions. Repository membership and write permissions remain under GitHub administration. The portal explains read, triage, and write boundaries and routes access requests to the repository owner; it never grants access itself.

## Accessibility and responsive behavior

Target WCAG 2.2 AA. Use semantic landmarks, a skip link, heading hierarchy, accessible names, keyboard-operable controls, visible focus, sufficient contrast, text alternatives for visual status, responsive reflow at 320 CSS pixels, zoom support, reduced-motion behavior, and polite live announcements for feed status. Tables and cards remain usable without color or pointer interaction. Document automated and manual checks.

## Deployment and verification

Integrate with the existing Tribute dashboard deployment and sitemap. Run focused feed/renderer tests, HTML/link checks, privacy scan, accessibility checks, python3 scripts/ci/repo_gate.py, and python3 scripts/ci/termux_smoke.py. Re-fetch the same PR head SHA and named CI jobs before promotion. Verify the live page and feed freshness after deployment.

## Open implementation choices

- Keep feed normalization in a focused hackathon.js module for testability.
- Use public raw GitHub content URLs pinned to master for canonical opportunity/challenge sources, plus existing dashboard data mirrors for dashboard-specific feeds.
- Keep teammate identity ephemeral in the UI until the teammate explicitly chooses a GitHub profile link; do not create a public roster database in this phase.

## Approval

Operator selected access=github and scope=full and explicitly authorized proposal registration, ICM routing, and implementation on 2026-11-24. The exact implementation plan is presented separately for review before product-code execution.
