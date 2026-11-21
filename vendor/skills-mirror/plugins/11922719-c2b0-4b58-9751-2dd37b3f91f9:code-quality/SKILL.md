---
name: code-quality
category: Engineering
description: "Standards for reviewing and cleaning up code. Use when reviewing any diff (your own before commit, a Codex or sub-agent diff, a colleague's PR) or when asked to clean up, de-duplicate or delete dead code. Holds the hard rules, the review checklist (standards and spec axes), module-design tests, and proof of deadness before deleting. To run a review use /code-review; to apply cleanups, /simplify.\n"
---

# Code Quality

Goal: every diff meets the hard rules below and reads like the rest of the codebase,
and dead code goes — **without ever deleting something that is actually used.** When
in doubt, do not delete; flag it instead. A false-positive deletion (removing live
code) is far worse than leaving one dead function in place.

> **Who writes the code:** if implementation is delegated to another agent, this
> skill is the standard the reviewing agent holds the work to, not a licence to edit
> product code directly. A cleanup the reviewer wants goes to the implementer as a
> brief; the deletion bar below is what the returned diff is held to. (Fallback: if
> the implementer is unavailable, implement at the identical bar and flag it
> inline.) Who executes in this install: `LOCAL.md` beside this skill, when your
> copy keeps one — *Who writes the code*.

## Hard rules — every diff, whoever wrote it

These are not style preferences. A diff that breaks one gets a **Required** finding,
and a brief to an implementing agent names all three.

