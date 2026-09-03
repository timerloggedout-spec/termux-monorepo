# MVT Experiment Skill

## Purpose
Run controlled minimum-viable tests across branches, tags, and immutable commit SHAs without rewriting history.

## Contract
1. Resolve every ref to an immutable commit SHA before comparison.
2. Record experiment ID, baseline SHA, candidate SHA, merge-base, suite, timestamps, changed paths, and outcome.
3. Keep baseline and candidate immutable during measurement.
4. Compare like-for-like suites and preserve raw evidence.
5. A failed or missing observation is not a pass.
6. Provider/deployment failures are classified separately from repository correctness.
7. Promotion is a separate reviewed operation.
8. Never discard a superseded experiment without preserving its provenance.

## Loop
RECON -> SELECT -> RESOLVE -> MEASURE -> WAIT -> VALIDATE -> RE-FETCH -> COMPARE -> CLASSIFY -> REPEAT.

## Adapters
Forensics/Restore, fragment matching, reverse-pointer mapping, Chrono/time-loop analysis, notation taxonomy, workflow reliability, GitHub Actions, Linear, Notion, Hex, and Vercel may consume this contract. Adapters must emit the same evidence fields and must not mutate experiment refs.
