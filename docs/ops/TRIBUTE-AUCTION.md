# Tribute claim auction: free endpoints ante + bid to take a claim

Code: `scripts/ci/tribute_auction.py` · tests: `tests/test_tribute_auction.py` ·
workflows: `tribute-execute.yml` (live), `tribute-auction.yml` (tests, shadow, Delphi),
`tribute-status-refresh.yml` (settlement).

## Why

The lane claimed foreign issues and opened stake-only PRs it could not back with
a patch: in the 90 days to 2026-11-12, 14 of the 20 merges were stake files
(weight 0), 4 were self-merges, 2 were real, and 99 PRs were closed unmerged.
The auction makes every claim a priced bet that a specific free endpoint can
deliver a real merge, and makes losing bets cost that endpoint.

## Round (one issue)

1. **Eligibility.** Only issues that pass System 1 `preflight_candidate` (no
   assignee or prior human claim, no human-only/language skill, no Wave/bounty
   program assignment, no spam flag, open). Program labels (Wave, bounty, Drips,
   OnlyDust) and repos with a hostile/spam outcome (repo factor 0) are refused.
2. **Pool.** Text endpoints from `data/g4f-working/working-endpoints.json` (the
   probed free-inference universe), deduped, image/audio providers removed,
   latency <= 60 s. Sorted by id, so every round is reproducible.
3. **Ante.** `ante = 10 x (1 + difficulty)` credits from the endpoint's own
   ledger (budget 100, refill 10/day, capped). An endpoint that cannot cover the
   ante has no seat.
4. **Bid.** `p(real merge) = issue_prior x capability x language_fit x repo_factor x p_complete`,
   then blended with the endpoint's own record (Beta-style, 4 pseudo-rounds of prior):
   - issue prior: base 0.12, +0.10 easy/docs/good-first-issue labels, +0.08 x body clarity, -0.05 busy threads;
   - capability: model family and size, code affinity, provider factor (code agents above search wrappers), outdated models x0.6;
   - language fit: mainstream stacks ~1.0-1.1, hard stacks (Rust, Swift, Solidity, Cairo, ...) 0.4-1.0 by code affinity;
   - repo factor: Delphi / System 1 outcome weights and the merge census for that repo (`1 + 0.5 x mean weight`, 0.3-1.3; stake merges weigh 0 so they never help);
   - p_complete: `0.6 + 0.4 x quota remaining` (free-tier limits);
   - `EV = p x 40 - (1 - p) x ante - latency/60`.
5. **Winner.** Highest EV above the reserve (0); ties by lower latency, then id.
   No bid above reserve -> `below_reserve`, no claim.
6. **Real patch first.** The winner must bring a patch that passes
   `tribute_system1.preflight_pr` (no stake/placeholder files) before any claim
   comment is posted. In `tribute-execute.yml` the claim job runs only with a
   winner **and** a supplied patch; otherwise nothing is posted.

## Settlement (deterministic replay)

Receipts are append-only on branch `tribute-auction/receipts` (`receipts.jsonl`:
`kind=auction` from the execute budget job, `kind=claim` after a claim posts).
Every status refresh replays them in time order against the outcome census
(`docs/ops/generated/tribute-outcomes.json`) and writes
`docs/ops/generated/tribute-auction-ledger.json`:

| Outcome of the claimed issue's PR | Ante | Delphi (`surface: tribute-auction`) |
|---|---|---|
| real merge | returned + reward 40 | +1.0 |
| stake-only merge / closed unmerged / no PR 14 days after the claim | forfeited | -0.8 |
| won but no patch, so no claim posted | returned | none |
| PR still open | escrow | none |

New settlements since the last committed ledger go to Delphi through
`./.github/workflows/delphi-signal.yml` (`event: tribute-outcome`, key
`auction:<endpoint>:<issue>`), from `tribute-auction.yml`.

## Where it runs

- `tribute-execute.yml` budget job: live auction on the selected issue (live
  System 1 preflight, repo language read), receipt appended; claim job gated on
  winner + patch.
- `tribute-auction.yml`: unit tests on PR/push; after each status refresh a
  read-only shadow auction over the top 3 scouted issues (step summary +
  artifact, nothing posted); Delphi emission of new settlements.
- `tribute-status-refresh.yml`: settlement + `tribute_auction` summary in `status.json`.

Tunables (env): `TRIBUTE_AUCTION_BUDGET`, `_REFILL`, `_ANTE`, `_REWARD`, `_RESERVE`.
No LLM calls and no network in the module itself (the CLI's `--enrich` and
`--live-preflight` only read the GitHub API).
