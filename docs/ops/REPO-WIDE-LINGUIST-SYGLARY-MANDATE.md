# 🎗️ Repo-wide DO-first Linguist / Siglary Mandate

**CHAT := STATE-CHANGE ∨ OVERSIGHT**
**STYLE := DO-FIRST ∧ CAVEMAN-6 ∧ SIGLARY++**
**OBJECTIVE := MAX(signal / token) ∧ precision ∧ actionability ∧ evidence**

## Scope

Apply this contract to project chat, repository documentation, code comments, commit messages, PRs, issues, review comments, workflow directives, agent prompts, and skills. Keep chat to necessary state changes and oversight. Rephrase authored sections as direct DO statements. Lead with concrete verbs, explicit actors, observable outcomes, and measurable acceptance conditions.

Use affirmative construction by default. Replace vague negative phrasing with a positive control:

| Avoid | DO-first form |
|---|---|
| “Don't use unauthenticated fetch.” | “Require authenticated fetch; reject unauthenticated requests.” |
| “No duplicate jobs.” | “Enforce one active job per key.” |
| “Not validated.” | “Validation state: PENDING.” |
| “Don't merge yet.” | “Hold promotion until every required gate passes.” |

Use `¬` when logical negation is semantically essential. Preserve exact API names, quoted source text, compiler syntax, error messages, and required legal or operational wording. Prefer `REQUIRE`, `ENFORCE`, `REJECT`, `EXCLUDE`, `HOLD`, and `FAIL-CLOSED` for operational controls.

## CAVEMAN-6 contract

1. **Action first:** `DO → owner → object → condition → evidence`.
2. **One claim per line:** split actions when owners or acceptance tests differ.
3. **Concrete verbs:** INSPECT · ROUTE · IMPLEMENT · TEST · VERIFY · RE-FETCH · COMPARE · CLASSIFY · RECORD.
4. **Explicit state:** distinguish DESIGNED · COMMITTED · EXECUTED · VALIDATED · PROMOTED.
5. **Proof adjacent:** include path, SHA, run, test, artifact, timestamp, or citation where available.
6. **Safe compression:** remove fluff and repetition while preserving scope, exceptions, ownership, and acceptance criteria.

## Chat protocol

`CHAT := STATE-CHANGE ∨ OVERSIGHT`

- State change: report a material delta, decision, blocker, or requested action.
- Oversight: inspect, compare, classify, verify, and record evidence.
- Surface decisions, risk, proof, and the next gate.
- Distinguish observation, inference, and authorization.
- Preserve approval boundaries for destructive, irreversible, production, credential, privacy-sensitive, or external-message actions.

## Siglary notation classes

Follow the canonical [Siglary Standard](../proposals/active/notation-sets/SIGLARY-STANDARD.md) and [Notation Matrice](../proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md). Keep **OPERATORS**, **GLYPHS**, and **CHORDS** distinct. Resolve every chord inside a named Shorthand Domain. Use only registered symbols in enforced surfaces.

| Operator | Meaning |
|---|---|
| `∧` | AND |
| `∨` | OR |
| `¬` | NOT |
| `⇒` | implies |
| `⇔` | iff / logical equivalence |
| `∀` / `∃` | for all / exists |
| `∅` | empty set |
| `∈` / `∉` | member / non-member |
| `∆` | change / delta |
| `≡` / `≅` | identity-equivalent / conforming (register-specific) |
| `≠` | unequal |
| `≤` / `≥` | upper / lower bound |
| `⊕` / `⊗` | combine / constrained combine |
| `↳` | child / derivation relation |
| `∴` / `∵` | therefore / because |
| `⊢` / `⊬` | entails / fails to establish |
| `⊥` | contradiction / invalid state |
| `⏸` / `▶` | hold / execute |
| `✓` / `✗` | pass / fail |

`⤴` remains the registered **dispatch GLYPH**, not an operator. Use `∆` as the canonical delta operator.

## Directive grammar

`DO <VERB> <OBJECT> ∧ <SCOPE> ⇒ <EXPECTED STATE> · EVIDENCE=<SOURCE>`

- `DO AUTHENTICATE GitLab fetch ∧ use GITLAB_TOKEN ⇒ authenticated transport · EVIDENCE=workflow run`
- `DO ENFORCE single-writer lease ∧ key=(repo, PR, revision) ⇒ active_owner_count ≤ 1`
- `DO RE-FETCH canonical master ∧ compare manifest SHA ⇒ classify ∆ ∧ record receipt`
- `DO HOLD promotion ⇔ required checks ∧ review gates ✓`
- `DO ROUTE chat ⤴ oversight ∧ state-change; dispatch execution to its authorized lane`

## Repository conventions

- **Comments:** state the invariant, intent, and relevant boundary.
- **Commits:** use imperative subjects; state outcome and scope.
- **PRs/issues:** lead with objective, changed state, evidence, risks, and next gate.
- **Workflows:** encode admission, execution, validation, and promotion separately.
- **Skills:** specify scope, sequence, evidence, approval boundary, and terminal states.
- **Metrics:** preserve raw observations, provider/version, derived value, and confidence.
- **Reviews:** separate verified facts, candidates, unknowns, and rejected hypotheses.

## Quality gate

- [ ] DO-first wording and concrete verbs
- [ ] Scope, owner, condition, and expected state are explicit
- [ ] Essential negation uses `¬` or a precise control verb
- [ ] Technical literals and quoted evidence remain exact
- [ ] Claims carry evidence or an explicit PENDING / UNVERIFIED state
- [ ] Chat content changes state or provides oversight
- [ ] OPERATORS / GLYPHS / CHORDS remain class-correct
- [ ] Chords resolve in a named domain
- [ ] N∅ remains chat-only; data records use schema nulls
- [ ] Signal stays high; repetition and ceremony removed

**Canonical reminder:** `DO the necessary action · prove the resulting state · record ∆ · repeat when evidence changes the next action.`
