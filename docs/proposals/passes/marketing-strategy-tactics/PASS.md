# Pass record — marketing-strategy-tactics (Delphi evaluation of fleet marketing)

**Run:** 2026-11-01 · **Commission:** owner order via the
web-design seat (evaluation only) · **Brief:** `brief.json` ·
**Evidence:** `evidence.json` — 15 stamped items, firsthand
artifact reads · **Generator:** `scripts/delphi/generate_proposal.py
--pass` · **Cycle:** `scripts/delphi/method_cycle.py` ·
**Findings:** `EVALUATION.md` (Q1 doctrine, Q2 tactics, Q3 claims spec)

## Candidates (n = 3 doctrines, generated)

| Candidate | Doctrine |
|---|---|
| marketing-strategy-tactics-strict-separation | Fleet surfaces state only the verified record; partner claims never enter fleet copy; tactics survive on measured signal + decision rules |
| marketing-strategy-tactics-attributed-tiered | Verified record in fleet voice; partner claims only labeled + attributed outside hero/brand; unverified offers carry NOT ESTABLISHED in copy |
| marketing-strategy-tactics-partner-forward-blend | Status quo: anchor partner's pitch may headline in fleet voice under a footer disclosure |

Candidate documents live in `docs/proposals/active/<candidate-id>/`,
registered in `docs/proposals/registry.yaml` (`author: oracle-method`).

## Outcome

- **Round 1: TIE at the top** — strict-separation 23.269 =
  attributed-tiered 23.269 (identical profiles; order is the
  tie-break, not a preference); partner-forward-blend 16.462
  (its headline benchmark claim unresolved against the evidence
  base). Ballots: LOCAL_BASELINE 5; HUMAN_COLLABORATOR 0;
  MODEL_PROVIDER 0 — stated, not filled in.
- **Comparator artifact (disclosed):** the first run scored
  tiered 18.423 — the cost_auditor money-veto substring scan
  fired on "cards" ("labeled cards/sections"; grid cards, no
  payment card in any variant). Wording corrected, pass
  regenerated, cycle re-run; scores above are the corrected
  run. Full account in `EVALUATION.md`.
- **Expectations:** brief-author priors strict 1/18, tiered
  2/17, blend 3/7 — blend's rejection matches; the top order
  did not separate (calibration at round 2 records it so).
- **Evaluation findings** (`EVALUATION.md`): separation
  doctrine SOUND with six named failure modes; tactics
  inventory verdicted per tactic on evidence (MVT + D0
  write-up pattern earn; unestablished distribution channels
  = motion without signal); claims discipline spec'd
  (assertable classes vs never-borrow list).

## Specified not run

- **DEBATE / revision round:** callable against the synthesis
  — the strict/tiered tie is its natural subject.
- **Implementation / adoption:** execution belongs to the
  owning lanes after the owner rules (landing PR #16's
  concurrence is Marketing's).
- **Round 2 + calibration:** open on adoption evidence + the
  2026-11-10 MVT window-close snapshot.

## Ledger records

Round-1 ballot record appended to the outcome ledger (issue
#1487) as a `delphi-generation-ballot v1` JSON comment at run
time; full receipts in `cycle/`.
