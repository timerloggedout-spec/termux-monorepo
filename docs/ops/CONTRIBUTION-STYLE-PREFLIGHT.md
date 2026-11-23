# Contribution Style Preflight

**Read this contract before implementation, drafting, or collaboration.** CI enforces these rules after a push, PR edit, issue/discussion event, or comment event. This preflight moves the same checks to the authoring stage.

## 1. Canonical sources

| Contract | Source |
|---|---|
| DO-first writing, CAVEMAN-6, chat, comments, commits, PRs, issues, reviews | [Repo-wide Linguist / Siglary Mandate](REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md) |
| Winning notation standard | [SIGLARY-STANDARD.md](../proposals/active/notation-sets/SIGLARY-STANDARD.md) |
| Registered notation and Shorthand Domains | [CAVEMAN-MICRO-DENSE-V2.md](../proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md) |
| CI implementation | [DO Statement Style workflow](../../.github/workflows/do-statement-style.yml) · [checker](../../scripts/ci/check_do_statement_style.py) |

Treat **Siglary** as the system name of record. Treat the Standard as the normative contract and the Notation Matrice as its live register. Apply owner-issued updates from those sources; keep new symbols and chords registered before use.

## 2. Authoring contract

Use the fixed statement frame:

`⌖scope → ▶action → ⊗constraint → ⤵output → ~state`

Apply CAVEMAN-6:

1. **Action first:** name the action, owner, object, condition, and evidence.
2. **One claim per line:** separate actions with different owners or acceptance tests.
3. **Concrete verbs:** INSPECT · ROUTE · IMPLEMENT · TEST · VERIFY · RE-FETCH · COMPARE · CLASSIFY · RECORD.
4. **Explicit state:** distinguish DESIGNED · COMMITTED · EXECUTED · VALIDATED · PROMOTED.
5. **Proof adjacent:** place the path, SHA, run, test, artifact, timestamp, or citation beside the claim.
6. **Safe compression:** remove repetition while preserving scope, exceptions, ownership, and acceptance criteria.

Lead with the intended action. Prefer affirmative operational controls such as REQUIRE, ENFORCE, REJECT, EXCLUDE, HOLD, and FAIL-CLOSED. Use `¬` when logical negation is essential. Preserve exact API names, code literals, quoted source text, compiler syntax, and error messages.

## 3. Siglary correctness

- Keep **OPERATORS**, **GLYPHS**, and **CHORDS** distinct.
- Use registered operators with their fixed meanings.
- Use registered glyphs within the issued set and glyph-cap rules.
- Resolve every chord inside its named Shorthand Domain.
- Expand any form whose meaning could be ambiguous or misleading; accuracy outranks compression.
- Keep `N∅` / `NOT_ESTABLISHED` in chat epistemics only; represent missing data with schema nulls.
- Place receipt references beside verdicts and state-change claims where the standard requires them.
- Preserve register boundaries, including the math-register proof condition for `≅`.

## 4. Surface-specific requirements

| Surface | Required shape |
|---|---|
| Code comments | State the invariant, intent, owner/context, and relevant boundary. |
| Commit subject | Use a scope prefix when useful, then an imperative action verb: `docs: publish contribution preflight`. |
| Commit body | State outcome, scope, evidence, and any remaining state. |
| PR title/body | Lead with objective and changed state; include evidence, risks, and next gate. |
| Issue title/body | State the requested outcome, scope, acceptance evidence, and owner. |
| Review/comment text | State the finding, evidence, impact, and requested corrective action. |
| Workflow directives | Separate admission, execution, validation, and promotion states. |
| Skills/instructions | State scope, sequence, evidence, approval boundary, and terminal states. |

## 5. Run preflight before publishing

Run the checker against the intended base before committing or posting:

```bash
python3 scripts/ci/check_do_statement_style.py --preflight --base origin/master
```

For a comment, review, or other draft, save the exact text to a temporary file and include it:

```bash
python3 scripts/ci/check_do_statement_style.py \
  --preflight --base origin/master --text-file /tmp/collaboration-draft.md
```

Select `origin/master-staging` when the active contribution lane targets `master-staging`. The checker includes untracked instruction files automatically.

## 6. CI coverage and response

The `DO Statement Style` workflow checks:

- added lines in changed collaborator instructions, skills, workflow directives, and operations/proposal documentation;
- non-merge commit subjects and bodies in the pushed or proposed range;
- PR titles and bodies;
- issue and discussion titles and bodies;
- issue, PR review, and discussion comments.

Run preflight before authoring and again before publishing. Treat CI as the final independent verifier. On a finding, rewrite the affected line as a concrete DO action, retain the exact technical meaning, rerun preflight, and publish after PASS.

**Acceptance:** every contributor can discover the winning Siglary standard before work; every authored collaboration surface follows DO-first CAVEMAN-6; local preflight and CI evaluate the same rule set.
