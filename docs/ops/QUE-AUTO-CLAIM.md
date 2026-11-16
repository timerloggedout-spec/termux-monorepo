# QUE auto-claim + auto-resolve (QUE #5286)

Origin: 2026-11-12 — 11 dispatch-watchdog ESCALATION notifications,
6h stale, headlined "UNCLAIMED for 441 minutes", while claims moved
17 → 20 against escalations 13 → 28 in a day. The system logged
stalls perfectly and then stopped; the drain that followed was a
hand route. This build gives the machinery the missing hand.

Decision of record: owner c.6843045932 · QDesk decision c.6843060529
· Cadence countersign c.6843070784 (no objection; thresholds derived
per entry at admission; the 15/30 numbers slot into the #4977 Fix-5
frame — no new governor constants). Binding on this build's landing.

## Mechanism (all inside the dispatch watchdog sweep)

1. **Claim at escalation, same pass, by rank.** A filing that
   crosses its escalate threshold still unclaimed — or one already
   escalated and still unclaimed — is claimed mechanically in the
   same watchdog pass, in que-task-rank/v1 order (#5283, binding
   since c.6843024949). Effective escalate threshold = min(tier
   frame, standard 15m); a tighter tier governs. Precedence:
   {tighter tier > wall-bound ≤48h claim-on-admission > standard
   15m}. A stall reaching 30m unclaimed emits a
   `stall_ceiling_breach` stall event on its exception escalation.
2. **Claim classes** come from the filing's own stamp: an explicit
   `claim-class:` line wins, then a named `executor of record:`,
   then the SWARM-DISPATCH route (`build-dispatch` → executor class,
   claimant `dispatch-executor`; `project-task-dispatch` → the
   QDesk seat queue, claimant `qdesk-seat-queue`). No stamp naming a
   class = unplaceable.
3. **The claim is the claim_task.py effect** — a PRODUCER CLAIM
   comment naming the machine as claimant of record + the
   `dispatch-claimed` label in the same motion, with the
   `dispatch-escalated` label removed. The claim resolves the
   **stall** (feed stall events close with the claim as resolution
   ref; the stall clock stops) — never the task, whose completion
   still requires its own done-evidence.
4. **Escalation is the exception.** Owner/QDesk-facing escalation
   fires only when placement fails — gated class, no claim class,
   or claim rejected twice — with the reason stamped on the
   escalation comment itself. Already-escalated exceptions never
   re-fire.
5. **Hard boundary.** Value-class / owner-gated work (labels
   `value-class` / `owner-gated` / `owner-hand`, or the
   `participation_set` / `countersign-required` / `owner-hand`
   markers) is never auto-claimed; it escalates by design. No
   admission/governor threshold changes beyond the countersigned
   timing slots.
6. **Lease + reclaim.** An auto-claim carries a lease (executor
   120m, seat-queue / named-executor 240m — claim-machinery windows,
   stamped in the claim comment). A claim with no execution state
   change (no non-watchdog comment) inside its window releases back
   to the pool: lease-release comment + label removal, and the
   filing re-enters ranking for re-claim. Manual claims carry no
   lease and are never reclaimed by this machinery.
7. **SIE gap feed.** Every auto-claim, failed placement, and lease
   release emits a record into `ops/que/feeds/stall-gap-feed.json`
   (schema `que.stall-gap/v1`, gap class `escalation-stall`, counts
   per cycle) — the SIE self-repair loop's learn-ledger intake,
   committed by the watchdog workflow alongside the dispatch-state
   feed.

## Code

- `scripts/dispatch/auto_claim.py` — pure decision logic (classes,
  gating, leases, planning, gap records).
- `scripts/dispatch/dispatch_watchdog.py` — classify caps escalate
  at the 15m standard; the sweep plans and executes claims /
  releases / exception escalations; the feed closes stall events
  with claim resolutions.
- Tests: `scripts/dispatch/test_auto_claim.py` +
  `test_dispatch_watchdog.py` (threshold expectations re-pinned to
  the timing decision, cited in place).

Live done-evidence (first post-merge watchdog cycle: a real
auto-claim by rank, a closed stall, zero re-fires) stamps onto
QUE #5286 as it occurs.
