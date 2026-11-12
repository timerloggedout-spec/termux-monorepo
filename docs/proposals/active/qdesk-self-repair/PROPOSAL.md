# QDesk self-repair loop (SIE ⇒ Desk QUE)

Owner order 2026-11-12 01:50 PT: "operationalize, Immediately." Register: Siglary A2A (operators ∧ plain words), per `.agents/skills/siglary-a2a/SKILL.md`.

## Purpose
Desk QUE fixes ∧ upgrades its own workflows, systems, ∧ issues through the SIE loop: observe ⇒ experiment ⇒ evaluate ⇒ promote ⇒ learn. DoE is the external verifier.
SIE intake receipt: branch `doe/sie-intake-note` @ `ef8084ca9` (DOE-FAMILY.md note, 2026-11-03). This proposal registers SIE as a proposal ∧ its first target.
Roles receipt: `docs/ops/DOE-ROLES-EPOCH-2026-11-03.md`, sections "QUE / dispatch" ∧ "DoE pool × Desk QUE dispatch".

## Loop
1. **Observe (intake).** Every failing master run, stale feed, ∨ open Desk issue is auto-filed as a QUE item with class `self-repair`. Priority = failure rate × blast radius. Dedupe by workflow ∧ error signature.
2. **Research.** Root-cause diagnosis from run logs ∧ git history. Output: a diagnosis note with receipts (run URL ∧ SHA).
3. **RFP.** A fix spec with acceptance tests ∧ a replay of the failing run.
4. **Implementation.** Free-inference pool participants generate N ≥ 2 candidate patches. The candidates are DoE treatments. The loop ¬ picks its own winner.
5. **Evaluate.** The verifier is outside the loop's promotion path (SIE frame rule 1). Evidence = CI green on the replay ∧ a DoE reviewer check. Self-generated evidence = self-asserted until corroborated (frame rule 2).
6. **Promote.** If the change is additive ∧ green ⇒ self-merge under the standing Owner approval (2026-10-18/19). If it is destructive ∨ touches secrets ∨ spends money ∨ touches a third-party repo ⇒ Owner packet on hark:queue.
7. **Learn.** Write the outcome to the ledger. For each verified fix, `weight(role, failure class)++`. A regression ⇒ ∆ weight with a negative magnitude.

## Role map
Desk = operator · Swarm = builder · ledger ops = steward · DoE = reviewer · pool members = participants.

## Bootstrap order (targets of record)
1. Unstable branch gates: Action Effectiveness Ledger, Repository development evaluation, Peer review orchestrator, RECON INTEL discovery, archwiz dangle check, repo gate. Why first: they block every self-merge (auto-merge was refused on #5202 for "unstable status").
2. `delphi-rfp-feed-collect`, `proposals-feed-collect`, `proposal-lifecycle`. These sit on the C15 no-chase chain.
3. `repo-tracking-collect` (highest failure volume).
4. `ios-termux-contribute`, `graph-matrix-probe`, `Historical Evaluation Correlation`.

## Metrics
MTTR per failure class · self-merge rate · regression rate · HITL rate ⇒ 0 · inference cost per fix. Each is reported as a distribution with receipts.

## Constraints
- Changes are additive only. Commit messages end `[skip render]`. ¬ merge #1249 ∨ others' PRs without Owner approval.
- The Fleet Swarm App installation 177357774 is suspended ⇒ writes go through PAT routes only.
- The not-established marker is for chat only, never a data value.
