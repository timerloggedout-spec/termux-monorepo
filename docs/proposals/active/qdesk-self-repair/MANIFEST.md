# MANIFEST — qdesk-self-repair

- **Proposal:** QDesk self-repair and SIE orchestration
- **Registry ID:** `qdesk-self-repair`
- **Status:** executing
- **Priority:** P0
- **Owner:** QUE / Optimizations & Assurance
- **Canonical proposal:** `PROPOSAL.md`
- **Lifecycle integration:** `../que-sie-pipeline-integration/PROPOSAL.md`
- **Tracking issue:** #5389
- **Implementation PR:** #5390
- **Primary workflow:** `.github/workflows/qdesk-self-repair.yml`
- **Primary implementation:** `scripts/que/self_repair.py`
- **Queue/watchdog sources:** `ops/challenge/dispatch-state-feed.json`, `ops/que/feeds/stall-gap-feed.json`
- **Evidence rule:** retain source issue/run/feed references, immutable revisions and independent verification receipts.

## Scope

Compose existing QDesk self-repair, QUE admission/claim, watchdog, Oracle Method, Delphi, DoE and ATES authorities into a bounded improvement lifecycle. Preserve each producer's canonical state and existing cadence.

## Acceptance gates

- Validate deterministic SIE stage receipts and transitions.
- Reconcile master workflow failures, feed freshness and dispatch escalation evidence.
- Preserve owner routing, idempotency and bounded intake.
- Require independent DoE/ATES verification before promotion.
- Retain failed, blocked and superseded outcomes in the learning record.
