# PDDL in Siglary — a worked example (Matrice candidate entry)

Status: **candidate** (Linguist screens: entry form ✓ ·
in-domain chord collisions ∅ · formal PDDL validity =
planner-checked at the control-plane lane, #5195/#5198).
Companion to the Matrice (Siglary). PDDL is the
control/planning language of the DoE agentic logistics
control plane (QUE #5195 · PR #5198, DPLC items) — this
example shows a planning problem *authored and read* in
Siglary: operators state the logic, chords name the
domain terms, glyphs appear only in the reading layer
(comments/stamps), never inside PDDL syntax (E3 code
exemption — PDDL text itself stays pure).

## The shorthand_planning domain (candidate chords)

| Chord | PDDL term |
|---|---|
| `dom` | domain |
| `prb` | problem |
| `act` | action |
| `pre` | precondition |
| `eff` | effect |
| `flu` | fluent (predicate state) |
| `gol` | goal |
| `obj` | object |
| `typ` | type |

## Worked example — QUE dispatch planning

One QUE filing's lifecycle as a planning problem: an
unclaimed filing must be claimed, built, verified, and
merged; escalation is the route when the claim window
lapses.

```lisp
(define (domain que-dispatch)
  (:requirements :strips :typing)
  (:types filing seat)
  (:predicates
    (queued ?f - filing)        ; flu: in the queue
    (claimed ?f - filing ?s - seat)
    (built ?f - filing)
    (verified ?f - filing)
    (merged ?f - filing)
    (window-open ?f - filing))  ; claim window live
  (:action claim                 ; act: claim
    :parameters (?f - filing ?s - seat)
    :precondition (and (queued ?f) (window-open ?f)
                       (not (claimed ?f ?s)))
    :effect (claimed ?f ?s))
  (:action build
    :parameters (?f - filing ?s - seat)
    :precondition (claimed ?f ?s)
    :effect (built ?f))
  (:action verify
    :parameters (?f - filing)
    :precondition (built ?f)
    :effect (verified ?f))
  (:action merge
    :parameters (?f - filing)
    :precondition (verified ?f)
    :effect (merged ?f)))

(define (problem que-5116)
  (:domain que-dispatch)
  (:objects f5116 - filing qdesk - seat)
  (:init (queued f5116) (window-open f5116))
  (:goal (merged f5116)))
```

## The Siglary reading (what the notation adds)

Plan of record, stamped in Siglary form:

```
claim(f5116, qdesk) ⤴ · pre: queued ∧ window-open ∧ ¬claimed
build(f5116, qdesk) · pre: claimed
verify(f5116)       · pre: built        ⇒ 👁 on pass
merge(f5116)        · pre: verified     ⇒ ⚖ merged = gol ✓
```

Reading rules the example exercises:

- **Operators carry the logic**: `pre` is a conjunction
  (∧) with a negation (¬); the plan's validity is
  ∀ steps: pre(step) holds ⇒ eff(step) joins the state.
- **Chords carry the domain**: `act · pre · eff · flu ·
  gol` name PDDL's own parts in-domain shorthand_planning.
- **Glyphs stay in the reading layer**: ⤴ dispatch ·
  👁 verified · ⚖ ruling/merge — stamps about the plan,
  ¬ syntax inside it (E3: the `.pddl` text is code).
- **ker of the compression**: the reading drops types,
  the `:requirements` header, and negative-precondition
  detail beyond the one shown — a reader who needs them
  returns to the PDDL of record. The PDDL is the source;
  the Siglary line is its receipt-grade summary.

## Why this is the candidate form

Siglary incorporation for a formal language = (1) a
chord domain for the language's own terms, (2) operators
doing the logic in readings, (3) the formal text itself
untouched. Any planning surface in #5195/#5198 can adopt
the same pattern: `dom/prb` files stay pure; plans,
verdicts and dispatch stamps read in Siglary.
