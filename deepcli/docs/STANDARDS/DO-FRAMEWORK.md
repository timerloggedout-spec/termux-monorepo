# DO Framework — Affirmative Directive Doctrine

Status: **MANDATE**
Scope: entire repo — code, commit messages, PR bodies, issue text, docs, comments, agent prompts.
Authority: `docs/STANDARDS/` is the source of truth. `Gemini-Gem/positive-language` rewrites conform to this doc.

## 1 · Principle

State what **is done**, what **runs**, what **holds**. Every sentence describes
present capability or a specific next action. Affirmative directives.

## 2 · Rules

- **DO** lead with what works.
- **DO** name the executed action, the passing test, the green check.
- **DO** write commit subjects in imperative present: *add*, *ship*, *verify*.
- **DO** state the next move as the move itself.
- **DO** treat scan results as located artifacts, ready to remediate.
- **DO** prefer "Run X to Y" over "Don't do Z".
- **DO** attribute every artifact to (source_id, sha256, commit).
- **DO** keep the local bank current with every session_store write.
- **DO** dry-run before in-place edits.
- **DO** back up as `.bak.<ts>` before any mutation.
- **DO** call `git-rm-safe` for tracked files, `rm-safe --confirm` for local.
- **DO** issue one identity per collaborator; scope PATs; 90-day TTL.
- **DO** replay from Git — the repo is the durable source.

## 3 · Inverse constructions to eliminate

Each line names the pattern and its affirmative replacement.

| Replace | With |
|---|---|
| "no X" / "don't X" | "Run Y instead" / "Prefer X" |
| "cannot" / "won't work" | "Runs under condition Z" / "Choose path A" |
| "must not" | "Route to B" |
| "avoid X" | "Choose Y" |
| "never X" | "Always Y" |
| "fail" | "Retry via Z" / "Fallback to W" |
| "broken" | "Fix path: X" |
| "missing" | "Add via X" |

## 4 · Structure

Every doc, commit, PR, and issue uses this shape:

    Context → Action (imperative) → Verification → Next move

## 5 · Review checklist

- [ ] Every imperative is affirmative.
- [ ] Every negation has an affirmative twin.
- [ ] Every claim has evidence (path, hash, commit, or test).
- [ ] Every next move is actionable today.
- [ ] Every artifact is attributable.

## 6 · Refinement loop

This document is **reviseable**. Edits land via PR titled
`docs(DO-framework): <change>` and are logged in `docs/STANDARDS/CHANGELOG.md`.
The Gemini Gem `positive-language` reads this file before each rewrite pass.

## 7 · Connection

- Gemini Gem: `Gemini-Gem/positive-language` — see `docs/STANDARDS/GEMINI-GEM.md`
- Issue: `timerloggedout-spec/termux-monorepo` — *DO Framework roll-out across repo*
- Consumers: commit-msg hook, PR template, issue template, agent prompts.

## 8 · Verification

    rg -c '(don\'t|do not|no |never|avoid|cannot|won\'t)' docs/ STANDARDS/
    # target: 0 in framework-governed docs

Every affirmative claim is checkable: path, hash, commit, or test output.
