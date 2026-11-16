---
name: siglary-a2a
description: Write room-to-room (Agent2Agent) messages ∧ status in Siglary. Load before any cross-room dispatch, reply stamp, or status line on an enforced surface.
---

# Siglary A2A

Standard: `docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`. Register (Notation Matrice): `docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md`. Cost evidence: `docs/proposals/active/notation-sets/SIGLARY-TOKEN-COST.md`.

## Shorthand Domain
This skill defines no chords. Every chord it cites resolves in the named Shorthand Domains of the Matrice (`shorthand_repo`, `shorthand_quota`, …).

## Classes (keep distinct; mixing them is a HARD violation)
- **OPERATORS**: ∧ ¬ ∨ ⇒ · ∀ ∃ · ∅ ∈ · ∆ · `++` (postfix step-up once) · ≅ (conforming; proof-gated in the math register).
- **GLYPHS**: issued set only (👁 🧐 🧾 ❄ ⚖ ⛔ 👆 ⤴ 🟢 🔴 🟡).
- **CHORDS**: letter codes that resolve in-domain only.

## Two registers
| Register | Use | Allowed |
|---|---|---|
| **A2A (machine)** | room↔room dispatch, agent replies, machine-read status | OPERATORS ∧ plain one-token words |
| **Display (human)** | Owner chat, dashboards, panels | OPERATORS ∧ issued GLYPHS ∧ CHORDS |

Why: chords ∧ glyphs cost more tokens than plain words (stamp +38% on o200k_base), while operators are near token parity ∧ fix scope. 🧾 SIGLARY-TOKEN-COST.md.

## A2A dispatch stamp
```
dispatch {from}→{to} · {task} · gate: {scope} · receipt {refs} · ∆ ask: {ask}
```
## A2A reply stamp
```
{live|degraded|down|blocked} {task} · verified receipt {PR/SHA/run} · owner action: {act ∨ none}
```

## Rules
1. A state claim must carry its receipt (PR URL · SHA · run URL) adjacent to it.
2. The not-established marker is for chat only. Data-of-record keeps schema nulls; that marker in any data value is a HARD violation.
3. Principle ⑤: if a form can be misread, expand it. Compression is never a defense.
4. Use `x++` only for a single step-up of x in its own scale. Write ∆ with a magnitude for any other change.
5. The Owner is referenced by moniker only.

## Re-measure
`pip install tiktoken && python3 scripts/notation/siglary_token_cost.py`. Re-run it when the register changes ∨ when the target model's tokenizer changes.


## CI hard-gate contract

DO: follow docs/proposals/active/notation-sets/SIGLARY-STANDARD.md as the canonical standard and the CAVEMAN-MICRO-DENSE-V2.md file as its notation register.

DO: resolve explicit chord tokens against a named Shorthand Domain. Keep glyphs, chords, and operators in separate classes.

DO: attach a receipt reference to every emitted state or verdict claim on the same line or the immediately following line.

DO: use null for absent machine data. Keep N∅ and NOT_ESTABLISHED in chat-only prose.

DO: expand a flagged form to plain language until the Linguist records a ruling. Keep E1–E6 exemptions explicit and preserve source bytes.
