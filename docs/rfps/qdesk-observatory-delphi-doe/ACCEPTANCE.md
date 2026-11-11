# QDesk pipeline — acceptance and verification matrix

| ID | Requirement | Test / evidence | Pass condition |
|---|---|---|---|
| QD-001 | Trigger idempotency | Replay same event N times | One request and one RFP identity |
| QD-002 | Burst safety | Concurrent issue/dispatch fixture | One coalesced sweep; no starvation |
| QD-003 | Evidence completeness | Missing evidence fixture | Explicit UNVERIFIED; no invented claim |
| QD-004 | Generator determinism | Same pinned inputs/config/seed twice | Byte-identical normalized output |
| QD-005 | Generator sensitivity | Change one input hash/config value | New provenance identity; old result retained |
| QD-006 | Duplicate handling | Duplicate source cards | Flag groups; no deletion |
| QD-007 | Domain-transfer safety | Trading-domain flagged candidate fixture | Parked absent explicit domain review |
| QD-008 | Design integrity | Planned vs observed allocation | SRM / assignment integrity passes or design is held |
| QD-009 | Stratum integrity | Cross-stratum outcome fixture | Wrong-stratum records excluded from target N |
| QD-010 | Replication semantics | Repeat one task vs independent tasks | Distinct repeated-measure and task-replication counts |
| QD-011 | Uncertainty | Small-n fixture | Descriptive only; no unsupported significance claim |
| QD-012 | Delphi fidelity | Signed ledger fixture | Votes/award exactly sourced; no generated ballot |
| QD-013 | Gate boundary | Parked/needs-access fixture | No implementation or secret provisioning |
| QD-014 | Permission boundary | Builder token lacks protected scopes | No merge/deploy/credential mutation |
| QD-015 | Role independence | Builder == verifier fixture | Validation held |
| QD-016 | Provenance | Tampered input/output hash | Receipt validation fails closed |
| QD-017 | Recovery | Cancelled workflow fixture | Resume from durable receipt and idempotent stage |
| QD-018 | Negative results | Candidate failure fixture | Failure retained and queryable |
| QD-019 | Incumbent preservation | Candidate scores regress | Incumbent retained |
| QD-020 | Cherry-pick lineage | Partial feature extraction | New child candidate links parent and selected feature |
| QD-021 | Propagation | Successful candidate promoted | New generation record with evidence and parent |
| QD-022 | Observatory freshness | Stale and missing feed fixtures | STALE / UNKNOWN / NOT_ESTABLISHED distinct |
| QD-023 | Feed parity | Feed vs canonical ledger census | Exact or explicit delta |
| QD-024 | Cost safety | No quota / exhausted / card-gated fixtures | No paid fallback or hidden spend |
| QD-025 | End-to-end | Intake → award → design → build → verify → receipt | Full correlated trace, all gates passed |
| QD-026 | Feed freshness | Fresh envelope with stale nested event batch | Per-block stale state is visible; no freshness laundering |
| QD-027 | Priority dimension separation | Fixture with QUE tier, opportunity timebox, quota focus and Gantt dependency | Each dimension remains distinct; no scalar silently overrides hard gates |
| QD-028 | Gantt instant honesty | Missing start, explicit close, null/unknown dates | Milestone only; no fabricated start or duration |
| QD-029 | Canonical/mirror parity | Compare QUE and dashboard mirror feeds | Byte-identical where the feed contract requires it |
| QD-030 | Quota snapshot shape | Missing/partial `series2_snapshots[].states` | Quota Usage renders explicit absence; no runtime exception or zero-fill |
| QD-031 | Queue census honesty | Queued, in-progress and >7-day wedged fixtures | Wedged runs excluded only with explicit separate listing |
| QD-032 | Refill attribution | Referral click, pending reward, verified credit and commission fixtures | Click/eligibility/credit/commission remain distinct states and resource classes |

## Minimum pilot

The first pilot must be offline or shadow-only, use a pinned and explicitly scoped candidate census, and run at least:
- one baseline;
- one randomized treatment cohort;
- one control/complement cohort;
- one independent verifier;
- one intentionally failing candidate;
- one duplicate-source fixture;
- one stale/unknown quota fixture.

The pilot is descriptive until the registered design's minimum evidence and uncertainty conditions are satisfied. It cannot promote a production route.

## Release checklist

- [ ] Existing Delphi and DoE contracts reconciled.
- [ ] Schema version and migration notes reviewed.
- [ ] Deterministic generator golden tests pass.
- [ ] RFP trigger idempotency and burst tests pass.
- [ ] SRM / allocation integrity checks pass.
- [ ] Provenance receipts verify.
- [ ] Builder/reviewer/verifier identities distinct.
- [ ] Security and cost gates pass.
- [ ] Observatory feed parity and stale-state tests pass.
- [ ] Failure injection and rollback rehearsal complete.
- [ ] Independent review recorded.
- [ ] Owner authorization recorded for any protected action.
- [ ] Feed/Gantt census reviewed; freshness, authority and mirror-parity gates pass.
