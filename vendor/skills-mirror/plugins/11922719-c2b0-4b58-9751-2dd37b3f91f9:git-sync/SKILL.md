---
name: git-sync
category: Workflow
description: "The standing git workflow. Use at the start of any branch work and before every commit, push, rebase or PR: your own branch (never main), rebased on current main, every branch pushed, PR bodies in the standard shape, PRs reported only when green, and merged branches and worktrees pruned before a session ends.\n"
---

# Git Sync

Goal: keep git from getting tangled. Local and origin stay in lockstep, history
stays linear, and the working branch is always rebased on top of current main
(and any branch it depends on). Apply this on **any** branch work.

> **Who writes the code:** if implementation is delegated to another agent, git
> operations themselves stay with the orchestrating agent: branching, rebasing,
> committing, pushing, PRs, and merges are its job, and **no worker or delegate ever
> commits**. The delegate produces the diff; the orchestrator lands it. (Who executes
> in this install: `LOCAL.md` beside this skill, when your copy keeps one — *Who
> writes the code*.)

**Exclusion: `worktree-agent-*` branches** (temporary branches for isolated
worktree agents). Do NOT apply the *sync* workflow to them — no rebasing, no
pushing; they die with their worktree. They DO get pruned once orphaned: never
pushed means never `: gone]`, so only the "merged local-only" prune in the sweep
below catches them. Don't touch one whose worktree is still live (`-d` refuses
anyway — that's the guard).

Defaults chosen by the user (apply automatically, no pausing):

- **Fully autonomous** for rebase, force-push, and pruning merged local branches.
- **Force-push uses `--force-with-lease`** — never bare `--force`.
- **Rebase cadence:** onto fresh main when starting work on a branch, and again
  right before any push or PR.
- **Main is updated fetch-only** — never checked out (a shared working tree;
  checking out main yanks it from concurrent sessions).

## Hard gates (check before the first mutation, every session)

1. **Never commit on `main` or a shared branch.** Before any code change, create
   your own dedicated branch — a commit on main in a shared checkout is
   immediately visible to (and rebased under) every other session. If you find
   yourself on main with edits: `git switch -c <branch>` first, then commit.
2. **In a SHARED working tree, isolate in a worktree.** A main checkout used by
   concurrent sessions or agents can have its branch switched under you
   mid-task — committing there risks landing your work on someone else's branch.
   Do code work in a dedicated worktree on your own branch. If the project ships a
   one-shot worktree command, prefer it; it usually also copies the untracked
   env/config files a fresh worktree lacks. Manual equivalent:

   ```sh
   git worktree add -b <branch> ../<repo>-<slug> main
   cd ../<repo>-<slug>
   cp ../<repo>/.envrc . && direnv allow      # untracked env files do not come along
   cp ../<repo>/<untracked-local-config> <same-path>   # any gitignored config the app needs
   pnpm install        # a fresh worktree has NO node_modules
   ```

   The project's own one-shot command and its config-copy step: `LOCAL.md` beside
   this skill, when your copy keeps one — *Creating a worktree*.

3. **No AI attribution in commits or PRs.** Never append an AI-generated
   attribution line or AI `Co-Authored-By` trailer to commit messages or PR
   bodies — the user's standing rule, every project. Substantive content only.
