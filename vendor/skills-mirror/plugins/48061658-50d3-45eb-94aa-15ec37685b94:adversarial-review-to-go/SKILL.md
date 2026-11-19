---
name: adversarial-review-to-go
description: Use when a spec, a plan, or an implemented diff needs an external adversarial reviewer — locks the reviewer to the altitude of what is being reviewed, converges diff findings to zero (GO), re-reviews a spec or plan until a round leaves fewer than 5 findings, mostly low severity, and re-verifies every finding on real source before acting.
---

# Adversarial Review to GO

For design-sensitive or concurrency-sensitive work, one review pass is not
enough. Run an external adversarial reviewer (the reviewer-strong agent in the
roster), re-verify each finding yourself, patch the valid ones minimally, and —
**on a finite surface** — review again until a round produces zero surviving
findings ("GO").

Two things decide whether that loop is right: **what surface you are reviewing**
(below) and **what altitude the reviewer is locked to**
([references/review-prompts.md](references/review-prompts.md)). Get either wrong
and the rounds stop converging.

This is the delegated-reviewer counterpart to
`superpowers:receiving-code-review` — apply that skill's discipline (act on
valid feedback, push back with reasoning on invalid feedback) to an external
agent's output.

## Where the Loop Applies

Both surfaces loop, but they stop at different places.

| Surface | Rounds | GO |
|---------|--------|----|
| **Diff / implemented code** | loop until zero | a round with zero surviving findings. Finite surface — the last round is where subtle findings surface. |
| **Spec / plan** | loop while the last round still found enough | a round with **fewer than 5 surviving findings, most of them low severity**. |

A document never needs zero. Every patch writes new prose and new prose is new
surface, so the finding count on a document has a floor that is not zero —
chasing zero is what once took a document from **300 → 720 lines** with findings
going **10 → 11**. But one round is not enough either: whether to go again is
decided by **what the previous round caught**, not by how long the document is.

## The Document Loop (spec and plan)

Every finding carries a **severity** (see the finding format):

| Severity | Spec / plan meaning |
|----------|---------------------|
| **High** | sends the design or the executor the wrong way: a wrong decision, a hard boundary broken, a DoD that goes green while the goal is unmet, a task that cannot run, a false parallel, an undecided "or" with data or security consequences |
| **Medium** | forces rework or a guess: a missing constraint, an acceptance that measures the easy part, a dependency stated loosely |
| **Low** | clarity, wording, a gap an executor would resolve correctly on its own |

After each round, re-verify every finding (the Golden Rule), patch the valid
ones, then count the **surviving** findings — the ones that held up on
re-verification, not what the reviewer sent:

- **Fewer than 5 surviving, and more than half of them Low → GO.** Stop.
- **Otherwise → another round.** A round that still catches 5 or more real
  defects, or catches few but mostly Medium/High, is evidence the next round will
  catch more.

Surviving findings are patched before deciding, including the round that reaches
GO. Severity is judged against `system-profile.md`, and the reviewer's label is
re-verified like the finding itself — a finding inflated to High to keep the
loop running, or deflated to Low to end it, is re-labelled by the owner.

Every round after the first runs with these guards, which are what keep the
loop converging:

1. **Altitude-locked prompt** — the spec/plan template, never a generic one.
   Uncalibrated, the loop diverges; calibrated, most findings stay at the
   document's own layer and some are cuts.
2. **Coverage report.** The reviewer lists which sections it examined deeply
   and which it only skimmed. Round N+1 targets **round-N patches first, then the
   skimmed sections** — not a fresh sweep of what was already covered.
3. **Smallest patch.** Each patch is the smallest change that closes the
   finding, and cuts from the reverse altitude check land in the same round.
4. **Fresh reviewer thread each round**, with the self-contained prompt — a
   resumed thread defends its earlier findings and anchors on what it already
   read.

## The Stop Rule

**If findings do not decrease across two consecutive rounds, the process is
broken — fix it before the next round.** On a diff, stop and do not run another
round until it is fixed. On a document, same: the next round only runs after the
cause is fixed, and the GO condition above is still the only way out. Check, in
this order:

1. **Altitude** — is the reviewer being invited to find things that belong one
   layer down? (Reviewing a spec with a source-file list attached is the
   classic.) Fix the prompt, not the artifact.
2. **Patch-induced findings** — see below. Were the patches larger than the
   findings needed?
3. **Severity drift** — are Low findings being counted as Medium to keep the
   loop alive?

If the cause cannot be found, show the user the per-round curve (count and
severity split) and let them decide.

## Lock the Reviewer to the Altitude

Calibration has **two axes**, and the skill used to name only one.

**Severity** comes from `concept-briefing`'s `system-profile.md` — include it in
every review prompt: the trade-off priority order, the hard boundaries, the real
scale. Without it a reviewer applies generic best practice and you get noise in
both directions: scaling findings on a 200-user internal tool, or a shrug at a
boundary that must never break. A finding is only real relative to this system's
priorities. The profile does **not** soften the bar on what it names untouchable
— those are the findings to take most seriously.

