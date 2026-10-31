# Research and paper-wallet proposal tracking

**Status: proposals recorded; runtime gaps remain open.** The owner requested Docs, issues, native subissues, Project and milestone tracking. This index joins the existing THUB-017 and MSM-005 lanes; it does not introduce another market, quota ledger, scoring system or scheduler.

## What exists versus what is proposed

[PR #1470](https://github.com/timerloggedout-spec/termux-monorepo/pull/1470) is open, unmerged and undeployed at [`d2778bcc`](https://github.com/timerloggedout-spec/termux-monorepo/commit/d2778bcc25966533ccd2f5bc1991aab672fb9cbe). Its opt-in Python/Rust Swarms adapters use the existing model hub. AdvancedResearch is pinned, not integrated or run; `research-plan.py` only emits an offline plan. Shared quota/reset/cooldown consumption, atomic quota reservation and correlated TermuxTelemetryLogger/3L0 telemetry are not proven end to end.

MSM-012 in the **model-selection-market packet** is only a CSV projection of existing MSM-005 stakes/cards/offers. The balance/reservation/settlement engine is absent. MSM-005 remains the wagering/bidding lane: its existing “done” status applies to the cards/bets/graph stub, not to the proposed accounting extension. The current MarketGraph is in memory; durable event persistence is part of the extension, not an existing accounting capability. MSM item IDs are packet-qualified because other packets also contain MSM-prefixed IDs.

## Proposals and owning issues

- [Research integration](RESEARCH-INTEGRATION.md): [research / #1520](https://github.com/timerloggedout-spec/termux-monorepo/issues/1520), continuing THUB-017.
- [Paper-wallet accounting](../model-selection-market/PAPER-WALLET-ACCOUNTING.md): [wallet / #1521](https://github.com/timerloggedout-spec/termux-monorepo/issues/1521), extending MSM-005 and preserving MSM-012 projection scope.

Both are native subissues of [existing team/research intent #129](https://github.com/timerloggedout-spec/termux-monorepo/issues/129). Each has four native subissues, not just checklist text.

## Work, dependencies and milestones

| Work | Depends on | Evidence required | Milestone |
|---|---|---|---|
| [THUB-017.A / #1522](https://github.com/timerloggedout-spec/termux-monorepo/issues/1522) | Proposal contract review; explicit #1470 disposition | Pinned bounded Research adapter; real runtime with fake search/inference | [Research + paper wallets: proposal and contract review](https://github.com/timerloggedout-spec/termux-monorepo/milestone/3) |
| [THUB-017.B / #1523](https://github.com/timerloggedout-spec/termux-monorepo/issues/1523) | THUB-017.A contract | Shared quota/reset/cooldown; atomic reserve and reconcile; no deny-path inference | [Research + paper wallets: bounded implementation](https://github.com/timerloggedout-spec/termux-monorepo/milestone/4) |
| [THUB-017.C / #1524](https://github.com/timerloggedout-spec/termux-monorepo/issues/1524) | THUB-017.A/B contracts | Correlated redacted hub/Research/TermuxTelemetryLogger/3L0 evidence | [Research + paper wallets: bounded implementation](https://github.com/timerloggedout-spec/termux-monorepo/milestone/4) |
| [THUB-017.D / #1525](https://github.com/timerloggedout-spec/termux-monorepo/issues/1525) | THUB-017.A/B/C | End-to-end success/failure/deny/cancel/unknown and exact-SHA remote receipts | [Research + paper wallets: end-to-end evidence](https://github.com/timerloggedout-spec/termux-monorepo/milestone/5) |
| [MSM-005.A / #1526](https://github.com/timerloggedout-spec/termux-monorepo/issues/1526) | MSM-005 existing event/market model; proposal review | Paper-point unit, issuance, account/event and settlement contracts | [Research + paper wallets: proposal and contract review](https://github.com/timerloggedout-spec/termux-monorepo/milestone/3) |
| [MSM-005.B / #1527](https://github.com/timerloggedout-spec/termux-monorepo/issues/1527) | MSM-005.A | Balance/reserve/settle/release, atomicity, idempotency and recovery | [Research + paper wallets: bounded implementation](https://github.com/timerloggedout-spec/termux-monorepo/milestone/4) |
| [MSM-005.C / #1528](https://github.com/timerloggedout-spec/termux-monorepo/issues/1528) | MSM-005.A/B; MSM-012 projection baseline | Rebuildable versioned CSV views, no import-based minting | [Research + paper wallets: bounded implementation](https://github.com/timerloggedout-spec/termux-monorepo/milestone/4) |
| [MSM-005.D / #1529](https://github.com/timerloggedout-spec/termux-monorepo/issues/1529) | MSM-005.A/B/C | Conservation, overspend, replay, concurrency, restart and CSV proofs | [Research + paper wallets: end-to-end evidence](https://github.com/timerloggedout-spec/termux-monorepo/milestone/5) |

The two parent issues are assigned to the contract-review milestone; implementation and proof stay open until their own evidence is complete. Milestones define exit criteria, not dates or service commitments. No due dates were invented.

## Project tracking

Reuse [existing Project #1](https://github.com/users/timerloggedout-spec/projects/1); do not create a competing board. Project status is a derived view, with new implementation work starting at **Todo**, not Done. The repository’s existing issue-to-Project automation performs additions: direct connector Project writes are denied. Native membership and **Todo** status were verified for all ten issues (#1520–#1529) through Project #1 item records after their issue events completed; this is direct membership evidence, not an inference from green automation runs. Milestone, parent-issue and subissue-progress fields derive from the issue hierarchy. Priority is P1 in each issue body; no claim is made that the Project Priority custom field was written.

## Completion and safety

Recording a proposal does not accept its runtime design or mark any implementation complete. Keep exact source revision, candidate SHA, test fixture, workflow revision, artifact hash and outcome together. Local Linux gates are not Android evidence. Remote execution via Termux and Actions/WorkSpaces is already documented in PR #1470; it is not a missing service to rebuild.

Paper points are nonredeemable internal accounting units, not provider quota or money. No blockchain/testnet wallet, RPC, signer, payment, live provider request, paid fallback, new schedule, routing-weight promotion, PR merge or deployment is part of this documentation change. Runtime changes require reviewed contracts and attributable evidence; existing observe-cycle and ledger-decision policy remains unchanged.

## Baseline evidence

- [Swarms operating-status audit at the PR revision](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/integrations/swarms/OPERATING-STATUS.md).
- [Research source registration and offline planner limits](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/docs/research/SWARMS-RESEARCH-WALLETS.md).
- [MSM-005 market stub](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/scripts/model_selection_market/market.py) and [MSM-012 CSV projection](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/scripts/model_selection_market/paper_wallet.py).
- [Existing remote execution instructions](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/integrations/swarms/REMOTE.md).
