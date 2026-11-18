# DoE considerations (recon 2026-11-17)

Source: experiments/doe/proofs/INDEX.md and the DOE-PROOF-COVERAGE.md pointer, read 2026-11-17. This note tracks status only. It doesn't change any experiment's verdict.

## Standing rules
- Every experiment of record gets its Lean proof. An entry missing its proof or its data-layer refs reads INCOMPLETE.
- Proof is not evidence. INCOMPLETE is about proof coverage. Other evidence stays valid.
- Artifacts stay in research/nse-023/examples/ and enter the proofs directory by citation.

## E001: settlement machinery
- Oracle run 41746401168 = FAIL (compile failure in section 2).
- The FAIL stands. Repair = an amendment packet plus a new oracle run.
- Section 2 snapshot fixtures are refuted as written: Rat bounds do not kernel-reduce. Owed: Nat-scaled bounds.

## Gap order (from the proofs index)
1. E002: EGM verdict arithmetic
2. E003: speculators acceptance
3. E004: rule-7 accounting
4. E005: mirror scoring (discharges at Panel Judge Mirror close)
5. E006: census arithmetic
6. M001: Wilson and Dirichlet (Mathlib)

## Rule 7 routed dispatch
Sets of 3, n-floor 3, cap 12. The stamp corpus is live.

## Deadlines
- 2026-11-10: fb-pages-mvt-1 decision date. Passed; verdict memo owed.
- 2026-11-18: Panel Judge Mirror judging closes. E005 discharges then.
- 2026-12-01: util-1 provider-rotation window closes (24 stamps, or the date).
- 2026-12-04: live-1 wave framing decision (n >= 16 and >= 4 per cell, or the date).

## Links
- Proof index: experiments/doe/proofs/INDEX.md
- Wiring manifest: experiments/doe/proofs/MANIFEST.json
- Routing side: WORKFLOWS-ROUTING-OPTIMIZATIONS.md in this folder
