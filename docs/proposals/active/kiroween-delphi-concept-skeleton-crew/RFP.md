# Proposal — Kiroween 2026 — generated concept proposal (challenge packet D4) — Skeleton Crew — a CMDB / reconciliation viewer run by a minimal crew: a tiny set of spec-first Kiro agents (ingest, reconcile, report) that keep a fleet inventory honest against its sources. The challenge lane's hand-noted input (input, not decision). Seeded from the repo's CMDB design (PR #1655); the Kiro project itself is created new inside the submission window.

- **Proposal ID:** kiroween-delphi-concept-skeleton-crew
- **Kind:** competition
- **Surface:** Kiroween 2026 — Devpost (kiroween.devpost.com)
- **Deadline:** Dec 4, 2026, 2:00 PM PST
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-30T23:44:05Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate the concept proposal for the fleet's Kiroween 2026 entry (challenge log packet D4): choose and scope a spec-first project built with Kiro under one of the four official themes, sized for a build window that starts after Nov 8, 2026 and ends at the Dec 4, 2026, 2:00 PM PST submission deadline. The project must be newly created inside the submission period (Oct 30, 9:00 AM PT – Dec 4) — nothing pre-built is eligible. The challenge-entries lane's hand-noted input (an input, not the decision): a CMDB/reconciliation viewer seeded from the repo's CMDB design (PR #1655), under Skeleton Crew or Frankenstein. Registration is being completed via the Devpost + Kiro ID creation lane (fleet Google identity); the entrant monikers are entrant{entrantDevpost}[platform:devpost] and entrant{entrantKiro}[platform:kiro].

## 2. Basis in evidence

- Data model and conflict matrix derive from the repo's CMDB design (PR #1655); specs written first in Kiro, agents generated from the specs. (evidence: `d4:concept-inputs`)
- Smallest viable scope for the post-Nov-8 build window: read-only inventory views + reconciliation report, no write actions. (evidence: `d4:sequencing`)
- Category shaping (official rules, stamped 2026-10-30): Skeleton Crew = foundation + TWO distinct applications, repo containing 2 separate app folders — the CMDB foundation carries the ingest/reconcile crew; the conflict viewer and the stamped-report app are the two applications. (evidence: `kiroween:category-skeleton-crew`)

## 3. Plan

**Steps:**

1. Create the Kiro project inside the submission window (on/after Fri Oct 30, 2026, 9:00 AM PT) and capture its creation timestamp into packet D4 as eligibility evidence; build work itself starts after Nov 8 per owner sequencing.
2. Author the spec pack in Kiro: inventory schema, source-adapter specs, reconciliation rules (from the CMDB design doc on master).
3. Generate the ingest and reconcile agents from the specs; keep every agent read-only.
4. Build the viewer: inventory list, conflict matrix, evidence-stamp detail view.
5. Seed the fixture inventory; run reconciliation; capture the stamped conflict report as implementation evidence (with run receipts).
6. Run the variant test_suites; every suite result carries its run receipt (command, exit code, output sha256, code paths).
7. Record the demo and file the Devpost submission by Dec 4, 2026, 2:00 PM PST.

**Risks:**

- Kiro spec-format learning curve inside a short post-Nov-8 window.
- Reconciliation scope creep (sources x conflict types) beyond what the window fits.
- Devpost deliverable requirements are unknown until the Oct 30 rules publish; the plan's demo/submission steps may need reshaping at lock.

**Alternatives considered:**

- Shrink to a single-source read-only inventory viewer if reconciliation slips; the stamped report remains the demo centerpiece.
- If spec-first generation stalls, re-shell the same data model inside the frankenstein composition.

## Provenance

Generated from 1 evidence set(s), 13 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
