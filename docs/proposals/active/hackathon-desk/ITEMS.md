# ITEMS — hackathon-desk

**Proposal:** hackathon-desk  
**Scope:** teammate collaboration portal, source-backed feeds, GitHub contribution flow, guide, and accessibility.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| HD-001 | Register the proposal and define the static GitHub-authenticated contribution architecture. | Registry, manifest, source, design, and plan agree on authority boundaries. | Implemented |
| HD-002 | Add tested feed adapters for QUE opportunities, challenge coordinator records, countdowns, desk traversals, dispatch state, and queue state. | Fixtures cover valid, empty, malformed, stale, and unavailable feeds; provenance and timestamps render. | Pending |
| HD-003 | Build responsive Hackathon Desk shell and Opportunities, Challenges, Hackathons, Proposals, and Pipeline views. | Navigation, cards, filters, status labels, source links, and mobile layouts work from canonical inputs. | Pending |
| HD-004 | Build teammate onboarding and GitHub contribution entry points. | GitHub identity is linked only by the teammate; repository permissions remain GitHub-enforced; Discord is optional and consent-based. | Pending |
| HD-005 | Integrate proposal creation and review navigation. | Existing proposal lifecycle, issue form, active registry, and PR process are linked without a second proposal store. | Pending |
| HD-006 | Integrate pipeline visibility from existing QUE, desk, and dispatch feeds. | Stages display evidence-backed states and feed freshness; the page creates no dispatches. | Pending |
| HD-007 | Publish the teammate User Guide and Accessibility Guide. | Guides cover onboarding, navigation, contribution workflow, roles, permissions, accessibility support, and troubleshooting. | Pending |
| HD-008 | Implement WCAG 2.2 AA-oriented accessibility behavior. | Keyboard-only, focus visibility, semantic landmarks, labels, contrast, zoom/reflow, reduced motion, and live status announcements are verified. | Pending |
| HD-009 | Add automated tests and repository validation. | Feed behavior, privacy exclusions, links, responsive/accessibility hooks, and proposal registry validate; both repository gates run on one SHA. | Pending |
| HD-010 | Add the ICM Hackathon Desk process route after the map-change proposal receives human approval. | Approved process card, ICM route, effects index, source citations, cold-walk, and ICM verification record. | Blocked — ICM human review |
| HD-011 | Verify deployment and end-to-end teammate flow. | Live page, feed freshness, GitHub destination auth, issue/PR entry points, and guide links verified against deployed commit. | Pending |

## Implementation constraints

- Preserve ops/que/feeds/opportunity-priority.json as the opportunity ranking source.
- Preserve ops/challenge/coordinator.json as the challenge coordinator source and single-writer boundary.
- Render metrics_internal and win_probability only on the existing Admin surface.
- Reuse the Tribute design system and dashboard deployment path.
- Keep browser behavior read-only; GitHub owns contribution writes and access decisions.
- Treat missing or stale feed data as an explicit evidence state.
- Use test-first implementation for each behavior change.
- Cite Implements: HD-<ITEM> in each implementation commit/PR.
