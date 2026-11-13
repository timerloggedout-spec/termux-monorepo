# DO-Statement + Siglary Mandate

Status: repository-wide communication and contribution standard
Scope: chat, issue comments, PR descriptions, commit subjects, code comments, docstrings, operational documentation and agent instructions.

## Communication contract
- Write actions, state changes, ownership, evidence and next steps as affirmative DO statements.
- Lead with the actor and action: `QUE routes scoped work`, `CI validates the schema`, `Vercel serves the static UI`.
- Express constraints as positive gates: `Require approval before paid usage`.
- Express unavailable states as observed facts: `Origin status = offline; native validation = pending`.
- Express risk through required controls: `Keep credentials server-side`.
- Use concise CAVEMAN-6 phrasing and Siglary operators where meaning stays unambiguous.
- Keep chat focused on state-change ∨ oversight.
- Route execution through governed issues, PRs and workflows.

## Siglary operators
`∧` AND · `∨` OR · `¬` NOT · `⇒` implies · `⇔` iff · `∈` member · `∉` excluded · `∀` all · `∃` exists · `∅` none · `Δ` change · `≈` approximate · `≡` equivalent · `≠` unequal · `≤` / `≥` bounds · `⊕` combine · `⊗` constrained combine · `⤴` route · `↳` child · `∴` therefore · `∵` because · `⊢` proven · `⊬` unproven · `⊥` invalid · `⏸` hold · `▶` execute · `✓` pass · `✗` fail.

## Examples
| Intent | DO form |
|---|---|
| Cost gate | `Require free-tier eligibility or verified credits before provisioning` |
| Evidence gap | `Feed freshness = unknown; schedule verification` |
| Service boundary | `Render owns optional feed caching` |
| Offline target | `Termux Origin = offline; native validation = pending` |
| Routing | `⤴ QUE → role-scoped recipient → evidence receipt` |
| Review | `CI ✓ → independent review → merge` |

## Enforcement boundary
The Siglary policy workflow checks PR titles, PR bodies, new commit subjects, issue comments, review comments and added prose/comment lines. The checker focuses on ordinary-language negation patterns and emits exact locations. It preserves technical tokens, code syntax, factual quotations, standards language and explicitly tagged `SIGLARY-EXEMPT:` lines for precise technical or legal cases.

Contributors resolve findings by rewriting the statement as an affirmative action, state or gate. The policy remains intentionally narrow: code behavior, test assertions, API fields and machine-readable protocols retain their exact semantics.

## Governance
- Maintainers own exceptions and record the reason beside `SIGLARY-EXEMPT:`.
- CI reports each violation with file/line or GitHub object identity.
- A green policy check means the submitted communication passed the configured lexical guard; human review retains semantic authority.
