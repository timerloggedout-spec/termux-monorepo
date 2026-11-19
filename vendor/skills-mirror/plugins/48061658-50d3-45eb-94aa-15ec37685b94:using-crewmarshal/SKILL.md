---
name: using-crewmarshal
description: Use when starting delegated multi-agent delivery on a project — maps the full workflow arc and points to the right crewmarshal skill and superpowers skill at each stage.
---

# Using CrewMarshal

CrewMarshal is the delivery discipline for work where **Claude architects and
reviews while external coding agents implement.** It stands on its own. When
superpowers is installed it works alongside it — using `brainstorming`,
`writing-plans` and `finishing-a-development-branch` for the design, plan and
integration steps, and slotting the delegation-and-review loop between them — but
it does not depend on it. Where the two disagree on how detailed a plan is, the
project decides, not either plugin — see `planning-for-delegation`.

## The Arc

**The arc is elastic.** `concept-briefing` tiers the request and that tier decides
which steps below actually run. What follows is the T2/T3 path — the full one.

```
pointer-handoff                  → (ongoing project) read the pointer, reconcile with reality
lessons-ledger                   → pull only the lessons matching this area + kind of work
concept-briefing                 → confirm system profile, tier the request, route
project-working-agreement        → load cadence + execution mode + role rules (set up once if missing)
[superpowers:brainstorming]      → design the change (steered by the profile)
[superpowers:writing-plans]      → draft the task-by-task plan
planning-for-delegation          → gate it: altitude, plan-detail convention,
                                   nine structural checks, assignment in waves, phase gates

   ┌─ executor-context           → keep the fixed context file current; handoffs point at it
   ├─ orchestrating-executors    → check quota, hand off ONE task in the background + monitor, don't poll; free agent + ready task → dispatch now
   │     checkpoint-verification  → inspect call-site + drive real runtime path
   │     convention-commit-gate   → enums, no magic literals, commit style
   └─  (loop per task; fix or re-dispatch if a gate fails; re-tier if scope diverges)

adversarial-review-to-go         → external reviewer, converge findings to GO
[superpowers:finishing-a-development-branch] → merge / PR / cleanup
pointer-handoff                  → write state + next action before the session ends
```

Steps in `[brackets]` come from the **superpowers** plugin, which exists on Claude
Code. On a harness without it, do that step directly — design before building,
write the plan before delegating, integrate deliberately at the end — and the
CrewMarshal skills around it are unchanged.

`pointer-handoff` brackets the whole arc: read at the start, written at the end
and whenever something significant surfaces mid-session. `lessons-ledger` is
consulted before working in an area, and written the moment a diagnosis proves
wrong or verification catches what the tests missed; its project-wide lessons get
crystallized into the `executor-context` file rather than pasted into prompts.

Projects with several services can run **multi-lane** once the working agreement
says so: the Chief runs this arc up to frozen contracts and a charter per lane,
then each lane coordinator runs the plan-to-commit part of the arc headless inside
its lane, always from a fresh session and its lane pointer; the Chief integrates.
Small projects never see it — see `multi-lane-coordination`.

Large layered work inserts one step: `concept-briefing` produces a **roadmap** of
phases from foundation upward, then each phase runs the arc above on its own,
with its own tier. Detailed plans are written per phase, never in advance.

### What runs at each tier

| Tier | Path |
|------|------|
| **T0** mechanical | Do it yourself → `convention-commit-gate`. Nothing else. |
| **T1** small, obvious | No spec, no plan file → executor → `checkpoint-verification` → `convention-commit-gate` |
| **T2** medium | Full arc, incl. `planning-for-delegation`; `adversarial-review-to-go` only if it touches a risky area |
| **T3** large / critical | Full arc, nothing skipped |

Skipping a step at T0/T1 requires the user's OK — `concept-briefing` asks once,
batched. Verification gates are never skipped when real code gets written.

## Where the Files Live

Every project document CrewMarshal keeps sits in the project's `docs/`: the pointer
(`STATUS.md`), `system-profile.md`, `working-agreement.md`, `team.md`,
`executor-context.md`, `lessons/`, and specs and plans under `specs/` and `plans/`
unless the working agreement puts them elsewhere. Multi-lane state goes in
`.crewmarshal/` beside it.

Projects set up by earlier versions keep these files in `docs/superpowers/`. Leave
them there or move them all at once — one location per project, never both. The
hooks look in both.

## When to Use Which Skill

| Situation | Skill |
|-----------|-------|
| Resuming an ongoing project, or closing a session | `pointer-handoff` |
| Starting work in an area, or recording a wrong diagnosis | `lessons-ledger` |
| Profiling the system + tiering the request before design | `concept-briefing` |
| Setting or changing how the team works: cadence, parallel vs sequential, role limits, plan detail | `project-working-agreement` |
| Planning large work as phases from foundation upward | `concept-briefing` (roadmap) |
| Deciding what to build | `superpowers:brainstorming` |
| Turning a spec into tasks | `superpowers:writing-plans` |
| Checking a plan before anyone is dispatched | `planning-for-delegation` |
| Several services, several coordinators, one Chief | `multi-lane-coordination` |
| Handing a task to an external agent | `orchestrating-executors` |
| Writing project context executors reuse every dispatch | `executor-context` |
| Accepting an executor's result | `checkpoint-verification` |
| Committing at a checkpoint | `convention-commit-gate` |
| Reviewing a spec, a plan, or a diff adversarially | `adversarial-review-to-go` |
| Integrating the finished branch | `superpowers:finishing-a-development-branch` |

## Principles That Hold Across All Stages

- Process depth matches the work. Mechanical work gets no spec; critical work
  gets everything. Measuring size without changing what runs is just ceremony.
- The system profile is confirmed by the user, not inferred and assumed. Scale,
  users, and what wins a trade-off decide architecture — a machine guess there
  propagates into every downstream prompt.
- Claude does not write business code — it designs, reviews, and verifies.
  (Exception: foundation/concurrency/verification code where precision beats
  delegation.)
- Every finding from any reviewer is re-verified on real source before it is
  applied — never blindly.
- Reviewers are locked to the altitude of what they review, and only a finite
  surface (a diff) can be converged to zero. A spec or plan is re-reviewed
  until a round leaves fewer than 5 findings, mostly low severity.
- Anything about the future — growth, expected load — is asked, never inferred.
  The repo holds no evidence about it, so a guess there is a guess that hardens
  into a fact.
- Green tests are never acceptance; the call-site and real runtime path are.
- Whoever writes the code does not certify it. Recompute expected values yourself.
- Every dispatch runs in the background with a monitor attached at launch; then
  you work on something else or wait for the notification — never poll. A monitor
  you describe but never start is worse than admitting there isn't one.
- The executor roster is machine-specific and lives in one file; the skills are
  portable.

## Across Harnesses

CrewMarshal installs on any agent harness that loads `SKILL.md` folders (Claude Code
and Codex both do). Two things differ by harness — neither changes the discipline:

- **Bookend skills.** `brainstorming`, `writing-plans`, and
  `finishing-a-development-branch` come from superpowers where it is installed.
  Without it, do those steps directly; every CrewMarshal skill works standalone.
- **Background work.** `orchestrating-executors` requires every dispatch to run in
  the background with a monitor that notifies this session. Where the harness has
  no verified channel for that, the dispatch does not meet the contract — say so,
  and use the fallback the project allowed or ask; never imply a watch exists.

Skill names are referenced without a namespace prefix here, because the prefix
differs per harness. Invoke them however your harness invokes skills.