4. **A PR isn't "up" until it's green.** After opening or pushing to a PR, poll
   the checks (`gh pr checks <n> --watch`) and only report/hand off the PR when
   all pass. A failure means fix and re-push, not announce. Caveat: in a repo
   whose CI path-filters them out, docs-only PRs (e.g. `plans/**`) trigger ZERO
   checks — "no checks reported" + `gh pr view <n> --json
   mergeable,mergeStateStatus` showing MERGEABLE/CLEAN counts as green; don't wait
   on a suite that will never start. (Which repos behave this way here: `LOCAL.md`
   beside this skill, when your copy keeps one — *Docs-only PRs trigger no
   checks*.)
   **Classify each red check before fixing it:** PR-caused, flaky or infra,
   unrelated (red on the base too), or needs a decision. Check the base before
   blaming the PR: if the same job is red on the base, or `git log <PR base
   sha>..origin/<base>` shows the cause landing there, it is not yours to fix in
   this PR. Rerun a flaky job once, only when `gh run view <id> --json attempt`
   says attempt 1 (`gh run rerun <id> --failed`); a second red is a real failure.
   (Adapted 2026-10-17 from PostHog's ci-shepherd.)

## Working inside a worktree

Creating the worktree is the easy half. Almost every recorded incident
happened *while operating in one* — because cwd, branch, and the worktree's
continued existence are all assumptions that quietly fail.

- **Never rely on cwd when more than one worktree exists — pass `git -C
  <abs-path>` explicitly, every time.** The harness resets cwd between calls, so a
  `cd` in one call does not hold for the next: a `git branch --show-current`
  "confirming" the branch was reporting a *different* checkout, and a
  `cd <main-checkout> && git rebase origin/main` meant to rebase a feature branch
  rebased **main** instead (harmless only by luck). Never `cd` into the shared main
  checkout to run branch operations.
- **Target the worktree's absolute path when editing, too** — edits and commits
  aimed at main-checkout paths land on `main`, not your branch.
- **Re-check the branch before any mutation** (`git rev-parse --abbrev-ref HEAD`).
  A worktree's branch can be silently flipped at session start, and a concurrent
  session can switch it under you mid-task.
- **A successor session taking your branch leaves YOUR worktree DETACHED.** A
  branch can be checked out in only one worktree, so the handover detaches yours —
  and `git status --short` reports **clean**, so nothing looks wrong. Check
  `git branch --show-current` (or `git status -sb`) in the sweep: "clean" and "on the
  right branch" are different claims. The work survives only because it was pushed —
  **push before handing a branch to another session.**
- **Your worktree may not survive the session.** It can be deleted externally
  mid-session, or claimed by a session you just spawned. Run `git worktree list`
  before any sweep and treat any worktree you did not just create as **occupied**.
- **A worktree whose `node_modules` is a symlink to the main checkout blocks
  `pnpm add`** — install from the root, or give the worktree its own install.

## The invariants

1. **main is always current** — update it without leaving your branch:

   ```sh
   git fetch origin main:main
   ```

   This fast-forwards the local `main` ref to `origin/main` without checkout.
   (If it errors — not fast-forwardable, or `refusing to fetch into branch
   'main' checked out at <path>` because a concurrent worktree holds main —
   just `git fetch origin` and rebase onto `origin/main` instead. Never force
   local main.)

2. **The working branch is rebased onto latest main** — at task start and before
   every push/PR:

   ```sh
   git fetch origin main:main
   git rebase main
   ```

3. **Branches that depend on another branch rebase onto that branch**, not main.
   Fetch the dependency first, then `git rebase <dependency-branch>`. When the
   dependency later merges to main, rebase back onto main and drop the dep —
   mechanics in [restacking-and-stacks.md](restacking-and-stacks.md).

4. **Branches stay pushed.** After committing, push. First push of a new branch:
   `git push -u origin <branch>`.

5. **Any history rewrite is force-pushed** — keep origin identical to local.
   After every rebase, amend, squash, or reword:

   ```sh
   git push --force-with-lease origin <branch>
   ```

6. **Prune local branches whose remote is gone.** Remotes are deleted on PR
   merge, so a missing upstream means merged-and-done:

   Run the auto-prune sweep under *End-of-work / handoff / archive sweep* below, exactly as
   written; it holds the only deletion commands. Only delete a branch you are not
   currently on; switch away first if needed.

## Procedure at a glance

**Starting work on a branch:**

```sh
git rev-parse --abbrev-ref HEAD          # confirm which branch you're on (gate 1)
git fetch origin main:main               # refresh main (no checkout)
git rebase main                          # (or rebase onto the dependency branch)
git push --force-with-lease origin HEAD  # only if the rebase moved commits
```

**Before any push or PR:**

```sh
git fetch origin main:main
git rebase main
# resolve conflicts if any, then:
git push --force-with-lease origin HEAD  # plain push if no rewrite happened
```

**When a base branch was amended/rebased/squash-merged, or you're running a
multi-PR stack:** read [restacking-and-stacks.md](restacking-and-stacks.md)
first — a plain rebase in those situations duplicates commits or conflicts
against rewritten twins.

**After a PR merges (cleanup) — remove the WORKTREE too, not just the branch.**
A merged PR's worktree is dead weight; leaving it is how orphaned worktrees pile
up. Clean as you go, the same session the PR merges:

```sh
git fetch --prune
git worktree remove <path-of-the-merged-branch's-worktree>   # if it had one; plain remove refuses if dirty
git worktree prune                        # drop admin refs for already-removed dirs
```

Then delete the branches with the auto-prune sweep below, never with a hand-typed
`git branch -D`: a branch with neither a `: gone]` upstream nor a `--merged` proof
has no evidence it landed, and `-D` deletes unmerged work without asking.

Worktree removal deletes a full `node_modules` (~30-60s on a 5.5k-file repo) — run
a multi-worktree removal in the background (see `LEARNINGS.md` beside this skill,
when your copy keeps one). Re-check `git status --porcelain` right before each
removal and let plain `git worktree remove` (never `--force` on unseen state)
refuse a dirty tree.

## The PR body

Every PR description has the same three parts, in this order:

1. **Summary — the smallest visual that makes the change clear.** Pseudocode of the
   new flow, a call tree, a file-tree diff, a before/after table, or a mermaid
   diagram; prose only for what the visual cannot carry. One or two sentences of
   *why*, and the ticket link.
2. **Evidence — before and after.** A screenshot or recording for UI; otherwise the
   exact command whose output was red before and green now (name the regression
   test). Every claim in the body is one you checked: colleagues read it as fact.
3. **Merge danger.** Two lines: `Door: one-way | two-way` and `Blast radius:
   <one word>` (none, module, service, data, users). Two-way means a plain revert
   fully undoes it. A one-way call names the checked fact that makes it so — a
   destructive migration, a published contract, a message sent, a branch that
   deploys on merge — and a one-way door gets an independent second review before
   merge.

Nothing else is required, and an AI attribution line is never allowed (hard gate 3).

<!-- PR body shape adapted from mattpocock/skills `pr` (MIT, (c) 2026 Matt Pocock). -->

## End-of-work / handoff / archive sweep (MANDATORY)

Cleanup is not "on request" — accumulation (dozens of `: gone]` branches, orphaned
worktrees) is the failure this skill exists to prevent. Run this sweep at the end
of a task, at every handoff, and before `archive_session`. Two tiers:

**Auto-prune the provably-safe set (no confirmation).** When your install ships the
sweep script (the *Automated backstop* below; `LOCAL.md` beside this skill names it,
when your copy keeps one), run exactly that for the current repo, dry run first, then
`--apply`: it implements every gate in this section, tested. The commands below are
the manual fallback for an install without it. Two categories of dead branch — both
must be swept, because they accumulate through different holes:

```sh
git fetch --prune
# (a) UPSTREAM-GONE: branches whose remote was deleted on merge. EXCEPT protected
#     long-lived names (a "[gone]" release branch can carry hundreds of commits) and
#     the checked-out branch (branch -D refuses branches held by a worktree — the guard).
git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads \
  | awk '$2=="[gone]"{print $1}' | grep -v '^worktree-agent-' \
  | grep -Ev '^(main|master|develop|trunk|release|staging.*|production.*|prod)$' \
  | while read -r b; do git branch -D "$b"; done
# (b) MERGED LOCAL-ONLY: branches with NO upstream that are fully merged into
#     the base — never-pushed feature branches AND orphaned worktree-agent-*
#     whose worktree was removed. --merged "$base" proves zero unmerged commits;
#     -d (not -D) double-checks and refuses anything not merged; a branch a live
#     worktree still holds is refused too. Both are the safety net, so this can't
#     eat unpushed work (an unpushed plan branch has commits ahead of base → excluded).
#     The base comes from origin/HEAD: a hardcoded origin/main silently skips this
#     clause in develop-based repos.
base=$(git symbolic-ref --short refs/remotes/origin/HEAD)   # e.g. origin/main
git branch --merged "$base" --format='%(refname:short) %(upstream)' \
  | awk -v b="${base#origin/}" '$1==b{next} $2==""{print $1}' \
  | while read -r b; do git branch -d "$b"; done
# remove CLEAN worktrees whose branch is merged (background; plain remove)
git worktree prune
```

Category (b) is the hole that let a pile of merged `worktree-agent-*` branches
survive: local-only (never pushed → never `: gone]`), and the old sweep skipped
them by name. `--merged origin/main` + `-d` makes deleting them provably safe.

**Sweep sessions too, not just branches.** When the session-mesh tools are
available (`ccd_session_mgmt`), a merged PR usually has a session that owned it:
`list_sessions` locates it by title/branch, `archive_session` retires it. Offer
the archive (report, don't silently archive) — a session that looks done may
still be holding follow-up state.

**Report, never auto-delete, the ambiguous set** — surface these for a human:

- **Dirty worktrees** (uncommitted changes) — could be another session mid-flight.
- **Local-only branches with no upstream** — verify merged first (`git rev-list
  --count origin/main..<branch>` == 0 means fully merged → safe; otherwise it holds
  unpushed work — flag, don't delete).
- **Branches with a live remote** (e.g. a shared `prod-hot-fix`) and known-KEEP
  branches (unpushed plans, re-land-pending rescue branches).

**Automated backstop.** Run the same sweep unattended: a session-end hook and a
weekly scheduled job (a launchd agent, cron, or similar) should both call **one
shared implementation** — a sweep script over a list of repos. It is a plain shell
job — the decision procedure is fully deterministic, so it needs no model in the
loop and costs no tokens. Make dry-run the default so anyone can see exactly what
it would do, any time, and require an explicit `--apply` to act; have the
scheduled run append to a log you can tail. (This install's hook and script paths,
launchd label, repo list and log: `LOCAL.md` beside this skill, when your copy
keeps one — *Automated sweep backstop*.)

```sh
# shape of the interface — dry-run is the default
bash <path>/sweep-worktrees.sh
bash <path>/sweep-worktrees.sh --apply      # act
tail -40 <log-dir>/sweep-worktrees.log      # what the weekly run did
```

🔑 A worktree PINS its branch — `git branch -D`
refuses a branch checked out anywhere — so declining to remove worktrees made
the branch prune a no-op for exactly the branches that mattered. The sweep
derives the base from `origin/HEAD`.

A worktree is removed only if EVERY gate passes; any gate that cannot be
evaluated resolves to KEEP: not the main checkout · not `--exclude`d · not
detached or unreadable · branch not protected · clean tree · no session transcript
touched within `--idle-hours` (24h default, read from
`~/.claude/projects/<slug>/*.jsonl` mtime) · tip older than `--min-age-days` ·
branch is `[gone]` or 0 ahead of base · no open PR. `--max N` caps removals per
repo (the session-end hook removes one at a time). Branches checked out in any
worktree, and branches matching the protected pattern
(`main|master|develop|trunk|release|staging.*|production.*|prod`, replaced
wholesale by a protected-list file of one ERE per line — this install's path is in
`LOCAL.md` beside this skill, when your copy keeps one), are never candidates, in
either the worktree phase or the branch phase.

⚠️ **`gh` failure must not mean "assume a PR exists."** The sweep
probes `gh repo view` once per repo: when gh can answer, the per-branch PR
check is authoritative; when it cannot, the PR gate is dropped and branch state
alone decides, which is already decisive (0-ahead means there are no unique
commits to lose).

## Safety rules / failure modes to catch yourself on

- **About to run a git mutation without checking the branch?** Stop —
  `git rev-parse --abbrev-ref HEAD` first. In a shared tree a concurrent session
  may have switched it under you.
- **Never force-push main or any shared/protected branch.** Force-push applies
  only to your own feature branch.
- **`--force-with-lease` rejection is a signal, not a nuisance.** Origin advanced
  under you — fetch, inspect, reconcile (rebase your work on top), then retry.
  Do not escalate to `--force`.
- **Linear history only.** Integrate with rebase, never merge commits. Don't
  create merge commits to "catch up" a branch — rebase it.
- **Don't delete unmerged work.** Prune only branches proven merged (`: gone]`,
  or `--merged origin/main`). A `gone` branch with unpushed local commits you
  don't recognize → stop and flag it rather than `-D`.
- **"Committed, not pushed" in a handoff note = a commit at GC risk.** At resume,
  `git branch -a --contains <sha>`; if nothing contains it, pin it immediately
  (`git branch rescue/<topic>-<sha7> <sha>`) before analyzing (see `LEARNINGS.md`
  beside this skill, when your copy keeps one).

### Commands that destroy uncommitted work

Three separate incidents, one shape: a git command doing exactly what it documents
while the caller expected an "undo".

- **`git checkout -- <file>` is not "undo my last edit".** It restores from
  HEAD/index, so using it to revert a temporary edit (a mutation, a debug print) on a
  file whose real work is **uncommitted** discards the entire slice in that file. It
  presented as a legitimate test failure — the specs were untouched, so the suite went
  red — and cost a full re-implementation. To undo a temporary edit, `cp` the file
  aside and `cp` it back. **Detection: after restoring, `git status` should STILL list
  the file as modified; if it went clean, you just deleted your work.** Structural
  fix: commit the slice *before* mutation-testing it, then amend.
- **`git reset --hard origin/main` assumes a clean tree.** The common slice cadence
  (`fetch && reset --hard` → commit on top) destroyed a finished, unpushed edit —
  same family as above with a wider blast radius: `checkout` takes one file, `reset
  --hard` takes the tree. Commit or stash first.
- **Never chain a push onto a rebase.** A conflicted rebase stops with HEAD
  **detached** while the branch ref still points at the **pre-rebase** commit — and a
  pipe between the two commands swallowed the exit status `&&` relied on, so the push
  ran and published the stale commit as a clean-looking `* [new branch]`. Rebase,
  verify, *then* push, as separate steps. Before any push, check for an in-progress
  rebase: `ls -d "$(git rev-parse --git-path rebase-merge)" 2>/dev/null` (plain
  `.git/rebase-merge` does **not** work in a worktree), and treat a literal `HEAD`
  from `rev-parse --abbrev-ref` as detached ⇒ do not push.
- **Stage explicit paths, never `git add -A`.** A `pnpm install --ignore-workspace`
  fabricated a nested lockfile and workspace file (~3.4k untracked, non-ignored lines)
  that `git add -A` staged without complaint, silently decoupling the package from the
  root workspace. Before committing, diff the staged list against the slice's intent
  (`git diff --cached --name-only | grep -E 'lock|workspace|\.claude'`);
  `git ls-tree origin/main <path>` answers "did my tooling create this?"

### In a rebase-merge repo, prove merged-ness by CONTENT, not ancestry

Rebase-merging rewrites every commit hash, so a merged branch's local tip and main's
copy are different objects with identical trees. Consequently:

- **`git merge-base --is-ancestor` says NO for branches that are fully merged**, and
  `git branch --merged origin/main` won't list them. Don't panic, and don't prune on
  that signal. Prove disposability with `git diff <tip> origin/main` being **empty**.
- **`git branch -d` succeeding is a weaker guarantee than it looks** — it means
  merged into its *upstream*, not into main. Verify, then delete.
- **A commit written AFTER the PR merged does not reach main.** It sits on the branch
  until some later PR carries it — check `git show origin/main:<file>` rather than
  assuming a push landed it. A quiet `git push -q` with tailed output hides this.
- Syncing after a rebase-merge: `git diff origin/main --stat` empty proves your work
  is fully upstream, making `reset --hard origin/main` + `push --force-with-lease`
  lossless — and gives the safety classifier the specific justification it demands.

### PR mechanics that mislead

- **`gh pr merge` from inside a worktree prints `fatal: 'main' is already used by
  worktree at …` — the MERGE still succeeded.** But verify **both halves
  independently**: `gh pr view <n> --json state` for the merge, and
  `git ls-remote --exit-code --heads origin <branch>` for the branch. ⚠️ gh's cleanup
  appears to abort as a unit, so `--delete-branch` may leave the **remote branch
  alive** — an earlier note claiming the remote delete still succeeds was wrong.
  Expect the manual `git push origin --delete` to be **blocked** by the safety
  classifier (merging a PR is not the user naming a branch deletion); that is correct
  — leave it, record a follow-up, and sweep merged branches in one authorized batch.
- **Never use `gh pr merge --auto` on a repo without required status checks** — it
  waits for nothing and merges instantly, silently bypassing merge-on-green. Run
  `gh pr checks --watch` to green, then merge explicitly. (A GraphQL "unstable status"
  error on the first attempt just means checks were still registering.)
- **When GitHub and a local dry-run disagree about conflicts, suspect a custom merge
  driver.** `.gitattributes` declaring `**/LEARNINGS.md merge=union` is honored by
  local git and **ignored by GitHub's server-side merge**, so concurrent journal
  appends show as CONFLICTING while `git merge-tree` reports clean. Resolve locally —
  rebase onto main (union applies during replay), `push --force-with-lease`, then
  merge. Never resolve in the GitHub UI.
- **A CONFLICTING PR gets NO CI runs**, which presents as "no checks reported" and is
  easily mistaken for a docs-only PR. After every rebase-merge, `git fetch && git
  rebase origin/main` before opening a follow-up PR from the same branch — duplicates
  drop automatically.
- **A rebase-merged PR's green CI can hide a lockfile broken by a sibling merge.**
  PR CI never re-runs post-rebase, so main can look green while every
  `pnpm install --frozen-lockfile` fails. When a lockfile-adjacent PR rebase-merges
  after any sibling that regenerated the lockfile, verify main immediately. Diagnosis
  handle: tag builds all failing in ~30s at "install dependencies" = lockfile drift on
  main, not a code problem.

## Before you call this done

- You are on your own dedicated branch (never main), in a worktree if the
  checkout is shared.
- The branch is rebased onto current main (or its dependency) and pushed;
  origin matches local after any rewrite.
- Commits are atomic, messages substantive, no AI attribution trailers.
- Any PR you opened/pushed is green (or provably has no checks) before you
  report it.
- The end-of-work sweep ran: safe set pruned, ambiguous set reported, merged
  worktrees removed.

## Capturing learnings (session-handoff protocol)

Append durable git workflow gotchas to `LEARNINGS.md` beside this skill, when your
copy keeps one — gh/CLI
failure modes, prune holes discovered, re-stacking traps — deduped and tagged
by repo. Read it before non-trivial git surgery (stacks, bulk prunes, recovery).
