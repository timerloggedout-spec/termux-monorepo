# Hackathon Desk — proposed ICM route

**State:** PROPOSED · HUMAN MAP REVIEW REQUIRED  
**Domain object:** docs/icm/objects/operations/challenge-program.md  
**Change process:** docs/icm/processes/change-and-validate.md

## Proposed process card

Create docs/icm/processes/hackathon-desk.md as a process card for the teammate-facing collaboration surface.

The card routes:
- UI and feed changes to apps/tribute-dashboard/hackathon.html, hackathon.js, and canonical feed contracts.
- Opportunity state to QUE and ops/que/feeds/opportunity-priority.json.
- Challenge events and gates to the challenge coordinator and schema.
- Contribution identity and writes to GitHub Issues and Pull Requests.
- Proposal lifecycle to docs/proposals/PROCESS.md.
- Accessibility verification to the Hackathon Desk guides and test suite.

## Proposed map edits

1. Add a “build or operate the Hackathon Desk” route in docs/icm/CLAUDE.md.
2. Add the new process card to docs/icm/processes/CONTEXT.md.
3. Add a change-impact row to docs/icm/effects/CONTEXT.md.
4. Add the process card under “See” in docs/icm/objects/operations/challenge-program.md.

## Explicit exclusions

- Keep ICM maintenance documentation-only.
- Keep source ownership with existing challenge, QUE, proposal, and dashboard contracts.
- Preserve the static page and GitHub permission boundary.
- Keep metrics_internal and win_probability out of every public surface.
- Preserve the ICM 02_design human approval checkpoint before editing the map.

## Human decision

Operator review: PENDING  
Decision: APPROVE / REVISE / REJECT  
Reviewer notes: PENDING
