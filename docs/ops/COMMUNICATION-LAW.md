# Communication Law — DO-First / CAVEMAN-6 / Siglary

**Status:** binding communication standard for humans and agents across this repository.

## 1. Core contract

`CHAT := STATE-CHANGE ∨ OVERSIGHT`

Use chat for decisions, state transitions, routing, evidence, blockers, and oversight. Put implementation detail in tracked code, issues, PRs, and documentation.

`DO := ACTION + OWNER/SCOPE + CONDITION + EXPECTED_STATE`

Lead with affirmative, executable statements. Prefer direct verbs and explicit outcomes.

## 2. Message operators

| Operator | Required payload |
|---|---|
| `DO` | Action + owner/scope + condition + expected state |
| `ASSERT` | Evidence-backed state + source/reference |
| `ROUTE` | Recipient + role/scope key + destination |
| `RECORD` | Durable artifact + evidence pointer |
| `ESCALATE` | Trigger + authority + requested decision/action |
| `HOLD` | Gate + evidence required for release |
| `VERIFY` | Test/check + expected result + observed result |
| `DISPOSITION` | Finding + impact + action + acceptance condition |

## 3. CAVEMAN-6 and Siglary

Use compact language while preserving unambiguous meaning.

`∧` AND · `∨` OR · `¬` NOT · `⇒` implies · `⇔` iff · `∈` member · `∉` excluded · `∀` all · `∃` exists · `∅` empty · `Δ` change · `≈` approximate · `≡` equivalent · `≠` distinct · `≤/≥` bounds · `⊕` combine · `⊗` constrained combine · `⤴` route · `↳` child · `∴` therefore · `∵` because · `⊢` proven · `⊬` unproven · `⊥` invalid · `⏸` hold · `▶` execute · `✓` pass · `✗` fail.

Use symbols where they improve precision; pair unfamiliar notation with a short legend at first use in durable documents.

## 4. Surface-specific rules

### Chat
- Keep each message to a state change, oversight decision, evidence update, or one required clarification.
- Lead with the current state and the requested/approved next action.
- Route implementation detail to a repository artifact and cite its path or issue.
- Remove filler, ceremony, duplicate context, and status narration.

### Source comments
- Explain intent, invariant, boundary, trade-off, or non-obvious behavior.
- Put the reason beside the relevant code.
- Keep comments synchronized with behavior.
- Prefer names and structure over narration.
- Use TODO/FIXME only with owner or issue reference and a concrete completion condition.

### Commit subjects and bodies
- Use imperative, outcome-led subjects; target 50–72 characters.
- Keep one logical change per commit.
- Body records rationale, key behavior, validation, and linked issue/proposal.
- Include `Implements: TER-N` and proposal item IDs when applicable.
- Example: `docs: establish affirmative communication law`.

### PR titles, descriptions, and reviews
- Title states the delivered outcome.
- Description records scope, implementation, evidence, tests, risks, and linked work.
- Review comments use `DISPOSITION → evidence → impact → requested action → acceptance condition`.
- Separate verified facts, inference, and pending evidence.
- Use checklist items as executable acceptance criteria.

### Issues and stewardship reports
- State owner, priority, status, dependency, next action, and evidence pointer.
- Use explicit state verbs: `QUEUED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED`, `DONE`.
- Keep durable decisions in the issue/proposal/PR record.

## 5. Negation and exact semantics

Prefer affirmative construction. Use negation where exact technical meaning requires it: logical operators, security boundaries, prohibited operations, test assertions, quoted source text, and precise failure evidence. Preserve the truth conditions of contracts and diagnostics.

## 6. Enforcement

- Treat this document as the canonical standard.
- Agent instructions and contributor guidance link here.
- PR template requires a communication-law self-review.
- Reviewers assess comments, commit messages, PR text, and issue updates against this standard.
- Improve violations by rewriting to action + evidence + outcome; preserve technical semantics.
- Apply the standard prospectively to new and edited content; migrate historical text when touched for substantive work.

## 7. Acceptance checklist

- [ ] Message leads with action/state/evidence.
- [ ] Scope, owner, and expected outcome are clear.
- [ ] Comments explain intent or invariant.
- [ ] Commit is imperative, focused, and issue-linked.
- [ ] PR/review text includes evidence and acceptance criteria.
- [ ] Notation is precise and locally legible.
- [ ] Negation preserves an exact technical requirement.
