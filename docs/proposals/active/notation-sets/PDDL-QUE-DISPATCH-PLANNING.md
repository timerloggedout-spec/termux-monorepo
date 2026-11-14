# PDDL QUE Dispatch Planning — Extended Candidate

**Status:** candidate; planner validation required  
**Purpose:** formalize the existing QUE dispatch example with explicit resource, lease, verification and terminal-state semantics.

The existing `PDDL-SIGLARY-EXAMPLE.md` remains the notation/reading example. This file extends the planning model; it does not supersede the canonical QUE implementation or workflow contract.

## Siglary relationship

**PDDL ⊂ Siglary.** Siglary is the parent notation system and vocabulary governance; PDDL is its specialized formal-planning register. Preserve standard PDDL domain/problem syntax wherever planner interoperability requires it. Siglary metadata and adapters supply the wider notation context, operator vocabulary mapping and provenance. Register new Siglary terms/chords through the Linguist-owned Matrice; keep planner-facing PDDL tokens standards-compatible.

## Planning boundary

PDDL answers: *is there a sequence of legal actions that reaches the goal under declared predicates/resources?*

It does not answer whether a code change is correct. Verification is represented as a required action whose result must come from an independent evidence-producing validator.

For production use, pin the planner and version, retain the domain/problem files, command line, planner output, plan digest and validation receipt.

## Candidate PDDL domain

```lisp
(define (domain que-dispatch-v2)
  (:requirements :strips :typing :negative-preconditions)
  (:types filing seat)
  (:predicates
    (queued ?f - filing)
    (claimed ?f - filing ?s - seat)
    (built ?f - filing)
    (verified ?f - filing)
    (merged ?f - filing)
    (window-open ?f - filing)
    (lease-valid ?f - filing ?s - seat)
    (available ?s - seat)
    (blocked ?f - filing)
    (failed ?f - filing)
    (awaiting-verification ?f)
    (verification-receipt-valid ?f)
  )

  (:action claim
    :parameters (?f - filing ?s - seat)
    :precondition (and
      (queued ?f)
      (window-open ?f)
      (available ?s)
      (not (blocked ?f))
    )
    :effect (and
      (claimed ?f ?s)
      (lease-valid ?f ?s)
      (not (queued ?f))
      (not (available ?s))
    )
  )

  (:action build
    :parameters (?f - filing ?s - seat)
    :precondition (and
      (claimed ?f ?s)
      (lease-valid ?f ?s)
      (not (blocked ?f))
    )
    :effect (and (built ?f) (awaiting-verification ?f))
  )

  (:action accept-independent-verification
    :parameters (?f - filing)
    :precondition (and
      (built ?f)
      (awaiting-verification ?f)
      (verification-receipt-valid ?f)
      (not (failed ?f))
    )
    :effect (and
      (verified ?f)
      (not (awaiting-verification ?f))
    )
  )

  (:action release-seat
    :parameters (?f - filing ?s - seat)
    :precondition (and (claimed ?f ?s) (verified ?f))
    :effect (and
      (available ?s)
      (not (lease-valid ?f ?s))
      (not (claimed ?f ?s))
    )
  )

  (:action release-seat-failed
    :parameters (?f - filing ?s - seat)
    :precondition (and (claimed ?f ?s) (failed ?f))
    :effect (and
      (available ?s)
      (not (lease-valid ?f ?s))
      (not (claimed ?f ?s))
    )
  )

  (:action merge
    :parameters (?f - filing)
    :precondition (verified ?f)
    :effect (and (merged ?f) (not (queued ?f)))
  )
)
```

## Modeling cautions

- The example uses a simplified single-seat availability predicate; concurrent capacity requires numeric fluents or explicit seat objects.
- `verification-receipt-valid` is an externally established fact imported from an independently verified evidence receipt. The planner must never invent this predicate or treat its own plan as verification.
- Lease expiry, wall-clock deadlines and durative build/verification require a temporal PDDL subset or an external scheduler.
- A real merge is an external side effect and must remain behind repository policy/approval; a planner-generated plan is not authorization.
- The failed-seat release is only a simplified recovery path; retry/requeue, lease expiry and compensation still need explicit actions and terminal conditions before this model can represent production behavior.
- The domain is not declared valid until checked by a named PDDL planner and scenario tests.

## Required validation cases

1. queued + open window + available seat yields a claim plan;
2. claim consumes the queued state so a second seat cannot claim the same filing;
3. closed window prevents claim;
4. blocked filing prevents claim/build;
5. unavailable seat prevents claim;
6. build cannot precede claim;
7. merge cannot precede independent verification receipt;
8. expired lease cannot authorize build;
9. repeated release by the former claimant cannot free a seat now leased by another filing;
10. a planner plan cannot bypass human approval or repository branch protection.
