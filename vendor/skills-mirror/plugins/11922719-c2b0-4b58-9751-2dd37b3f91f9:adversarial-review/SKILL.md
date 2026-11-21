---
name: adversarial-review
category: Workflow
description: "Run several independent model seats against one problem or one plan, make them attack each other, fact-check every contested claim, then ask the human one gate of questions. Two modes: a design panel for an open problem, and a plan review for a drafted or approved plan. Use only when the human asks for adversarial or multi-seat work. Not for a code diff (use /code-review), pure ideation (idea-refine), or a single Verifier pass on one claim.\n"
---

# Adversarial review

Goal: get a design or a plan attacked by seats that fail in different ways, before anyone builds
it. Every mode uses the same method. Seats work on their own first, then attack each other, and
the moderator verifies each fact they dispute. The human then answers one gate of questions.

> **This install's seats, dispatch forms, record locations and worked examples** are in
> `LOCAL.md` beside this skill. Read it first when your copy keeps one.

## Guardrails (read before spending anything)

- **Only on request.** A panel costs four seats times three rounds. Run one only when the human
  asks for adversarial, panel or multi-seat work. Otherwise a single Verifier pass is the tool.
- **One Verifier pass per gate.** About to start a second seat on the same question? Then the
  brief was too thin. Fix the brief rather than adding seats.
- **Seats are read-only.** No seat edits a file. The moderator writes every record.
- **Different families beat more seats.** Two model families who disagree are worth more than
  four seats from one family who agree.
- **The moderator is not a seat.** She runs the rounds, checks the facts and writes the verdict.
  She never adds a proposal of her own to the panel.

## Mode 1 — Design panel (an open problem)

Records go in one folder: `README.md`, `problem.md`, `incidents.md`, `lenses.md`,
`r1-instructions.md`, `r1/<seat>.md`, `r2-instructions.md`, `r2/`, `r3-instructions.md`, `r3/`,
`facts.md` and the verdict page.

1. **Mine the history.** A cheap read-only agent (low tier) reads journals, handoffs and queues
   and writes `incidents.md`. It records failures only, generalized, with real numbers. It never
   describes the existing solution, so no seat anchors on it. Brief:
   [templates/history-miner.md](templates/history-miner.md).
2. **Write the brief.** `problem.md` holds the problem, the hard environment facts, numbered
   success criteria and the incident list. It tells each seat not to look for the current
   mechanism. Template: [templates/panel-problem.md](templates/panel-problem.md).
3. **Assign lenses.** Give each seat a different starting lens: correctness first, fewest moving
   parts, use the substrate, and contrarian. A seat may drop its lens once it is beaten. Template:
   [templates/panel-lenses.md](templates/panel-lenses.md).
4. **Round 1: independent proposals.** Each seat writes one design, specific enough to be
   attacked. It must include an incident table (prevented / made cheap / not addressed) and its
   own two weakest points. Run every seat in parallel. Template:
   [templates/panel-round-1.md](templates/panel-round-1.md).
5. **Check facts, then summarize the convergence.** List every factual claim the proposals
   disagree on or depend on, and verify it yourself. Use a scratch bare repo for git behaviour,
   the vendor's docs for platform rules, or a dry run against the real service. Write
   `facts.md` ([templates/facts.md](templates/facts.md)): VERIFIED with the method, or
   UNVERIFIED with why it matters. Then name what the
   seats agree on and the live disagreements as (a), (b), (c)…
6. **Round 2: cross-attack.** Each seat gets all the proposals plus `facts.md`. For each other
   proposal it writes 1–3 kill shots: a concrete timeline (machines, sessions, times, state)
   rated fatal, serious or tolerable. It also attacks the consensus, rules on each disagreement
   in one line, lists what it would steal and states its concessions. Template:
   [templates/panel-round-2.md](templates/panel-round-2.md).
7. **Check facts again.** Verify every new claim a kill shot rests on, and append it to
   `facts.md`.
