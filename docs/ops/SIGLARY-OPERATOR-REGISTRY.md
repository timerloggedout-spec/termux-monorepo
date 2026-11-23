# Siglary Operator Registry

**Contract:** one glyph = one meaning · role-visible families · explicit grouping · zero implied precedence.

Use stable IDs in reviews, tests, documentation, and lint findings. Keep glyphs exact; use parentheses or explicit words when grouping could be ambiguous.

## Logic

| ID | Glyph | Meaning | Example |
|---|---|---|---|
| SIG-OP-001 | ∧ | AND; both predicates hold | auth ∧ catalog |
| SIG-OP-002 | ∨ | OR; either predicate holds | queued ∨ running |
| SIG-OP-003 | ¬ | logical negation | ¬eligible |
| SIG-OP-004 | ⇒ | implies; left condition entails right result | tests pass ⇒ ready |
| SIG-OP-005 | ⇔ | iff; both directions hold | ready ⇔ gates pass |
| SIG-OP-006 | ∈ | member of a set | provider ∈ catalog |
| SIG-OP-007 | ∉ | excluded from a set | secret ∉ artifact |
| SIG-OP-008 | ∀ | for all members | ∀ changed files |
| SIG-OP-009 | ∃ | at least one exists | ∃ valid route |
| SIG-OP-010 | ∅ | empty set / none | reviewers = ∅ |
| SIG-OP-011 | ≠ | distinct / unequal | catalog ≠ inference |
| SIG-OP-012 | ≡ | equivalent under the stated contract | source ≡ projection |
| SIG-OP-013 | ≈ | approximate value or relationship | latency ≈ 1s |
| SIG-OP-014 | ≤ | less-than-or-equal bound | latency ≤ 2s |
| SIG-OP-015 | ≥ | greater-than-or-equal bound | coverage ≥ 95% |
| SIG-OP-016 | ∝ | proportional relationship | load ∝ concurrency |

## Evidence

| ID | Glyph | Meaning | Example |
|---|---|---|---|
| SIG-OP-017 | ⊢ | proven by cited evidence | ⊢ repo gate PASS |
| SIG-OP-018 | ⊬ | evidence insufficient to establish the claim | ⊬ inference ready |
| SIG-OP-019 | ⊩ | assertion paired with trace/evidence | ⊩ catalog healthy {run 123} |
| SIG-OP-020 | ≟ | disputed / requires adjudication | quota ≟ free |
| SIG-OP-021 | ∎ | closed / terminal disposition | SIG-01 ∎ |

## Flow

| ID | Glyph | Meaning | Example |
|---|---|---|---|
| SIG-OP-022 | ⤴ | route / hand off | ⤴ QUE |
| SIG-OP-023 | ↳ | child / subordinate item | ↳ SIG-02 |
| SIG-OP-024 | ⤵ | land / deliver output | ⤵ PR #123 |
| SIG-OP-025 | ↻ | cadence / repeat cycle | ↻ daily probe |
| SIG-OP-026 | ⊕ | combine / additive composition | A ⊕ B |
| SIG-OP-027 | ⊗ | constrained combination | route ⊗ quota |
| SIG-OP-028 | ⋈ | join / correlate records | task ⋈ run |

## State

| ID | Glyph | Meaning | Example |
|---|---|---|---|
| SIG-OP-029 | ⏸ | hold pending a named release condition | ⏸ auth proof |
| SIG-OP-030 | ▶ | execute / proceed | ▶ smoke |
| SIG-OP-031 | ✓ | passed / verified | ✓ repo gate |
| SIG-OP-032 | ✗ | failed / rejected | ✗ lint |
| SIG-OP-033 | ⧖ | pending / awaiting result | ⧖ CI |
| SIG-OP-034 | ⚡ | immediate / execute now | ⚡ bounded probe |
| SIG-OP-035 | Δ | change / difference | Δ files = 2 |
| SIG-OP-036 | § | rule / clause reference | § SIG-OP-001 |

## Composition rules

1. Prefix the operator ID in formal policy, lint output, and review dispositions when a definition matters.
2. Use parentheses for mixed logical expressions; the registry assigns zero operator precedence.
3. Keep one meaning per glyph. Add a new glyph only with a new stable ID and collision review.
4. Preserve Unicode code points exactly in tests and machine output.
5. Treat ⊢ as evidence-backed proof, ⊩ as assertion plus trace, and ⊬ as an evidence boundary.
6. Pair compact notation with a short natural-language explanation when the audience lacks the registry.
