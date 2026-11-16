# Siglary + DO authoring enforcement

**Authority:** docs/proposals/active/notation-sets/SIGLARY-STANDARD.md and docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md.
**Implementation task:** #5334. **Leg-B lineage:** #5116 / #5131.

## Enforcement contract

| Surface | Gate | Decidable HARD checks | Judgment boundary |
|---|---|---|---|
| Skills (SKILL.md, SKILLS.md, *.SKILLS) | siglary-census | issued glyphs, explicit chord/domain resolution, class labels, N∅ data blocks, receipt claims | principle ⑤ ambiguity remains EST pending Linguist ruling |
| ICM (docs/icm/**) | siglary-census | class labels, glyph register, explicit chord/domain resolution, N∅ data blocks | principle ⑤ ambiguity remains EST pending Linguist ruling |
| Root + nested CLAUDE.md | siglary-census | canonical-standard reference, class labels, glyph register | principle ⑤ ambiguity remains EST pending Linguist ruling |
| DoE participant records (ops/doe, ops/que/dispatch, ops/que/feeds, ops/challenge) | siglary-census | N∅ data boundary, explicit chord/domain resolution, receipt claims | principle ⑤ ambiguity remains EST pending Linguist ruling |
| GitHub PRs, issues, comments, reviews, releases, issue/PR templates | DO Statement Style + siglary-census | DO hedging, action-first commit subjects, notation class/glyph/chord rules, state/verdict receipt adjacency | principle ⑤ ambiguity remains EST pending Linguist ruling |
| Bot-generated output | generator/template owner | validate rendered output before publication; retain source/template identity | generated artifacts are E5 and are not hand-edited |

## Normative behavior

- **DO:** keep GLYPHS, CHORDS and OPERATORS distinct.
- **DO:** resolve each explicit chord in a named Shorthand Domain.
- **DO:** use only the issued glyph inventory and registered operators.
- **DO:** store data absence as schema-native null; keep N∅ / NOT_ESTABLISHED chat-only.
- **DO:** place a receipt reference on the state/verdict line or immediately following it.
- **DO:** use natural imperatives or an explicit DO: marker for instructions.
- **DO:** preserve necessary prohibitions as valid constraints; the DO gate rejects hedging, not security or preservation constraints.
- **DO:** expand ambiguous notation while a Linguist ruling is pending.

## Exemptions

| Class | Treatment |
|---|---|
| E1 sealed/historical ledgers | preserve original bytes; exclude from prospective scans |
| E2 quoted prior art | preserve quotation; exclude quoted lines from notation classification |
| E3 code | exclude identifiers, syntax and code fences from prose notation checks |
| E4 fixtures | mark seeded examples with SIGLARY-FIXTURE: or place them under tests/fixtures/ |
| E5 generated artifacts | validate at the generator/template; exclude generated projections |
| E6 chat exports/transcripts | preserve historical captures; enforce new authored surfaces |

## Receipt and output contract

The validator emits siglary-census/v1 with per-surface-class counts, named findings, runtime and character/file measurements. A zero-surface census exits non-zero as INCONCLUSIVE; it is never represented as a pass. HARD findings produce FAIL; principle-⑤ EST findings produce REVIEW and block the affected form pending a Linguist ruling. Event receipts use a deterministic SHA-256 identity. The feed writer deduplicates within its feed file; cross-run replay deduplication awaits the persistent authorized feed writer.

The Actions workflows upload the census and feed line as immutable run artifacts. The current workflow uses read-only GitHub permissions; it does not silently write to master. Persistent publication into the Linguist panel feed remains a separately authorized writer integration and is not claimed by this change.

## Validation state

| Capability | State |
|---|---|
| Validator and DO policy authored | IMPLEMENTED |
| Positive/negative seeded contract tests | TESTED locally; hosted CI receipt pending |\n| Principle-⑤ EST review state | IMPLEMENTED and locally tested; hosted receipt pending |
| PR/issue/comment/review/release event wiring | IMPLEMENTED; hosted event receipts pending |
| Hard-gate behavior in Actions | IMPLEMENTED in workflow source; ENFORCED only after a successful hosted run is observed |
| Full-repository baseline census | PENDING first hosted census |
| Bot generator/template integrations | INVENTORIED as a required surface; individual generator adoption remains owner-specific |
| Persistent Linguist feed publication | PENDING authorized writer capability |

Do not promote a surface from IMPLEMENTED to TESTED or ENFORCED without the corresponding run/artifact receipt.
