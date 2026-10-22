# Tournament and Evidence Contract Reconciliation

**Status:** integration contract proposal; no leaderboard migration has occurred.  
**Scope:** System One offline receipt scoring, the Observatory tournament/leaderboard, and manager tournament provenance.

## Existing components (inspected)

- `scripts/eval_tournament.py` scores normalized candidate/question receipts. It is an offline analysis utility; it does not call models.
- `deepcli/deepcli/observatory/tournament.py` accepts trial results and records provider/model score, cost, latency, and success into a `Leaderboard`, then returns top and worst trials for a role/task.
- `docs/ops/MANAGER-TOURNAMENT.schema.json` defines `manager.tournament.v1` with tournament/cohort IDs, policy version, task contract hash, environment fingerprint, managers, evaluation contract, and provenance.

These are related, but not interchangeable. Their current schemas and semantics differ. Do not merge their records or present their scores as equivalent without a versioned adapter and explicit metric definitions.

## Recommended integration boundary

1. **Raw receipts remain canonical.** Keep per-question JSONL and source artifacts immutable, content-hashed, and associated with the exact source commit and run.
2. **Offline scorer is a projection.** The tournament JSON report is rebuildable from receipts; it is not a new durable leaderboard.
3. **Observatory leaderboard is a separate projection.** Publish only metrics whose units, cohort, task, and status semantics are explicit. Never map exact-match accuracy into a generic composite score without a documented formula.
4. **Manager tournament is a policy/cohort envelope.** Link it to the raw receipt manifest using an explicit evidence URI and digest in a future schema revision; do not mutate `manager.tournament.v1` records in place.
5. **Expected labels must agree.** Pairwise comparisons use shared question IDs only. If candidates carry different expected values for the same question, mark the row non-comparable and increment `expected_mismatch_questions`; do not award a win.
6. **Failure classes stay distinct.** Correctness, abstention, schema validity, infrastructure status, latency, cost, and judge preference are separate fields. Missing or failed runs must not silently become incorrect answers or be dropped from denominators without disclosure.
7. **Judges are auxiliary evidence.** Preserve judge identity/version and calibration receipts separately. A model's own rating cannot authorize repository writes or certify itself.
8. **Promotion requires matched cohorts.** Pin benchmark/task versions, source commit, adapter/runtime versions, data/config hashes, environment, repetitions, and acceptance thresholds. Report uncertainty when sample sizes permit; do not rank by latency alone.

## Proposed versioned mapping (not yet implemented)

| Evidence concept | Canonical location | Optional projection |
|---|---|---|
| Per-question outcome | Immutable JSONL receipt | Candidate accuracy / pairwise report |
| Runtime measurement | Receipt field with unit | p50/p95 latency and cost summary |
| Run identity | GitHub workflow/run + source SHA | Cohort identifier |
| Benchmark/task definition | Versioned task contract + hash | Manager tournament evaluation contract |
| Artifacts | URI + SHA-256 digest | Redacted manifest |
| Selection decision | Human-reviewed promotion record | Observatory leaderboard entry |

An adapter should reject missing hashes, unknown metric units, duplicate candidate/question pairs, inconsistent ground truth, and unrecognized status values. It should be deterministic and read-only by default.

## Validation checklist

- [ ] Unit tests cover same-label and mismatched-label pairwise cases.
- [ ] JSON output is deterministic and rejects NaN/Infinity.
- [ ] A fixture validates the receipt-to-report projection.
- [ ] Mapping into Observatory is documented and tested without mutating raw receipts.
- [ ] A versioned manager-tournament extension is reviewed before any migration.
- [ ] CI run and artifacts are verified on the exact PR head.
- [ ] No live-model quality claim is made from synthetic fixtures.

## Sources

- Repository-local implementation: [offline scorer](../../scripts/eval_tournament.py)
- Existing Observatory tournament: [tournament.py](../../deepcli/deepcli/observatory/tournament.py)
- Existing schema: [MANAGER-TOURNAMENT.schema.json](./MANAGER-TOURNAMENT.schema.json)
- Research map and adapter/license review: [RECON-INTEL-ECOSYSTEM-MAP.md](./RECON-INTEL-ECOSYSTEM-MAP.md)

This document is an engineering integration proposal, not legal advice, a performance result, or proof that a production adapter exists.