8. **Round 3: final designs.** State the settled points (S1…) as binding unless a seat can show a
   timeline that breaks one. State the remaining cruxes (C1…) with the real numbers. Each seat
   delivers a final design on top of the settled points, a position on each crux with numbers,
   a ledger answering every kill shot aimed at it, and one test to run before building. Template:
   [templates/panel-round-3.md](templates/panel-round-3.md).
9. **Run the tests the seats asked for**, where they are cheap and safe. Add the results to
   `facts.md`.
10. **Write the verdict.** Publish it as a page the human can come back to. It holds the chosen
    design, which seat won each crux and why, the facts table and the open decisions. Then ask
    the decisions in one gate (see *The question gate*) and record the answers in `README.md`.
    Nothing gets built from a panel: its output is the input to `planning`.

## Mode 2 — Plan review (a drafted or approved plan)

1. **Write the brief.** It lists the plan, the design record, the live files the plan changes,
   what has landed and the current state. Verify that state yourself first, and date it. Save it
   beside the plan as `review-brief.md`. Template:
   [templates/plan-review-brief.md](templates/plan-review-brief.md).
2. **Dispatch two reviewers in parallel.** Use the Verifier and a reviewer from a second model
   family. Both are read-only, and both get the same brief.
3. **Each reviewer works per item, then on the whole program.** For every item she gives the most
   likely live failure as a concrete sequence, the decisions it needs that the plan does not
   state, and any ordering or blocker errors. For the whole program she covers rollback, cutover
   with live sessions, distribution of binaries and config, parallel programs, availability and
   execution constraints. She ends with a deduplicated question list. Each question has options,
   with her recommendation first, and is marked BLOCKING or LATER (with the item it blocks).
4. **Save the reviews** beside the plan as `review-<seat>.md`. Keep each review's own words; a
   condensed copy says so in its first line.
5. **Merge the reviews with your own pass.** Check every claim a reviewer marked as source-derived
   against the file it cites. Then split the questions in two:
   - **Technical, with one right answer**, where both reviewers agree or a check settles it:
     LOCK it on the recommendation (L1…). List it for objection, but do not ask it.
   - **A real choice** (policy, money, risk appetite, the human's time or presence): it goes to
     the gate.
6. **Ask the gate** (see below). Builds already running that an open question affects may finish
   and test, but they hold their land until the answer arrives.
7. **Revise the plan.** Add a `## Revision N` section that links the reviews, names the faults
   they found, and holds the human's answers (D…) and the locked items (L…) as tables. It ends
   with the revised order. Commit it.

## The question gate (both modes)

- Ask in one gate, using the structured-choice tool with up to 4 questions per call. Calls may
  run back to back. Put the recommendation first in every question.
- A second gate is only for questions that cannot be worded until a first-gate answer is in.
- Once the last answer is in, say plainly that the gate is closed.

## Common failure modes

- **Showing seats the current solution.** They anchor on it and review it instead of designing.
  Give them the incidents, not the mechanism.
- **A fact one seat asserted becomes a premise.** Every contested claim goes through `facts.md`
  before the next round reads it. A seat sounding confident is not a check.
- **Vague attacks.** "This might be complex" is not a kill shot. Send it back for a timeline.
- **Asking the human technical questions.** If both reviewers agree and a check confirms it, lock
  it. The gate is for choices.
- **A verdict that lives only in chat.** Write the records and the verdict page, and write the
  answers back the same turn they are given.

## Before you call this done

- [ ] The human asked for adversarial or multi-seat work
- [ ] At least two model families sat, and every seat was read-only
- [ ] `facts.md` (panel) or the merged pass (review) verified every contested claim, and the
      claims nobody could verify are marked UNVERIFIED
- [ ] All records are saved where the next session will find them
- [ ] One gate asked, answers recorded, gate declared closed
- [ ] Panel: verdict page published. Review: `Revision N` committed to the plan

## Related skills

- [planning](../planning/SKILL.md): a panel's verdict is a plan's input. A plan review produces the
  plan's next revision.
- [idea-refine](../idea-refine/SKILL.md): use it when the idea is still vague. A panel needs a
  problem with success criteria.
- [orchestration](../orchestration/SKILL.md): seat briefs are sub-agent briefs. Make them
  self-contained, decision-complete and read-only.
