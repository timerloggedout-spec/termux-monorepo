# ITEMS — workflow-self-repair-hardening

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| SRH-001 | P0 | executing | Correct the action-first commit-subject validator for the generated backup-relay `export` subject and add a regression assertion. | Exact failing subject is accepted because `export` is a registered imperative; negative-first checks and scope/verb enforcement remain intact; focused tests and both repo gates pass. |
| SRH-002 | P0 | executing | Make Team MVT evaluation distinguish a skipped/incomplete matrix from an evaluator failure. | Skipped/cancelled matrix jobs emit an explicit non-promotable incomplete receipt; unexplained incomplete matrices still fail closed; execution failures remain visible; correctness stays UNKNOWN until independently evaluated. |
| SRH-003 | P0 | executing | Make Gemini after-peers defer safely when GitHub API quota is exhausted and bound peer-state comment reads. | PR repository/draft/SHA/peer-state validation remains mandatory; rate-limit exhaustion produces an explicit skip/defer with no model invocation; comment lookup is bounded; no retry storm or fallback. |

## Evidence

- #5363: run [43736180498](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43736180498) rejected generated subject `backup relay: export exp-20261115T162848Z-a2f472` because `export` was absent from the validator verb set.
- #5361: run [43724374863](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43724374863) skipped the lane job, downloaded zero lane artifacts, then failed with `expected 15 DOE cells, found 0 (lane result skipped)`.
- #5316: run [43735462393](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43735462393) failed PR validation with HTTP 403 and `x-ratelimit-remaining: 0`.

## Validation boundary

PRs #5476–#5478 are draft candidates. Their latest inspected commit combined-status endpoints returned no status checks; hosted CI and both repository dual gates have not been proven on those heads. The issue-specific self-repair loop still requires its independent evaluator and review evidence. No candidate is promoted by this proposal.
