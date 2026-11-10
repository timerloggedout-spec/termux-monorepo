# Siglary — Standard of Record + Enforcement Design

Owner order 2026-11-10 04:54 PT: **Siglary is repo-wide
ENFORCED.** This file is the standard; the Notation Matrice
(CAVEMAN-MICRO-DENSE-V2.md, legacy path) is its register.
Linguist owns the standard + validation design; enforcement
machinery is built by Swarm via Desk QUE (filing of record
rides this standard).

## 1. Scope (of record)

Enforcement surfaces:

- **repo skill files** — `skills/**`, `SKILL.md` files,
  `~/workspace/custom-skills` mirrors of record in-repo;
- **ICM** surfaces (instruction/context modules of record);
- **`*.SKILLS` / `SKILLS.md`** files anywhere in the repo;
- **`CLAUDE.md`** (repo root + nested) — the conventions
  surface carries the standard by reference;
- **DoE-dispatched participants' usage** — reports, stamps
  and records emitted by participants in DoE planes (chat
  relays + repo records alike).

Out of scope: quoted prior art, historical sealed records
(ledgers stand as written), code identifiers (unless a
surface above governs them).

## 2. The standard (what compliance means)

1. **Classes kept distinct** (taxonomy of record):
   GLYPHS (pictographs) · CHORDS (letter codes, resolved
   in-domain via Shorthand Domains) · OPERATORS (formal
   symbols: logic ∧ ¬ ∨ ⇒ · quantifiers ∀ ∃ · set ∅ ∈ ·
   ∆ · `++` · ≅). Calling an operator a glyph, or a chord a
   glyph, is a class violation.
2. **Principles ⓪–⑤ bind**: glyph cap (highest-frequency
   only; default = chord/word) · one glyph per recurring
   concept · chord codes for domain terms · vowel-drop
   glue only · owner swaps override · **accuracy outranks
   compression** (ambiguous ∨ misleading form = violation,
   however short).
3. **N∅ boundary**: NOT_ESTABLISHED/`N∅` = chat epistemic
   marker only — NEVER a data-of-record value. A data
   surface (ledger · feed · DB · machine-readable file)
   carrying it = **hard violation, fail-closed**.
4. **Receipt discipline**: state claims in enforced
   surfaces carry their receipt class (🧾/id) — a verdict
   or state-change without an adjacent receipt reference
   is a soft violation (drift-eligible, per nc-1 R3).
5. **Registers**: ≅ in math register = proof-gated claim;
   in Siglary register = conformance predicate. Mixing
   registers without marking = violation.

## 3. Validation design (compliance measured, ¬ assumed)

**Validator** (Swarm-built, Linguist-specced):

- **Census pass** over the §1 surfaces on every push
  touching them + a weekly full-repo census. Each surface
  instance is classified: compliant · soft-violation
  (class/register/receipt classes) · hard-violation
  (N∅-in-data; misleading form under ⑤ where decidable).
- **Decidable checks first**: N∅/NOT_ESTABLISHED as a
  stored value in data files (grep-class, exact) · class
  misuse in the Matrice's own surfaces · unresolved
  chords (chord ∉ any Shorthand Domain table) in enforced
  surfaces · glyph inflation (glyph ∉ issued set).
- **Judgment checks sampled**: ambiguity/misleading-form
  (⑤) and receipt-adjacency are rated on a sampled stratum
  via the nc-1 evaluator pattern (dual-rater, κ-gated)
  — NOT_ESTABLISHED-grade until κ lands; reported as
  estimates, never as census facts.
- **Verdict contract**: per-surface compliance rate +
  violation counts by class, stamped {surface · as-of ·
  rates}; hard violation on a merged surface = FAIL
  (fail-closed), soft violations = report + drift queue.
  A green run with ∅ census = INCONCLUSIVE, ¬ PASS.
- **Feed**: results land in the linguist panel feed family
  (siglary_compliance entry class) — schema nulls where a
  rate is not established (never N∅ in the data).

## 4. Performance design (does it work, measured)

- **Compression**: sampled before/after on enforced
  surfaces — characters + message count per delivered
  outcome (the honest unit is the message, ¬ the glyph);
  reported as distributions, not point claims.