1. **One responsibility per file.** A file has one reason to change. A file that both
   decides and coordinates (business logic plus orchestration), or that serves two
   features, is two files.
   - **The one exception is a single-file component** (a Vue SFC and the like), which
     holds template, script and style together. Even there, move the logic out into
     composables (or the stack's equivalent) and split the component into children,
     so no single component carries a whole screen — unless its complexity really
     demands it. Keep the extraction performant: no extra reactive layers or watchers
     just to split.
   - **Size cue (soft):** past ~200 lines for a component file or ~300 for any other
     file, the reviewer must say why it still has one responsibility, or split it.
     The number prompts the look; the one-reason-to-change test decides.
2. **Readable by a junior engineer.** A junior engineer can follow the functional flow
   without asking anyone. The flow is clean, simple and consistent.
3. **One rhythm per kind of work.** The same kind of work (an endpoint, a screen, a
   job, a form) moves data through the same stages, in the same order, with the same
   names and the same error and loading shape, everywhere in the codebase. Someone
   who has read one should be able to predict the next.
   - Before writing, find the closest existing instance of this kind of work and
     mirror its flow, not just its formatting.
   - Mirroring the established flow is never speculative, even when this one
     instance would get by without a stage. A shorter one-off is a second pattern,
     and a second pattern is the defect.
   - A better pattern is a migration, not a local improvement: propose moving every
     instance (as its own change), or keep the existing rhythm.
   - Review check: could a reader who knows the sibling predict this file's
     structure?

## Code quality & style

Match the code to its surroundings — the bar is "reads like the rest of this
file/module," not your personal preference; for a kind of work, the codebase's rhythm
(hard rule 3) is the surroundings. Naming, comment density, error handling, and file
layout all follow local idiom; don't introduce a style island.

- **Respect per-repo conventions over general taste.** A repo may, for example,
  ban comments entirely in some languages (extract a name instead), or keep
  framework decorators out of shared type libs. Read AGENTS.md, CLAUDE.md, and
  neighbouring code before imposing anything. (This install's standing conventions:
  `LOCAL.md` beside this skill, when your copy keeps one — *Per-repo conventions*.)
- **DRY with judgment — three strikes before a shared helper.** Two pieces of logic
  that merely look alike today are not duplication. This governs shared *logic*; the
  shape of the flow is hard rule 3. One exception: two copies that must stay in
  lockstep (the same fields, the same contract) share one base from the second use,
  so they cannot drift.
- **No speculative mechanism in new code:** no generic engines, configurability,
  factories, registries or flag parameters for single-use code; no "flexibility"
  that wasn't requested; no error handling for scenarios that cannot occur.
  Mirroring the established flow is not speculation (hard rule 3).
- **Reach for what exists before writing new**, in this order: a helper or component
  the repo already has, a standard-library or platform feature (`structuredClone`, a
  native `<input type="date">`), a dependency already installed, and only then the
  minimum new code.
- **Clean up your own orphans — and only yours:** remove the imports, variables,
  and functions that YOUR change made unused. Pre-existing dead code stays in an
  unrelated diff — flag it for a separate pass under the deletion discipline
  below rather than bundling its removal.
- **Scope litmus: every changed line traces directly to the request.** A line you
  can't tie to the task belongs in a separate commit or not in the diff at all.
- **Scope discipline:** a quality pass is behavior-preserving. If a cleanup
  changes behavior, surface it separately rather than smuggling it in.
- **Change sizing:** ~100 changed lines is good, ~300 acceptable for one logical
  change, ~1000 split it — stacked, by file group, horizontal (shared code first),
  or vertical slices. Whole-file deletions and automated refactors are exempt;
  there the reviewer checks intent.
- **Rule of 500:** a refactor touching >500 lines warrants a codemod, not hand edits.

### When a refactor is worth it

Propose the named move, not just the problem — and apply one test: **does this
reduce complexity or merely relocate it?** Count the concepts a reader must hold,
prefer the version where branches *disappear*, and prefer deleting a mechanism to
polishing it. Making a type boundary explicit so downstream branching vanishes
is usually the highest-value move available.

**The over-simplification traps** (these are the non-obvious half, and why
`/simplify` needs judgment rather than a rule):

- Inlining a helper that **named a concept** makes every call site worse.
- Merging two simple functions into one complex one is not simpler.
- Some abstractions exist for extensibility or testability — stripping them is a
  regression, not a cleanup. **Fewer lines ≠ simpler.**
- Dropping a stage the rest of the codebase has (hard rule 3) is not a
  simplification; it starts a second rhythm.
- Litmus: would a junior engineer understand this faster than the original?

**Don't simplify** code you don't yet understand, code that is already clean,
performance-critical code where the simpler form is measurably slower, or a module
about to be rewritten.

## Module design: depth and seams

Hard rule 1 sizes a *file*; these size a *module* — what sits behind an interface and
where that interface is cut. A **deep** module hides a lot of behaviour behind a small
interface; a **shallow** one makes callers learn nearly as much as it does.

- **The deletion test.** Imagine inlining the module into its callers. If the total
  complexity drops, it was a pass-through; if it rises, it was earning its keep.
- **One adapter is a hypothetical seam; two adapters is a real one.** An interface with
  a single implementation (and no second in sight — a test fake counts) is speculative
  mechanism; inline it until the second one arrives.
- **The interface is the test surface.** If the behaviour that matters can only be
  tested by reaching past the interface, the cut is in the wrong place — move the seam
  rather than the test.
- **Replace, don't layer.** When interface-level tests cover a deepened module, delete
  the old tests of the shallow pieces it absorbed; keeping both doubles the cost of
  every later change.
- **A new module's interface is designed twice** — see
  [planning](../planning/SKILL.md) *Design it twice*.

## Reviewing a diff

Your own before commit, a delegated agent's, or a colleague's — the same pass.

- **Pin the fixed point first.** Confirm the base resolves (`git rev-parse <base>`),
  review the three-dot diff (`git diff <base>...HEAD`, which compares against the
  merge base, so commits that landed on the base meanwhile are not counted as yours),
  and check it is non-empty before reading anything.
- **Read the tests first** — they reveal intent and coverage before you read the
  implementation. Agent-written tests are where defects hide: read them at least as
  hard as the code. A loosened assertion (an exact value turned into
  `toBeGreaterThanOrEqual`, `toBeDefined`) is a finding, and an `as` cast is a
  contract change dodged. Settle a doubtful assertion by mutating the subject — see
  [tdd-skill](../tdd-skill/SKILL.md)'s mutation rails.
- **The hard rules, file by file:** one responsibility per file, the flow mirrors
  its nearest sibling, a junior could follow it.
- **"Additive" is a property of the diff, not of the behavior.** A new entry in a
  shared map, registry or enum changes every rule keyed off it: grep every read and
  enumerate the branches it feeds. A new field threaded through a payload: list
  every early return between entry and write, and check every falsiness guard
  (`x || undefined`, `if (x)`) still lets an empty value be saved. (A cross-skill
  principles file, if you keep one: *Giving existing code a NEW INPUT is an
  interface change*.)
- **Before approving a new shared abstraction or contract change,** grep the
  existing contract and its consumers for a flag or branch that already covers the
  case — and read the type's own comments.
- **A behavior change carries its prose.** Grep for docs, API descriptions and
  comments describing the old behavior and update them in the same change.
- **Error paths:** keep only the fallible call inside a `try` (a validation `throw`
  inside it is caught by its own `catch`); normalise error payloads to one shape at
  the boundary; a shared helper's fallback text stays generic; and no error path may
  render nothing.
- **Allow-lists over user input** use a `Map`/`Set` or `Object.hasOwn` — an object
  literal inherits `constructor`, `toString` and `__proto__`.
- **A green run proves only what it ran.** A test runner that transpiles without
  type-checking is not a type-check; run the full suite, not the touched specs; read
  a linter's file count, not just its error count (an unquoted `**` in a shell-run
  script lints one directory level). (A cross-skill principles file, if you keep one:
  *A green suite covers only the defect classes its environment can represent*.)