**Altitude** comes from *what is being reviewed*, and it is what the prompt must
constrain. Three templates, one per artifact type, in
[references/review-prompts.md](references/review-prompts.md):

| Reviewing | Ask about | Forbid |
|-----------|-----------|--------|
| **Spec** | decisions, missing constraints, DoD that can go green for the wrong reason | source-file lists, "check it against the code", mechanism |
| **Plan** | can each task actually run, are the dependencies real, does acceptance measure the *hardest* requirement | debating mechanism, rewriting the design |
| **Diff** | correctness at the cited site, gaps tests don't cover, seeded mutations | — file lists belong here |

Do not reach for one generic prompt and adjust it by feel. The controlled
comparison is stark: same model, same document, prompt switched to lock altitude
⇒ implementation-layer findings dropped to **0** (previously the majority) and
**3/10** findings were "cut this, it belongs in the plan".

## Patches Breed Findings

**Round N+1 reviews the round-N patches first.** Say so in the prompt, and name
the patched sites.

In the measured document review, **6 of 11** round-2 findings were caused by the
round-1 patch itself. A reviewer that treats round N+1 as a fresh sweep spends
its attention on the parts nobody touched, and the newest, least-reviewed text
gets the least scrutiny — exactly backwards.

## Ask for the Reverse Altitude Check

Alongside "what is missing", ask the reviewer for **what is present that belongs
one layer down and should be cut**. Reviewers volunteer additions by default;
subtraction has to be requested.

This is what keeps a spec from drifting into plan territory over successive
rounds, and it is directly measurable: 3 of 10 findings in the calibrated round
were cuts. A document that only ever grows under review has been told, by
omission, that growth is the only allowed outcome.

## Every Finding Ships With Fix Options

A finding with no fix is a bug report: it hands the owner a blank page at the
exact moment the context is freshest in the reviewer's head. **Every finding
carries 1-2 proposed fixes** — required output, not a courtesy.

Each finding has these fields, in this order:

| Field | Content |
|-------|---------|
| **Finding** | what is wrong, at the cited place |
| **Failure** | the concrete consequence — inputs or interleaving → wrong result. Not "risky" |
| **Fix options** | 1-2 directions. Each: the approach and where it applies, in at most two sentences, plus its cost — what it breaks, slows, or postpones |
| **Recommended** | which option, and why — or "owner decides" plus what the decision turns on |

A second option only when it takes a **different approach**. The same fix at two
sizes is one option.

**A fix option is a direction, not a patch.** Name the approach and the place it
applies, then stop. Two sentences is the whole budget — no code, no diff, no
rewritten paragraph, no line numbers. The detail belongs to whoever re-verifies
the finding on real source, because only they can see what the surrounding code
actually allows.

| Right size | Too deep |
|------------|----------|
| "Guard the read-modify-write in `applyQuota` with a compare-and-swap on the version field — costs a retry loop." | the 30-line patch that implements the CAS |
| "State the retention limit as a constraint in §3 instead of leaving it to the plan." | the rewritten §3, drafted for you |
| "Split T4 — the migration and the backfill touch the same table and cannot run in parallel." | a re-sequenced task list with new IDs |

A fix option that no longer fits in two sentences has stopped being a direction
and become the implementation — which is the owner's work, and only after the
finding is confirmed. An over-detailed option costs twice: the reviewer spends
its attention drafting instead of finding, and the draft is persuasive enough to
get applied without the check.

**Fix options inherit the review's altitude**, exactly as findings do:

| Reviewing | A fix option looks like |
|-----------|-------------------------|
| **Spec** | which decision to take instead, or what constraint the spec is missing — named, not drafted |
| **Plan** | which task to split, which dependency to reorder, what the acceptance should measure |
| **Diff** | where the guard belongs and what kind — the smallest one that holds, not the code for it |

A spec review that answers with a patch has dropped an altitude — the same defect
as attaching a source-file list to the prompt, arriving from the other end.

**They are suggestions, and the Golden Rule still runs.** A proposed fix is the
reviewer's hypothesis about a defect you have not confirmed yet. Confirm the
finding on real source first, then decide whether either option is the right
patch. A well-written fix option is the most persuasive thing in the report and
the easiest to apply without looking — which is precisely why re-verification
comes first.

## Seed Mutations (Diff Reviews)

Green tests prove the code runs. They do not prove the tests are watching the
right thing. Require the reviewer to:

1. Copy the repo to a scratch directory.
2. For **each constraint the task claims to satisfy**, seed a deliberate defect —
   preferring the failure modes the handoff itself called classic.
3. Run the suite and report **which mutations were not caught**.

At a real gate this caught 4/4 seeded mutations, including the exact trap the
handoff had flagged. Without it, a green suite of hundreds of tests is evidence
of very little.

## The Golden Rule

