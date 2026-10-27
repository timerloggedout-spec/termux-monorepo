# Tribute Lane Efficacy Audit — 2026-10-27

Scope: what the Help-Wanted / Tribute lane has actually achieved upstream —
claims, stake PRs, real PRs, conversions, and maintainer perception — audited
firsthand against the live upstream records, and reconciled with the
concurrent fixes PR #1677 and PR #1694. Trigger: owner question on
interledger/interledger.org-v5 #804 (is the maintainer poking fun at the
lane?). Method: the lane's own audit ledger
(`docs/ops/generated/help-wanted-tribute-audit.json`, snapshot
2026-10-25T05:09Z, 114 unique upstream PRs) as the universe, with every
reachable PR re-read live from the GitHub API on 2026-10-27. GitHub author
search undercounts this account and was not used as the universe.

## Headline numbers

Universe: **114 upstream PR attempts across 111 repos** (ledger, 2026-10-25).
Live re-verification 2026-10-27: 107 reachable, 7 unreachable (6 × 404 —
repo deleted/private/renamed; 1 redirect) and counted as evidence gaps.

| Measure | Count | Note |
|---|---|---|
| PR shape: stake-only | 106 / 114 (93%) | ledger `stake_only` flag |
| Stake marker file present | 108 / 114 | `.github/help-wanted-lane-stake.md` |
| Solution proof present | **0 / 114** | ledger `solution_proof_present` |
| Merged (live, of 107 reachable) | 16 (15.0%) | median time-to-merge 0 days |
| Closed unmerged (live) | 63 (58.9%) | median 1 day open before closure |
| Still open (live) | 28 (26.2%) | 27 stake-only + 1 implementation-unproven; median age 23.5 days, max 46 |
| **Independently verified realized effects** | **0** | `help-wanted-realization-evidence.jsonl` holds no verified records |

