# Production MVP Delivery Gantt — Delphi Oracle / MVT-DoE / Moneyball

**Updated:** 2026-10-24  
**Scope:** ship a useful offline MVP while keeping `master` functional. This is an execution ledger, not a claim that every lane is complete.  
**Source of truth:** GitHub PRs, workflow runs, sanitized artifacts, issue/PR review receipts. A plan or queued workflow is not execution evidence.

## Critical path

| Window (estimate from start) | Lane | Work package | Exit evidence | State |
|---|---|---|---|---|
| T+00–30 min | P0 — Offline oracle | Freeze synthetic cohort; implement closed decision enum, evidence gate, synthetic comparator, three experiment contracts | Unit tests; fixture hash; receipt with E-01/E-03/E-05 | Implemented on MVP branch; CI pending |
| T+30–60 min | P0 — CI / production guard | Run offline tests without secrets/network; publish sanitized receipt artifact; keep AWS and deployment disabled | Green PR checks on exact SHA; artifact source SHA + hash | Implemented on MVP branch; CI pending |
| T+30–90 min | P0 — MVT/DoE/TLM | Preserve V0 as comparator; connect the existing #1567/#1569 source matrix and TLM receipt to common fixture/evidence contract | Source/claim matrix, fixture version, run receipt, limitations, independent review | Existing evidence/docs; integration and reviewer receipts pending |
| T+45–90 min | P0 — Delphi independent-results lane | Separate human ballots, model/provider observations, deterministic baseline, and automation gates; collect only validated completed results | Per-source receipt, duplicate/dependency handling, missingness, dissent; no synthetic votes | Contract merged in #1611; actual independent results pending |
| T+60–100 min | P1 — Gantt / RFP lifecycle | Keep proposal items, dependency order, acceptance criteria, owner gates and status linked | Versioned Gantt + item ledger; links to issue/PR/CI evidence | This plan committed with MVP branch |
| T+60–120 min | P1 — EPS / Moneyball value board | Reuse existing Basksweep-approved evidence; separate actual cost, counterfactual list-price value and verified no-cost execution | Deterministic projector tests, reconciled source manifest, explicit stale/unknown state | #1592 open; not complete |
| T+60–120 min | P1 — Adaptive quota awareness | Extend the existing quota panel/readers, not a parallel poller or registry | Freshness/authority distinctions, safe public projection, private fields excluded | #1593 open; not complete |
| After explicit approval | P2 — AWS adapter | Re-check current eligibility, account-specific credits, region, IAM/OIDC, budget caps, kill switch and teardown; only then enable a minimal adapter | Explicit owner approval + deployment/usage/cost/teardown receipts | Blocked; no AWS calls/resources claimed |
| After verified connector state | P2 — Hex consumer | Re-check provider cooldown and native connector access; use only sanitized artifact and read-only projection | Fresh connector result, confirmed import/export receipt, no assumption from Actions ZIP | Unverified; connector query on 2026-10-24 returned a Team/Enterprise access-tier requirement, not a cooldown timestamp; expiry unknown |

Time windows are planning estimates, not deadlines or evidence of elapsed work. Independent reviewers may work in parallel after the frozen fixture contract is published.

## Lanes and dependencies

```text
                         MASTER FUNCTIONALITY GATE
                    repo-gate + smoke + workflow contracts
                                  |
                 +----------------+----------------+
                 |                                 |
          OFFLINE ORACLE MVP                 MVT / DoE / TLM
          E-01 / E-03 / E-05                V0 + source matrix
                 |                                 |
                 +---------------+-----------------+
                                 |
                      SANITIZED TLM / EPS RECEIPT
                                 |
                  +--------------+---------------+
                  |                              |
          DELPHI RESULT CURATION          MONEYBALL PROJECTION
          human != model != CI            actual != counterfactual
                  |                              |
                  +--------------+---------------+
                                 |
                      READ-ONLY DASHBOARD / HEX
                                 |
                     OWNER-GATED CLOUD EXPERIMENT
```

## Release rules — master must remain functional

1. Build and validate on a topic branch. No direct writes to `master`.
2. Run the device-friendly repository gate and Termux smoke; run the MVP contract suite and proposal lifecycle checks.
3. Publish a receipt tied to the exact commit and fixture hash. The receipt must state `DEPLOYED=false`, `PROMOTED=false`, `aws_invocations=0` for this local MVP.
4. Re-fetch final head SHA, workflow conclusions, and artifact metadata before considering merge.
5. Merge only when required checks pass and the PR remains mergeable at the expected SHA. Do not treat skipped/cancelled provider reviews as successful reviews.
6. After merge, re-fetch `master`, verify the merged source and rerun the master functional gate. A merged commit alone is not proof of runtime health.

## Definition of MVP

**In scope:** deterministic evidence-gated decision recommendations; fail-closed consequential actions; frozen synthetic fixtures; three experiment contracts on the same cohort/rubric; counterfactual replay; adversarial instruction isolation; versioned sanitized receipt; no-network/no-credential CI; explicit evidence-state accounting.

**Out of scope until separately authorized and evidenced:** model/provider results, human consensus, live routing, account creation, AWS deployment, paid invocations, native Hex import/export, or promotion to production traffic.

## Open gates

- [ ] MVP branch checks and artifact inspected on the final SHA.
- [ ] #1567/#1569 evidence and independent collaborator reviews reconciled.
- [ ] #1611 term registrar and ballot deadline assigned; real ballots/provider runs collected, or their absence explicitly reported.
- [ ] #1592 deterministic projector built and validated against Basksweep-approved fixtures.
- [ ] #1593 integrated into the existing quota surface with safe public/private separation.
- [ ] Hex connector cooldown/access state fetched from an authoritative current source; do not infer an expiry. The current tool response is an access-tier error and does not establish cooldown duration.
- [ ] AWS eligibility and budget gates rechecked; explicit owner approval recorded before any cloud action.
