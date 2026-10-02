---
name: recon-first-worktree-discipline
description: RECON-before-action doctrine for the Termux-monorepo. Codifies worktree management, safety-preserving writes, pipeline-not-one-offs, credential hygiene, and preservation-of-work invariants. Every action on a shared ref, tracked file, or live service must pass through this skill.
version: 1.0.0
---

# RECON-FIRST WORKTREE DISCIPLINE

## Prime directive

**Nothing is deleted. Nothing is overwritten. Nothing is assumed.**

Every mutation to a shared ref, tracked file, live service, or
memory bank is preceded by RECON. RECON is not optional and it is
not a formality. It is the difference between a working session
and a recovery session.

---

## 1 - RECON (read before you touch)

Before ANY of the following actions, RECON is mandatory:

- git push (any form, any branch)
- git branch -f, git reset, git rebase, git checkout
- Editing a tracked file
- Running a script that mutates Postgres, Hindsight, or the codespace
- Renaming anything (files, banks, branches, variables)
- Restarting any service

### RECON checklist

    [ ] What is on disk right now?            ls, find, git status
    [ ] What is on the remote right now?      git fetch, git log origin/<ref>
    [ ] Who else is using this ref?           git worktree list, gh pr list
    [ ] What did the last 5 commits do?       git log --oneline -5
    [ ] Is there uncommitted work-in-flight that a push would clobber?
    [ ] Does the target already exist?        grep, ls, gh api
    [ ] Is the API/DB reachable and what does it say right now?
    [ ] What process is writing to this?      pgrep, /proc/<pid>/environ

If any answer is unknown, RECON is not finished. Do not proceed.

### Live data beats memory

When a question can be answered by an API call, a database query,
or a gh api response - make the call. Never say "likely," "should
be," or "probably" when a 200ms query resolves it.

    BAD:  "The token probably has the user scope."
    GOOD: curl -sSI -H "Authorization: token $t" \
            https://api.github.com/user | grep x-oauth-scopes

---

## 2 - WORKTREE DISCIPLINE (never mutate shared refs directly)

~/ is the main worktree. It is shared. Do not:

- run destructive git ops in ~/
- git checkout between long-lived branches
- git branch -f anything you did not create this session
- git push -f any ref, ever, unless you created it in this session
  and checked git log origin/<ref> ^HEAD is empty

### For any multi-file change: worktree

    ~/.deepcli/worktrees/<safe-branch-name>/

Created via:

    git worktree add ~/.deepcli/worktrees/<branch> -b <branch> origin/<base>
    cd ~/.deepcli/worktrees/<branch>
    # edit, commit, push, PR
    cd ~ && git worktree remove ~/.deepcli/worktrees/<branch>

### Force-push rule

    FORBIDDEN:  git push -f origin <any-ref>
    ALLOWED:    git push --force-with-lease origin <ref-you-created-this-session>
    ALLOWED:    git push origin HEAD:<ref-you-created-this-session>

If the target ref has commits you do not recognize: stop, do not
push, investigate. If you cannot fast-forward, you must not push
at all until the divergence is understood.

---

## 3 - PRESERVATION OF WORK (nothing is deleted)

Before deleting, moving, or renaming:

- Copy current state to .bak.<unix-ts> alongside the original
- Or stash / worktree / archive it
- Or, if it is data: export it, snapshot it, commit it

### Service restarts

Capture /proc/<pid>/environ before kill. Restore on start.

### Codespace retirement

Never gh codespace delete without:

1. hs-codespace-retire (ships uncommitted state to a branch)
2. hindsight-admin export-bank for every bank
3. Verify the archive on disk before delete
4. Only then gh codespace delete --force

---

## 4 - PIPELINE, NOT ONE-OFFS

If the user asks to fix a pipeline, edit the pipeline. Do not
manually extract the artifact the pipeline was supposed to produce.

    BAD:  user asks to fix session export -> assistant greps session
          files for the target artifact and dumps it manually
    GOOD: user asks to fix session export -> assistant finds the export
          stage, patches it, runs it once end-to-end, verifies output