**Merged is not realized.** The merged set includes stake-shaped PRs; a
merged stake file is not a fix. The defensible efficacy statement today is:
17 merges per the ledger (16 confirmed live), **zero** independently
verified realized effects, and a realization registry whose strict
verification rules have never once been satisfied. Any aggregate like
"105 successful contributions" is prohibited by the lane's own evidence
rules (see also PR #1694's wording).

## Named examples (firsthand)

### 1. EF-CHAIN/SendAm #492 and #607 — non-conversions (owner-ruled 2026-10-26)
- #492 (for issue #465): stake PR, 1 file +8/−0, opened 2026-09-24. The
  target issue was closed by others on 2026-10-03 (PR #697 QUICKSTART fix).
  Our PR sat 32 days and was closed unmerged by the maintainer
  2026-10-26T09:48Z.
- #607 (for issue #538): same shape, opened 2026-09-26. Issue closed by
  others 2026-10-15 (PR #637). Closed unmerged 2026-10-26T09:48Z — the same
  minute as #492: a maintainer batch cleanup of two dead stakes.
- Classification: **non-conversion** (opened as tribute, closed unmerged,
  completed by others). Never a completion.

### 2. ROCm/rocm-libraries #13152 — open liability, maintainer question unanswered
Correction to the fleet's standing record: this PR is **still open** (it was
previously described as closed/retired). Stake PR for issue #10586, opened
2026-10-06, 1 file. Thread, firsthand:
- The lane posted one `reengage` and five `stale_nudge` follow-ups
  (2026-10-06 → 2026-10-21, ~72h cadence), each quoting a CI bot
  (`therock-pr-bot[bot]`), not a human.
- 2026-10-22, maintainer **dysu-amd**: *"Hi @timerloggedout-spec, what is
  the purpose of this PR?"* — no reply in the thread as of 2026-10-27.
- Posting a reply on a third-party repo is an Owner stop under Tribute
  System 1, so the lane parked correctly by design — but the public debt
  stands: a maintainer asked what our PR is for, and the honest answer
  (a stake with no fix behind it) is the efficacy problem in one sentence.

### 3. interledger/interledger.org-v5 #804 — claim-only, and the bibschan verdict
- 2026-10-23T05:08Z: AarishMansur asks to be assigned.
- 2026-10-23T05:22Z: the lane posts its claim comment — **14 minutes after**
  the human's request (the claim text does offer to yield).
- 2026-10-26T23:46Z: maintainer **bibschan** assigns AarishMansur:
  *"hi folks – assigned to @AarishMansur, please let me know if you have
  bandwidth to work on it, otherwise we can assign to @timerloggedout-spec"*
- 2026-10-27T05:49Z: AarishMansur opens PR #823 (still open at audit time).

**Verdict: not mockery.** On the visible record this is ordinary,
professional triage: the first asker got the assignment; the lane was named
as the fallback, which is a (mild) trust signal — the maintainer treats the
lane as a known, assignable quantity. The efficacy finding is separate and
real: the lane claimed an issue a human was already taking and converted
nothing. This is exactly the case `preflight_candidate` (prior human claim →
exclude) now exists to block; `help_wanted_claim.py` on master does call it.

## Maintainer-perception assessment (evidence only)
- Negative: dysu-amd's unanswered "what is the purpose of this PR?" (ROCm);
  SendAm's silent batch closure of both stakes the same minute; the 63
  closed-unmerged PRs died at a median of **1 day** — maintainers are
  closing stake-shaped PRs on sight.
- Positive: bibschan naming the lane as fallback assignee; 16 merges,
  median same-day — when the lane (or a maintainer, tolerantly) lands
  something, it lands fast.
- Net: the claim comments read as *acceptable backup*; the stake PRs read
  as *noise*. Perception risk concentrates in unconverted stakes that
  linger (28 still open, oldest 46 days), not in claims.

## Reconciliation with concurrent work
| Item | Closes | Does not close |
|---|---|---|
| PR #1677 (open, **draft**) — fail closed on placeholder diffs, eligibility revalidation before push and before PR-open, SendAm #492/#607 regression tests | The **forward** stake failure mode: a placeholder can no longer earn solution status, and stale/claimed issues fail closed at delivery time | The 28 legacy stakes already upstream; the unanswered dysu-amd question; claim-only footprint (no PR → invisible to the diff gate); audit freshness. Still a draft — the gate is not law until merged |
| PR #1694 (open) — preserve historical audit coverage on partial refreshes | Audit-history monotonicity: a partial refresh can no longer erase a complete observation | Refresh **cadence**: the generated audit was last committed 2026-10-25T05:09Z ("live status refresh"); `help-wanted-status-refresh` runs since then: none scheduled after 2026-10-23, last run a manual dispatch 2026-10-25. The ledger missed the 2026-10-26 SendAm closures entirely |
| Tribute System 1 (on master) — classifiers, `preflight_candidate`, `preflight_pr`, `reengage_allowed` gates in scout/claim/contribute/followup writers | Post-hoc routing: retired/yield classes never re-engage (`tests/test_tribute_system1_gates.py` proves the seed fixtures never trigger a post) | Prevention at claim time is only as good as comment readability (unreadable → excluded, fail-closed: correct, but silent); claim comments are outside the PR audit universe |

## Gaps and recommendations
- **G1 — Legacy stake overhang.** 28 upstream PRs still open, 27 of them
  stake-only. R1: convert-or-withdraw pass — each gets a real patch or a
  self-close inside a set window. Closing our own PRs is a third-party
  write: **Owner decision**, list to be produced by the lane.
- **G2 — Unanswered maintainer question (ROCm #13152).** R2: surface to
  Owner with two prepared options (drafted reply, or withdraw the PR).
  Do not post from the lane (Owner stop).
- **G3 — Claims are unaudited.** The audit universe is PRs only; the #804
  claim-only pattern leaves no trace in efficacy numbers. R3: add a claim
  ledger beside the PR ledger (issue URL, prior-human-claim check outcome,
  disposition) so claim→conversion is measurable.
- **G4 — Audit staleness.** Generated audit is 2+ days old and missed the
  SendAm closures. R4: restore the status-refresh schedule (silent since
  2026-10-23) and alert when `generated_at` is >26h old.
- **G5 — Realization is unmeasured, not zero-proven.** 0 verified effects
  may understate reality, but the registry's independence rules are the
  lane's own honesty bar. R5: either file independent verifications for
  the merged set or report efficacy as "16 merged / 0 verified realized"
  everywhere — never a blended success count.
- **R6 — Merge #1677.** The forward gate is the highest-leverage fix in
  flight; undraft and land it (its CodeQL advisory was still running at
  recon time).

## Method limits
Universe = the lane's ledger, not search (author search undercounts this
account). 7 of 114 PRs were unreachable live and are carried as evidence
gaps, not outcomes. Closure actor was not returned by the API for the
closed-unmerged set; closure timing and state were used instead.
Claim-comment footprint beyond #804 was not enumerated — that absence is
itself G3.

— [MUSEai]@{role:{tribute-efficacy-audit}} · 2026-10-27 · Sources: live
GitHub API reads 2026-10-27; ledger snapshot 2026-10-25T05:09Z;
PRs #1677/#1694/#1671 and TRIBUTE-SYSTEM1.md read at master.
