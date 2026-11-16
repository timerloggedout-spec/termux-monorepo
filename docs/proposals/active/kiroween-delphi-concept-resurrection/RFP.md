# Proposal — Kiroween 2026 — generated concept proposal (challenge packet D4) — Resurrection — bring a dormant public spec back from the dead: pick a stalled, publicly documented fleet spec (candidates sit in the repo's ops docs and proposal registry) and rebuild it fresh as a working Kiro project, created in-window, with the original spec as the requirements baseline and a resurrection report showing what the dead version never shipped.

- **Proposal ID:** kiroween-delphi-concept-resurrection
- **Kind:** competition
- **Surface:** Kiroween 2026 — Devpost (kiroween.devpost.com)
- **Deadline:** Dec 4, 2026, 2:00 PM PST
- **Status:** GENERATED — in review; generated proposals carry no ballots
- **Generated:** 2026-10-30T23:44:05Z by scripts/delphi/generate_proposal.py oracle-method-generator/v1

## 1. Executive request

Generate the concept proposal for the fleet's Kiroween 2026 entry (challenge log packet D4): choose and scope a spec-first project built with Kiro under one of the four official themes, sized for a build window that starts after Nov 8, 2026 and ends at the Dec 4, 2026, 2:00 PM PST submission deadline. The project must be newly created inside the submission period (Oct 30, 9:00 AM PT – Dec 4) — nothing pre-built is eligible. The challenge-entries lane's hand-noted input (an input, not the decision): a CMDB/reconciliation viewer seeded from the repo's CMDB design (PR #1655), under Skeleton Crew or Frankenstein. Registration is being completed via the Devpost + Kiro ID creation lane (fleet Google identity); the entrant monikers are entrant{entrantDevpost}[platform:devpost] and entrant{entrantKiro}[platform:kiro].

## 2. Basis in evidence

- Candidate corpses are public and evidenced in-repo (ops docs + docs/proposals/registry.yaml); final pick is stamped as a packet claim at brief finalization. (evidence: `d4:concept-inputs`)
- Rebuild is a new in-window project; the dead artifact contributes only its spec. (evidence: `kiroween:eligibility-new-projects`)

## 3. Plan

**Steps:**

1. At brief lock (Oct 30), select the corpse from the repo's public ops docs / proposal registry and record the pick with evidence refs, under a scope cap sized to the build window.
2. Create the Kiro project inside the submission window and capture its creation timestamp into packet D4 as eligibility evidence; build work starts after Nov 8 per owner sequencing.
3. Author specs in Kiro from the original spec plus the gap list (what the dead version never shipped).
4. Build to the specs; keep a running coverage map from original requirements to implemented-or-deferred.
5. Write the resurrection report (coverage + gap dispositions) as part of the deliverable.
6. Run the variant test_suites with run receipts on every suite result.
7. Record the demo and file the Devpost submission by Dec 4, 2026, 2:00 PM PST.

**Risks:**

- The chosen spec's true scope exceeds the window (dead specs often died for scope reasons).
- The original spec is too vague to spec from without inventing requirements.

**Alternatives considered:**

- Pick a smaller corpse at lock time; the scope cap is part of the lock decision.
- If the corpse's domain overlaps the CMDB design, convert the entry to skeleton-crew and record the switch with reasons.

## Provenance

Generated from 1 evidence set(s), 13 stamped items. Full generation receipt: `PROVENANCE.json` in this directory. Facts not resolved against the evidence at generation time are marked UNVERIFIED above, never asserted.