**Always re-verify each finding against the real source yourself. Never apply
findings blindly.** The external reviewer is fast and catches things e2e can't
(crash-gap, TOCTOU, migration-on-deploy), but it is also sometimes wrong or
wrong about severity. For each finding:

1. Confirm it on the actual code (reproduce the reasoning at the cited site).
2. If valid — weigh the reviewer's fix options against what the code actually
   shows, then patch minimally (prefer a CAS/guard at the exact contention point
   over a broad rewrite) and re-verify with `checkpoint-verification`. Taking an
   option unchanged is fine once you have confirmed it at the site; taking it
   because the reviewer wrote it well is the failure.
3. If invalid or overstated — push back with the code/test that disproves it,
   and record why it was rejected.
4. Surface rejected findings to the user for a decision when they involve a
   real trade-off (e.g. distributed primitive vs in-process guard). Same for any
   finding the reviewer marked "owner decides" — pass both options up as written,
   with their costs, rather than picking one quietly.

This one is not a theory: across a full delivery, 21 of 21 findings survived
independent re-verification and none were rejected — which is exactly why the
rule is cheap to keep and expensive to skip the one time it matters.

## The Round Loop (diff)

```
round = 1
repeat:
    dispatch external reviewer on the current diff
        (self-contained prompt: plan pointer + diff scope + system-profile;
         round > 1: name the previous round's patched sites, review them first;
         require seeded mutations for every claimed constraint;
         require the finding format: finding + failure + 1-2 fix options + recommendation)
    for each finding: re-verify on source → choose among the fix options
                      → patch-if-valid / rebut-if-not
    re-run checkpoint-verification (2 consecutive green where applicable)
    if findings did not decrease over the last two rounds: STOP, check altitude
    round += 1
until a round yields zero surviving findings  → GO
```

For a spec or a plan, the same loop with two differences: targets are the
patched sites plus the sections the previous round skimmed, and the exit is
**fewer than 5 surviving findings, more than half Low** instead of zero.

## Practical Notes

- Keep each review prompt self-contained (pointer + scope + profile) so a fresh
  reviewer thread works — don't rely on a giant resumed context.
- The reviewer may run out of quota mid-loop. A purely formal confirmation round
  can be skipped if the user agrees; already-verified mechanical fixes don't
  need another round.
- Record the convergence (e.g. "4 rounds, 5→2→1→0"; for a document with the
  severity split, e.g. "3 rounds, 12 (5H) → 7 (2H) → 3 (0H, 2L)") and the accepted residual
  trade-offs in the merge commit or plan notes. Record a non-convergence too,
  with what the altitude check found — that is a `lessons-ledger` entry.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Reviewer flagged it, just apply it" | Re-verify on source first. Reviewers are sometimes wrong. |
| "One round was clean enough" | On a diff, converge to zero. The last round is where subtle ones surface. |
| "One round on the spec is enough" | Count what that round caught. 5+ surviving, or mostly Medium/High, means go again. |
| "The spec is short, skip the second round" | Length does not decide. The previous round's findings do. |
| "Only 3 findings left, but they're High — ship it" | GO needs fewer than 5 **and** mostly Low. Go again. |
| "Findings went up — run another round" | Findings went up because the altitude, the patches or the severity labels are off. Fix that first. |
| "I'll give the reviewer the file list so it can check properly" | On a spec or plan that is the bug. It invites implementation-layer findings you then patch into the document. |
| "The reviewer will figure out what layer to work at" | It will not. It answers the prompt you wrote; a file list is an instruction. |
| "Round 2 should look at everything again" | Round 2 looks at round 1's patches first. That is where the new defects are. |
| "149 tests pass, the constraint holds" | Tests prove it runs. Seed a mutation to prove they are watching. |
| "Rewrite the whole thing to be safe" | Patch minimally at the contention point. Broad rewrites add risk. |
| "Rejecting this finding, moving on" | If it's a real trade-off, the user decides — surface it. |
| "The reviewer wrote a fix, apply it" | The fix rests on a finding you have not confirmed. Verify at the site, then choose. |
| "Findings only — proposing the fix is my job" | Then every finding starts from a blank page. 1-2 options are required output; the choice is still yours. |
| "Ask for three or four options to compare" | Two different approaches, max. A menu shifts the thinking back onto you and dilutes the reviewer's reasoning. |
| "Handy patch for my spec finding" | Spec fixes are decisions and constraints. A patch means the reviewer dropped an altitude — reject it like a file-list finding. |
| "It shipped working code, that saves me a step" | Code written against source the reviewer only partly saw. Take the direction, write the change yourself after confirming the finding. |
| "More detail in the option means less work for me" | It means the reviewer spent its attention drafting instead of finding, and the draft is persuasive enough to get applied unchecked. |
| "Reviewer wants it hardened for scale" | Check the profile. On a one-replica internal tool that's noise; on the boundary it calls untouchable it's the opposite. |
