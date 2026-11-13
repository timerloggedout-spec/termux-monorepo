# DO-Statement Mandate — Repository-Wide

**Status:** ACTIVE · scope: new authored material across the repository and project chats.

## Operating contract

`CHAT := STATE-CHANGE ∨ OVERSIGHT`

Use each message, comment, commit, pull-request description, workflow prompt, code comment, document, and skill to cause a concrete state change or provide actionable oversight.

- Lead with the action: **Add, Keep, Preserve, Route, Verify, Publish, Record, Compare, Escalate, Measure, or Stop**.
- State the intended result before the constraint.
- Convert negative-first instructions into positive operating steps.
- Keep the signal dense: `MAX(signal / token)` · CAVEMAN-6 · Siglary operators.
- Remove filler, repeated context, and ceremony.
- Attach a receipt to material state changes: path, SHA, PR, workflow run, scan ID, or verified URL.

## Scope

Apply this contract to:

- GitHub issue and pull-request comments.
- Commit subjects and bodies.
- Pull-request titles and descriptions.
- Source-code comments and docstrings.
- GitHub Actions names, prompts, and log messages.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `SKILLS.md`, ICMs, docs, and all `SKILL.md` files.
- Chat relays, status reports, and operator-facing dispatches.

Historical records and quoted source material retain their original wording. Code syntax and domain-specific formal statements retain their required semantics.

## Siglary operator register

Use formal operators with their registered meanings:

| Operator | Meaning |
|---|---|
| `∧` | AND |
| `∨` | OR |
| `¬` | NOT |
| `⇒` | implies |
| `⇔` | iff |
| `∀` | for all |
| `∃` | there exists |
| `∅` | empty set |
| `∈` / `∉` | member / non-member |
| `Δ` | change |
| `≈` | approximately |
| `≡` | equivalent |
| `≠` | unequal |
| `≤` / `≥` | bounds |
| `⊕` / `⊗` | combine / constrained combine |
| `⤴` / `↳` | route / child |
| `⊢` / `⊬` | proven / unproven |
| `⊥` | invalid |
| `⏸` / `▶` / `✓` / `✗` | hold / execute / pass / fail |

GLYPHS, CHORDS, and OPERATORS remain distinct classes under [Siglary Standard](../proposals/active/notation-sets/SIGLARY-STANDARD.md). Resolve every chord in a named Shorthand Domain. Use plain language as the canonical fallback whenever a compact form risks ambiguity.

## Authoring patterns

| Surface | DO pattern |
|---|---|
| Code comment | `Preserve the source SHA so the published receipt stays attributable.` |
| Commit subject | `Add agent-readability source validation` |
| Commit body | `Add the P8 metadata gate and record the publication path.` |
| PR description | `Publish the canonical source, run the dual gates, and verify the deployed URLs.` |
| Review comment | `Add a regression test for the empty Open Graph description.` |
| Workflow prompt | `Read the current source, apply the bounded change, run the named checks, and record the result.` |
| Chat relay | `P8 fixed in source; deployment and live scan remain in the verification queue.` |

## Public content and internal codecs

- Keep public HTML, Markdown, `llms.txt`, sitemap files, and Agent Ready fixtures directly readable.
- Keep zero-width and bidirectional control characters out of public crawler-facing surfaces.
- Keep experimental invisible-character encodings inside an explicitly scoped internal codec with a visible canonical sidecar, documented decoder, and round-trip tests.
- Preserve canonical source text and semantic equivalence across HTML and Markdown projections.
- Use schema nulls for unestablished data values. Keep chat-only epistemic markers out of machine records.

## Release and verification

A score badge is eligible only when a fresh Agent Ready receipt records `score ≥ 95`, a scan URL, and a verification timestamp. Unknown or lower scores keep the badge hidden.

A source-level pass and a deployed-page pass are separate receipts. Record both before declaring the public surface complete.
