# QUE task-ranking amendment — blocker / dependency / benefit terms (QUE #5646)

Amends: `docs/ops/QUE-TASK-RANKING.md` (method of record
`que-task-rank/v1`, QUE #5283) and the lease rule in
`docs/ops/QUE-AUTO-CLAIM.md` §6.
Authority: owner directive 2026-11-26 (#5646 c.7202914059) under the
QUE efficacy program of record (#5646). Landed by the main seat per
the owner's same-day order: if the queue still needs to claim and
execute, Muse lands #5646 itself.
Status: amendment of record. The additive score terms below are
specified exactly so the executor leg can implement them in
`scripts/que/task_ranking.py` as a method bump; until that code lands
and DoE scores the generation (scored path, #5546), the terms bind
claim-order *policy* — the watchdog sweep's per-pass reprioritization
(#5646 Leg 4) reads this document.

## The defect this amendment answers

The v1 score (tier + wall + age + state) cannot rank a
system-unblocking item above routine work, and the lease machinery
converts claim failure into silent repetition: a claim expires with
no execution state change, releases, re-claims, and releases again —
each cycle stamping the item, none of them escalating. The owner's
words, 2026-11-26: *"We had to manually|physically get some queued
PR's DOne."* A completion a human had to carry is the rubric's
failure, not the item's. The census in Appendix A is the evidence:
two items, 147 lease releases between them, zero execution.

## 1. Additive upward terms (blockers · dependencies · benefit-opening enhancements)

Three additive components join the v1 dispatch score. Each is
evidenced from the item's own scope (a stamped link or edge), never
asserted freehand — the same evidence standard as the leverage term
L (#5546 c.6980162905).

- **B — blocker-class, +250.** The item's non-completion stalls at
  least one other queued item or a live breach. Evidence: a stamped
  `blocks:` link on the item, or a dependency edge in the QUE Gantt
  representation (#5631) where this item is the blocker.
- **U — dependency-unblocking, +150.** The item's completion directly
  clears a stamped blocker for the current head-of-order item or a
  wall-bound item. Evidence: the blocker edge it clears, named in the
  item's scope or in the dependent's stamp. (B scores the item's
  position in the graph; U scores its immediate effect on the head.)
- **E — benefit-opening enhancement, +100.** An enhancement whose
  completion opens a capability, lane, or benefit that does not exist
  without it — e.g. a provider endpoint enrollment that opens a new
  inference lane. Evidence: a stamped `opens:` / `enables:` line in
  the item's scope.

B, U, and E stack, capped at **+400 combined**. The v1 invariant is
preserved: the maximum non-imminent combination is now
80 (tier) + 152 (wall decay) + 50 (age) + 40 (state) + 400 = 722,
still below the imminent-wall class (≥1000), so a wall inside 48h
continues to outrank every non-imminent combination.

### Leverage term L extended to the PR queue

L (#5546: an item scores for what its completion unblocks —
{bucket relief · items unblocked · lanes restored}, #5309 the
calibration case) has applied to issue claims only. Per the owner
directive, **L extends to PR-queue items**: a queued PR whose merge
unblocks work on the same evidence standard scores L from its linked
issue's scope. Until DoE's binding ruling on L, PR-queue rows publish
their L as an `L-shadow` component alongside the v1 components — the
publication step #5546 c.6980191416 already ordered for issue rows —
so the term is visible in the feed before it binds.

## 2. Hand-carried completion = rubric-miss

Any queued item (issue or PR) that reaches done through a
manual/physical carry — a seat hand-merge, a hand-claim outside the
machinery, an owner paste — is logged as a **rubric-miss datum** on
#5646 in the same pass the carry is detected:

```
rubric-miss: {item · carry route · the term (B / U / E / L / wall)
that should have ranked it claimable · pass id}
```

A rubric-miss counts against the rubric generation in DoE scoring of
the ranking line (#5546), never against the item. The acceptance
metric of this amendment is the owner's: queued PRs reaching done
*without* a carry. A pass with zero carries and zero rubric-misses
is the healthy state; a carry with no rubric-miss stamp is a
detection defect on this leg.

## 3. Required-upgrade class at the head of claim order

Claim order of record, recomputed per pass from live state (#5646
Leg 4), is:

1. **Owner-stamped leverage head** (the #5309 class).
2. **Required-upgrade class** — endpoint enrollment / activation
   filings under #5587, and any item stamped `required-upgrade`.
   Per the 2026-11-26 enrollment directive (#5587 c.7202912452),
   enrollment is the highest-priority QUE work: QDesk enrolls new
   Provider Inference Endpoints into the catalogue autonomously, and
   activations flow into the DoE pool generator under the standing
   gates. This class sits ahead of the escalated band (extends
   #5646 c.7191920432 from a single item to the class).
3. **Escalated band.**
4. **DoE v1 binding score order** (with §1 terms as they bind).

## 4. Lease-release cycling escalates — no fourth silent cycle

`QUE-AUTO-CLAIM.md` §6 releases a claim with no execution state
change back to the pool for re-claim, with no bound on repetition.
Leg 4 (#5646 c.7144252233) constituted a per-issue cycle counter and
a one-time escalation, but the sweep is not yet effective in the
watchdog run (#5646 acceptance instances #3 and #4: #5220, #5614 —
counters and escalations absent while the cycles ran). This
amendment makes the bound explicit and small:

- The watchdog carries a **per-issue consecutive-release counter**:
  lease releases with no execution state change since the claim,
  counted consecutively (any execution state change resets it).
- **At 3 consecutive releases, the machinery escalates once** — a
  stamped escalation on the item naming the cycle count, plus a
  defect datum on #5646. Three is the bound because 3 is where a
  seat caught #5614 by hand (instance #4); the machinery must catch
  it there first, without a seat.
- After that escalation the item is **claim-ineligible for silent
  auto re-claim** until a named claimant claims it or a stamped
  HOLD-cause (arm + pre-flight state, per #5646's conversion
  checkpoint) lands on it. There is no fourth silent cycle.
- Deferred-by-tier items are claim-ineligible outright (the #5220
  datum, instance #3): a tier-deferred item is never auto-claimed,
  so it can never enter the release cycle.

## Appendix A — churn census (evidence, live API, 2026-11-26)

Method: every comment on each issue fetched via the API and
classified by its machinery marker (LEASE RELEASE / PRODUCER CLAIM /
watchdog ESCALATION / routing / admission stamps vs substantive
content). Counts are exact as of the fetch (2026-11-26 ~20:47Z);
both issues remain open and the release counters were still moving.

### #5584 — Fleet Swarm rename, DOE-NAME tournament (filed 2026-11-17)

| class | count |
| --- | --- |
| total comments | 80 |
| LEASE RELEASE (watchdog) | **73** |
| PRODUCER CLAIM (watchdog) | 1 |
| watchdog ESCALATION | 1 |
| routing receipt + admission | 2 |
| substantive | 3 |

- Lease releases: 2026-11-25 ×7, 2026-11-26 ×66; span
  2026-11-25T21:57:28Z → 2026-11-26T20:08:37Z (~22h), claimant
  qdesk-seat-queue, every one "expired with no execution state
  change inside its lease window".
- Substantive comments are: the DoE commission acceptance
  (2026-11-17T17:02:53Z), a bot boilerplate notice, and the main
  seat's escalation stamp (2026-11-26T20:33:11Z). Execution
  comments (build dispatch, verdict, PR): **0**. The tournament's
  rounds have never run.
- Note the shape: 73 releases against a single on-issue claim
  stamp — the re-claims between releases did not each leave a
  claim comment, so the cycle is even quieter than the stamps
  suggest.

### #5614 — dispatch-watchdog defect filing (filed 2026-11-18)

| class | count |
| --- | --- |
| total comments | 81 |
| LEASE RELEASE (watchdog) | **74** |
| PRODUCER CLAIM (watchdog) | 1 |
| watchdog ESCALATION | 1 |
| routing receipt + admission | 2 |
| substantive | 3 |

- Lease releases: 2026-11-25 ×7, 2026-11-26 ×67; span
  2026-11-25T21:57:16Z → 2026-11-26T20:39:05Z, claimant
  qdesk-seat-queue, same no-execution-state-change cause.
- Substantive comments are two main-seat diagnosis/staging stamps
  from filing day (2026-11-18) and a bot boilerplate notice.
  Execution comments: **0**.
- #5646 acceptance instance #4 caught this item by hand at 3
  cycles on 2026-11-25 (21:57Z, 22:13Z, 22:38Z) and recorded that
  no Leg-4 counter or escalation stamp existed. The cycles then
  continued for another ~22 hours and 71 more releases — the
  direct evidence for §4's bound.

### Of record, not re-censused here

#5220 (acceptance instance #3, #5646 c.7144208742): 571 comments,
lease-release loop by the same claimant against a deferred-by-tier
item; each cycle also generated an owner notification email. §4's
deferred-item ineligibility answers this class.
