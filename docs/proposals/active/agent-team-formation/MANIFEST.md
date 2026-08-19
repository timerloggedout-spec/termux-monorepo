---
id: agent-team-formation
title: "Role-aware agent teams, game-player fleet, scoring, and controlled research"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: awaiting_review
  - id: Manus AI
    role: author
    status: posted
related_issues: [129, 236, 243]
related_prs: [131]
related_branches: [docs/agent-team-formation-draft]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — agent-team-formation

## Summary

This draft establishes an initial **role-aware and additive operating model** for the Termux multi-agent roster. It preserves the repository's existing MoneyBall concept while separating teams by verifiable work type rather than assigning every candidate one generic ELO value. The draft now includes research, development, delivery reliability, **Game Player Machines & Genre Teams**, game QA/accessibility, mobile analysis and forensics, security research/red team testing of project systems, wallet and economic-systems research, and orchestration/quality control. The registry model permits new teams, lanes, roles, tools, machine profiles, games, targets, and scorecards to be appended with versioned evidence.

The proposal is deliberately **not accepted**. The repository requires a recorded review before an accepted proposal may drive execution, and the configured integration branch, `master-staging`, is not currently present on the remote. This change is therefore a documentation-only draft based on the available `master` branch, not an integration-ready implementation.

## Evidence and scope notes

The existing lane SSOT assigns MoneyBall and agent mail to the multi-agent orchestration lane and names issue #129 and PR #131 as the corresponding work stream. However, live metadata captured on 2026-08-19 reports PR #131 open and dirty, 94 commits ahead of its recorded base, with failed peer-review and GitLab checks. Issue #243 supplies the `Roster:Teams:Games:Players` seed and an expandable game list. Issue #236 remains the mobile-analysis/forensics seed. The evidence package maps all of these labels into controlled, reproducible project-team work and preserves them as research signals. See [source.md](./source.md) and [the recon index](../../../recon/team-formation/README.md).

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| Manus AI | Author | posted | 2026-08-18 | Prepared the initial draft and item list; expanded the evidence package on 2026-08-19. |
| timerloggedout-spec | Operator-authorizer | awaiting_review | — | Confirm role names, scope, and whether to promote the proposal. |
| Security reviewer | Independent reviewer | awaiting_assignment | — | Required before security/red-team automation is accepted. |

## Review log

### 2026-08-18 — Manus AI

- **Disposition:** draft posted for review.
- **Notes:** The team model uses role-specific scorecards plus a shared reliability floor. Scores may inform task routing but do not replace task records, evidence, review pairing, or Operator policy.

### 2026-08-19 — Manus AI

- **Disposition:** recon package added to the existing draft.
- **Notes:** Added a label taxonomy, game-player fleet/genre-team contract, live MoneyBall reconciliation record, and Swarms/wallet research architecture. The package records #243 as the game-player seed, retains existing research labels, and treats future real-wallet work as a distinct staged architecture decision.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml` as a draft.
- [x] Added scoped work items in `ITEMS.md`.
- [x] Recorded the evidence and status discrepancy in `source.md`.
- [x] Captured the #243 game-player label, specialist label map, PR #131 state, and Swarms/wallet reference evidence.
- [x] Added the additive registry, game-player fleet, and wallet research backlog items (ATF-11 through ATF-13).
- [ ] Obtain an Operator review and an independent security review.
- [ ] Promote to `accepted` before implementing score, roster, or workflow changes.
- [ ] Reconcile the `master-staging` branch requirement before opening an integration PR.
- [ ] Cite `Implements: ATF-<ID>` on future implementation commits and PRs.
- [ ] Run `repo_gate.py` and `termux_smoke.py` before any merge.

## Links

- [Team charter](./TEAM_CHARTER.md)
- [Initial scoped items](./ITEMS.md)
- [Evidence log](./source.md)
- [Open questions](./DEBATE.md)
- [Team-formation reconnaissance index](../../../recon/team-formation/README.md)
- [Game Player Fleet and Genre Teams](../../../recon/team-formation/GAME_PLAYER_FLEET.md)
- [Initial Target Register Template](../../../recon/team-formation/TARGET_REGISTER.md)
- [Swarms Reference and Wallet Research](../../../recon/team-formation/SWARMS_WALLET_RESEARCH.md)
- [Repository proposal process](../../PROCESS.md)
- [Repository consensus rules](../../../CONSENSUS.md)