- **Correctness**: misread rate on the judgment stratum
  (a compressed form read wrong by the second rater =
  a ⑤ event); target trend ↓; any class of form with
  repeated misreads is re-issued or killed by Linguist
  ruling.
- **Cost**: validator runtime + census cost per run,
  stamped; enforcement that costs more than the
  compression saves is itself a finding.

## 5. Enforcement route

Machinery (validator workflow · census · feed writer ·
drift queue) = Swarm build via Desk QUE filing keyed
`project-task`. **Blocker of record at filing**: Termux
Fleet Swarm App installation 177357774 SUSPENDED
(GitHub-side, 2026-11-10) — app-minted execution blocked
until unsuspend; PAT routes unaffected; the standard and
this design are in force regardless (compliance is owed
by authors now; measurement starts when machinery runs).

## 6. Enforcement profile (Leg A — QUE #5116)

Per-surface-class conformance. Severity: **HARD** =
fail-closed at gates · **SOFT** = receipted finding,
drift queue · **EST** = sampled estimate only (judgment
stratum, §3).

### 6.1 Skills files (`SKILL.md` · `*.SKILLS` · `SKILLS.md`)

| Rule | Severity |
|---|---|
| Classes distinct in any notation the file teaches/uses | HARD |
| Chords resolve in a named Shorthand Domain (or the file defines its domain inline) | HARD |
| Glyph set ⊆ issued set (cap ⓪) | HARD |
| N∅/NOT_ESTABLISHED stored as a value in any data block | HARD |
| Receipt-adjacency for verdicts/state claims the skill prescribes | SOFT |
| ⑤ misleading form | EST → HARD on Linguist ruling |

### 6.2 ICM surfaces

| Rule | Severity |
|---|---|
| Dispatch/context stamps in Siglary form (class-correct) | HARD |
| Participant-facing instructions name their notation classes (¬ bare "glyphs" for operators) | SOFT |
| N∅ boundary (chat-only marker; records carry schema nulls) | HARD |
| ⑤ misleading form | EST → HARD on ruling |

### 6.3 CLAUDE.md (root + nested)

| Rule | Severity |
|---|---|
| Carries the standard by reference (this file + Matrice) | HARD (presence check) |
| Its own notation usage class-correct (operators ¬ called glyphs) | HARD |
| New notation introduced without Matrice registration | SOFT |

### 6.4 DoE-dispatched participants' usage

| Rule | Severity |
|---|---|
| Dispatch stamps + outcome records in Siglary form (classes distinct; chords in-domain) | SOFT (report-only until gate step) |
| Verdicts carry adjacent receipt refs (nc-1 R3 class) | SOFT |
| N∅ in any participant-emitted data record | HARD |
| ⑤ misleading form in a stamp/record | EST → HARD on ruling |

### 6.5 Exemption classes (of record)

- **E1 sealed records**: hash-chained/historical ledgers
  and merged records stand as written; enforcement is
  forward-only.
- **E2 quoted prior art**: quotations, prior-art citations
  (incl. "Caveman"/CEDRLang material quoted as prior art),
  and external text reproduced for analysis.
- **E3 code**: identifiers, string literals, and syntax of
  programming languages (a Lean `++` list-append in code
  is code, ¬ a Siglary operator use).
- **E4 fixtures**: test fixtures + seeded violation
  examples, when stamped as fixtures.
- **E5 generated artifacts**: conformance is enforced at
  the generator/template, ¬ by hand-editing outputs;
  violations route to the generator's owner.
- **E6 chat exports / transcripts**: historical captures
  stand; enforcement binds new authoring.

### 6.6 Principle ⑤ binding (accuracy > compression)

⑤ binds **every** surface class above, without exception:
any participant may flag any form as ambiguous/misleading;
a flagged form is **suspended** (expanded plain form is
always compliant) pending a Linguist ruling; a ruling of
"misleading" makes the form a HARD violation class-wide
and the Matrice entry is re-issued or killed. Compression
is never a defense. Rollout: report-only first, then
gates bind per surface class in the order 6.3 → 6.1 →
6.2 → 6.4, each step receipted on QUE #5116.