- **A finding is a property of the code in front of you.** Cross-repo merge order
  and release sequencing are not findings; how the code behaves when a dependency is
  missing is.
- **A special case bolted onto a busy flow is Required.** A one-off boolean, nullable
  mode or special-case branch added to an existing shared path, or one feature check
  scattered across shared code, belongs behind its own seam. So does an `any`, a cast
  or a silent fallback that exists only to quiet the compiler: it hides an invariant
  the types should state.
- **Type the invariant.** A `switch` over a union or enum ends in an exhaustive
  `never` check (or the repo's exhaustiveness lint), so a new variant fails to
  compile until it is handled. Prefer a discriminated union to a bag of optional
  fields, and parse external data once, at the boundary.
- **Name the devex break.** A changed secret source, a renamed or new env var, a
  remapped port or a newly required script is a Required finding that names the
  migration step. For flag-gated work, confirm the flag-off path is unchanged and grep
  the new symbol for use on ungated paths.
- **Independent async work runs concurrently; a multi-step update cannot half-apply.**
  Flag needlessly sequential awaits, and a write sequence that leaves state
  inconsistent when a middle step fails, where the clean shape is obvious.
- **Name the one fact the change is safe because of,** then prove it by running
  something (a test that fails without it, a repro, a query) or report it as
  unproven. The rungs, weakest first: said so, pointed at the line, showed the bad case
  cannot occur, ran it, reproduced it in the running app.

### The spec pass — the second axis

Everything above asks *is this good code?* The spec pass asks *is this the change
that was asked for?* — a different question that a standards review never answers.

1. **Find the spec**, in this order: a ticket key in the branch name or commit
   messages (fetch it and its acceptance criteria), a path the brief or plan names,
   the plan file under `plans/`, then ask. Never review against your memory of it.
2. **List three things, quoting the spec line for each:** requirements that are
   missing or only partly met; changes nobody asked for (scope creep, even when they
   are good); and requirements that *look* done but are wrong — the right field, the
   wrong rule.
3. **Keep the two axes in separate lists.** Do not merge or re-rank spec findings
   into standards findings: a clean diff that builds the wrong thing must not read as
   a minor note under a long list of nits.

The session that wrote the change is anchored on its own plan and carries the most
context pressure; a reader with only the spec and the diff has neither. On a
high-risk PR (auth, untrusted input, money, a shared contract), or after a long
implementation session, hand the spec pass to a sub-agent briefed with exactly those
two inputs.

## Dead code: prove it first

Removing code is governed by [dead-code.md](dead-code.md) — read it before deleting
anything your own change didn't orphan, and whenever asked to "remove dead code". The
short form:

- "Dead" means unreachable through ANY path. Rule out public API, string dispatch,
  reflection, framework wiring, serialization, build flags, lifecycle hooks,
  deliberate stubs and test-only use before calling anything dead.
- Tools give candidates, never verdicts; calibrate your search on a symbol you know
  is used.
- Prefer the smallest cut (drop the `export` before the symbol); when you can't
  prove it, flag it — don't delete it.
- Deletions get their own commit, with the evidence attached.

## Verify a flagged issue before acting on it

Whether a finding comes from a tool, a review subagent, another reviewer, or your own first
read — **confirm it against the exact code before you change anything.** Automated and AI
reviewers over-report; acting blindly churns or breaks correct code.

- **Do your own pass before reading other reviewers.** Read bot and colleague comments
  after your audit, so they cannot anchor it; then fold in the ones you confirm, with
  attribution. Don't report a hazard the branch introduces on purpose unless its author
  is likely underweighting it.
- **Read the precise code path** the finding names. Many "bugs" dissolve on reading (the
  framework already does the thing, the value is already neutralized upstream, the branch is
  unreachable).
- **For any runtime/DB/ORM/serialization claim, confirm empirically, not from memory of how the
  framework "should" behave.** Print the generated SQL, run a rolled-back transaction, write a
  10-line throwaway script, or repro the path. Empirical proof is cheaper and more certain than
  arguing internals.
- **Blast-radius grep before "fixing" a shared convention.** If the flagged pattern is the
  house convention across many call sites, a local "fix" is a behavior change across all of
  them — surface it as a decision, don't smuggle it into a cleanup.
- **Scope the fix to the real defect.** Reading the exact code often shrinks a fix from a wide
  signature change to a one-line clamp (and sometimes proves there's nothing to fix).
- **Budget for a third of your first-pass findings to be wrong.** For each candidate, name the
  one file read or command that would disprove it, and run it before writing the finding down.
- Then stack the **verified** fixes as small, concern-scoped commits/PRs.

## Fix at the right layer, at the right scope

- **The same bug twice means the fix is at the wrong LAYER.** A second instance of a bug
  you already fixed is not bad luck and not a missed case — it is evidence the first fix
  sat above the level where the defect actually lives. Before patching instance two, go
  find the layer where one change covers both.
- **A bug's blast radius is a scope decision, not a technical one.** How far a fix should
  reach — this call site, this module, every consumer — is a judgment about risk and
  ownership that belongs to the person who owns the change, not something the stack trace
  decides. Surface it as a choice rather than quietly picking the widest or narrowest.
- **Review the FIX as adversarially as the original code.** Patches reintroduce their own
  bug class: the author is now reasoning about a narrow, freshly-understood slice and is at
  their least suspicious. A fix deserves the same "how does this break?" pass the defect
  got.
- **Before calling code "too clever," find out WHAT FORCES IT.** Non-obvious code is
  sometimes load-bearing — a workaround for a framework bug, an ordering constraint, a
  performance floor. Simplifying without finding the forcing constraint reintroduces the
  problem the cleverness was solving. If nothing forces it, then simplify.
- **Extract the shared base rather than re-declaring the fields** when two types drift
  into near-duplicates; and **don't make one function serve two registers** — a label
  helper stretched to cover two audiences reads wrong in both.

## Reporting review findings

- **Two axes, two lists:** standards findings and spec findings (above) are reported
  under their own headings.
- **Label every finding by severity:** **Critical** (blocks — security, data
  loss, broken functionality) / *(no prefix)* = Required — including any break of
  a hard rule / **Optional/Consider** (worth doing, not required) / **Nit** (author
  may ignore) / **FYI**. Without labels authors treat all feedback as mandatory.
- **Lead by leverage:** correctness & security first, then hard-rule breaks and
  structural regressions, then missed simplifications, then the rest. A few
  high-conviction comments beat a long list — if you have one structural problem and
  ten nits, the structural problem IS the review.
- **Approve when the change definitely improves overall code health**, even if
  imperfect; don't block because it isn't how you'd have written it. Exit: all
  Critical resolved; every Required resolved or explicitly deferred with a filed
  follow-up (per the open-followups habit — no deferred cleanup without one).

## Posting a review to a PR on the user's behalf

Adopted 2026-09-04 from a real PR review, where a long top-level comment was
rewritten into inline threads over three rounds. The findings did not change; the
delivery did, and it came out roughly a third the length. (The originating PR:
`LOCAL.md` beside this skill, when your copy keeps one — *Posting reviews: the
originating PR*.)

- **Anchor every finding as an inline comment on the lines it concerns**, not as
  one top-level essay. `start_line`/`line` + `side: RIGHT` against the head SHA.
  The anchor carries the file and line, so the comment carries only the problem —
  that alone removes most of the scaffolding a top-level review needs.
- **Comment only on what needs work.** No "fixed since last time" recap, no
  "checked and fine" inventory, no praise. When a prior review had blockers, one
  line in the review body saying they cleared is the whole allowance.
- **Only genuinely file-less items go in the review body** — missing ticket, plan
  doc not updated, a verification that spanned repos.
- **One to three sentences per comment.** Mechanism, then consequence, then the
  fix. No bullet lists inside a comment, no hedging preamble.
- **Never change the review state unasked.** Post with `event: COMMENT` so an
  existing CHANGES_REQUESTED (or a clean slate) stays as it is; changing it is
  the user's call, made explicitly.
- **Draft in-session and get approval before posting.** The user revises wording;
  posting happens on an explicit go, not on your read of "this looks ready."
- **Mechanically, run exactly this** (paths relative to this skill's directory), dry
  run first, then the approved post:

  ```sh
  bash scripts/post-review.sh <owner>/<repo> <pr> review.json          # validates, posts nothing
  bash scripts/post-review.sh <owner>/<repo> <pr> review.json --post   # after the user's explicit go
  ```

  `review.json` is `{"body": "…", "comments": [{"path", "line", "side"?, "start_line"?,
  "start_side"?, "body"}]}`. The review `body` is required and non-empty (a one-line
  summary is enough when every point is on a line), and any other key exits 2. The script checks every anchor lies inside one of the PR's
  diff hunks at the current head (GitHub rejects the WHOLE review with 422 when one
  line is outside them), sets `commit_id`, refuses any `event` but `COMMENT`, posts
  once, and reads the comments back. Exit 0 ok, 2 bad input, 3 an anchor outside the
  diff, or in a file GitHub returns without a patch (binary or too large) (every one
  listed; nothing posted), 4 `jq` or `gh` missing, 5 a GitHub call
  failed or the head moved (never retried: a retry can double-post), 6 posted but
  fewer comments read back. Still confirm each anchor's wording against the code
  (`git show <ref>:<path> | sed -n '<a>,<b>p'`): the script proves the line is in the
  diff, not that it is the line you meant.
- **Verify across repo boundaries before asserting or asking.** On that PR an open
  question ("does the sibling service validate the hash?") and a standing nit both
  dissolved once the sibling repo was actually read. A question you could have
  answered yourself costs the author a round-trip; see a cross-skill principles
  file, if you keep one, on unverified claims reaching people other than the user.

## Dependency upgrades

- **Pre-add gate:** does the existing stack already solve it / size / maintenance
  / audit / license.

## Before you call this done

- Every changed file meets the three hard rules, or the exception is stated.
- Every deletion has evidence attached (where you searched, what you ruled out) —
  not just a tool's say-so.
- Anything you couldn't prove dead is flagged, not deleted.
- Build + tests + lint are green, and you exercised (or live-booted) any path
  whose use could be dynamic.
- Deletions sit in their own commit, separate from quality refactors.
- No behavior changed — or the behavior change is called out explicitly.
- New durable traps/conventions from this pass are captured in `LEARNINGS.md`
  beside this skill, when your copy keeps one.

## Related skills

- [deprecation-and-migration](../deprecation-and-migration/SKILL.md): removing something that still has consumers is a migration, not a cleanup.
- [security-and-hardening](../security-and-hardening/SKILL.md): its dependency-intake checklist runs alongside the pre-add gate here.
- [tdd-skill](../tdd-skill/SKILL.md): mutation rails for settling whether a test's assertion actually catches anything.
- [frontend](../frontend/SKILL.md): how a screen's components, state and data access are structured — the layers hard rule 1 splits along.

## Capturing learnings (session-handoff protocol)

Accumulate durable, project-specific quality knowledge in `LEARNINGS.md` beside this
skill, when your copy keeps one. Read it before quality or dead-code work.

<!-- Module-design tests, the fixed-point pre-flight and the separate spec axis are adapted from mattpocock/skills `codebase-design` and `code-review` (MIT, (c) 2026 Matt Pocock); the deep-module idea is John Ousterhout's, A Philosophy of Software Design. "Reach for what exists" adapted 2026-10-17 from `DietrichGebert/ponytail` (MIT). "No speculative mechanism", "Clean up your own orphans" and "Scope litmus" adapted 2026-08-27 from the Karpathy-derived `CLAUDE.md` template, `multica-ai/andrej-karpathy-skills`. The five review bullets from "A special case bolted onto a busy flow" through "Name the one fact" adapted 2026-10-17 from cursor/plugins' `thermo-nuclear-code-quality-review` and pstack's `blast-radius` (both MIT). -->
