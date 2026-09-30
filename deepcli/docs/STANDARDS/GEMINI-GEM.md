# Gemini Gem — positive-language

## Purpose

Rewrite an entire repository — code comments, commit messages, PR bodies,
issues, docs, and agent prompts — into affirmative directive syntax as
specified in `DO-FRAMEWORK.md`.

## Scope

- Input: any repo path or full repo.
- Output: rewritten files, one PR per pass.
- Contract: read `docs/STANDARDS/DO-FRAMEWORK.md` first; conform to §2 and §3.

## Procedure

1. **DO** load `DO-FRAMEWORK.md` before touching content.
2. **DO** stage rewrites in a worktree branch named `do-framework/<scope>`.
3. **DO** open one PR per pass with title
   `chore(do-framework): rewrite <scope>`.
4. **DO** include the checklist from §5 in the PR body.
5. **DO** log the pass to `docs/STANDARDS/CHANGELOG.md`.

## Test set

- Every transformed sentence reads as an action.
- Every negation has an affirmative twin.
- `rg` count of banned patterns trends to 0.
- Existing tests pass unchanged.

## Integration

- CLI: `gemini-gem run positive-language --scope <path> --dry-run`
- Hook: `commit-msg` enforces §2 on new messages.
- Issue: linked from `DO-FRAMEWORK.md` §7.