Pipeline layers (know which one you are editing):

    session store -> export -> harvest -> index -> query
        TUI        synthegration  harvest.py  forensic_  synthegration
                   export        code_blocks toolchain  search

Each layer has one job. Editing the wrong layer is the most common
mistake.

---

## 5 - CREDENTIAL HYGIENE

Never print tokens, keys, passwords, or passphrases.

    FORBIDDEN:  gh auth status --show-token
    FORBIDDEN:  cat ~/.gnupg/.2fa-pass
    FORBIDDEN:  env | grep -i key
    ALLOWED:    gh auth status                              # no token shown
    ALLOWED:    printf 'len=%d prefix=%.8s...' "${#TOK}" "$TOK"

If a token leaks to scrollback:

1. Log the rotation in ~/.deepcli/logs/hygiene/key-rotation.jsonl
2. Notify the user in the same turn
3. Do not repeat the operation that leaked it

---

## 6 - LIVE SERVICE HANDLING

### Codespaces

    gh codespace view -c <name> --json state                # always first
    gh codespace start <name>                               # positional, no -c
    gh codespace ssh -c <name>                              # -c required
    gh codespace cp -c <name>                               # -c required

Billing math: the REST API cpus field is authoritative, not
gh codespace list --json machineName. Core-hours = wall_hours x
cpus. Storage = disk_gb x wall_hours / 720.

The 402 "billing issue" means one of:

1. Core-hours exhausted
2. Storage exhausted
3. No budget in Settings > Billing > Budgets
4. Payment method invalid

Never wait 29 days without checking the budget first.

### Hindsight banks

    # live read
    curl -sS -H "Authorization: Bearer $KEY" $URL/v1/default/banks

    # bank rename: DROP FKs first, then update every table with a
    # bank_id column, then DELETE. Never UPDATE banks.bank_id (PK conflict)

memory_units.text is the fact body. memory_units.context is jsonb
wrapper metadata. Read COALESCE(nullif(text,''), context::text).

---

## 7 - SESSION AND EXPORT HANDLING

    session store -> synthegration export -> harvest.py -> forensic_toolchain -> search

Never hand-roll a regex to search sessions. Use layer 3 or 4.
Never modify harvest.py to look at a different shape. If the
harvest misses content, the bug is upstream.

---

## 8 - RESPONSE STYLE

- Match the user's energy. Terse when terse.
- One block per response, not five.
- Never say "likely" / "probably" / "should be" when a query is available.
- Own mistakes directly. No hedging, no defense.
- Never claim a task is done before verifying it in the same block.
- If a task cannot be completed, name the blocker, name the path, stop.

---

## 9 - COMMIT AND PUSH DISCIPLINE

    cd ~ && git fetch origin <branch>
    git log --oneline origin/<branch> ^HEAD    # anything new upstream?
    # if yes: git pull --rebase origin <branch>
    # if no:  git push origin HEAD:<branch>

Commit messages: Conventional Commits. Subject, blank line, body
naming: what changed, why, what it preserves.

Never --amend a pushed commit. Never --no-verify. Never commit secrets.

---

## 10 - WHEN IN DOUBT

Stop. Report state. Ask. The cost of a question is one turn. The
cost of a wrong push is a lost collaborator's session, a leaked
token, a deleted bank, or an unrecoverable loss of data. This repo
has already paid that cost three times. The doctrine exists so it
does not pay it a fourth.

---

## Quick reference

| Situation | Do |
|---|---|
| About to push | git fetch + git log origin/<ref> ^HEAD |
| Editing a shared file | .bak.<ts> first |
| Multi-file change | worktree |
| Single-file surgical | gh_edit_file |
| Renaming a bank | FK drop -> update children -> DELETE old row |
| Service restart | capture /proc/<pid>/environ first |
| Codespace retire | export banks -> archive -> delete |
| Token in env | never echo; mask as len=N prefix=xx... |
| Pipeline "looks stale" | read every stage, fix the stage that failed |
| Two options, unsure | pick the one that preserves state |
| Asked to "just do X" | RECON first, then X, verifying each step |
