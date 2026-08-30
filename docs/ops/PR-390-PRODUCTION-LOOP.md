# PR #390 production loop

PR #390 is a long-lived production integration surface. Its state must never be inferred from a remembered file count, an old review, or an unobserved workflow.

## Required cycle

`observe → compare → classify → implement → commit → wait → validate → re-fetch → repeat`

### Observe

The GitHub production ledger is the source for:

- base/head SHA;
- commit count;
- changed-file count;
- additions/deletions;
- ahead/behind `master`;
- latest commit/review/comment timestamps;
- check totals, pending checks, and failures.

The ledger uses SHA-bound evidence and status-aware retries. Permanent API errors are not retried as though they were transient failures.

### Compare

A large negative diff is **not automatically a rollback**. Compare against `master` and classify each removal:

1. authoritative source/runtime/test → recover when still canonical;
2. active proposal/research → preserve when provenance remains relevant;
3. generated telemetry/evidence → preserve identity and provenance;
4. intentional replacement → retain only with an explicit tested successor;
5. superseded artifact → archive with source SHA, timestamp, reason, and replacement.

### Implement

Prefer small, auditable commits. Never manufacture historical telemetry. Never restore a secret, credential, or private mapping payload into the public repository.

For the Linguist/CedrLang lineage, the #154 70% `to_1337speak()` value is an initial rollout parameter for incremental character-level variability. Exact round-trip reconstruction remains the invariant.

### Wait / validate

A commit is not complete until the relevant GitHub checks have actually run and their terminal states have been re-fetched. A skipped provider, stale review, or missing run is `UNVERIFIED`, not green.

### Re-fetch / repeat

Every new head SHA starts a new evidence cycle. Reviews and comments must be associated with the current SHA where possible; outdated findings cannot be counted as current approval.

The loop stops only when:

- the branch is not behind `master`;
- current review threads are resolved or explicitly dispositioned;
- required checks are terminal and successful/accepted;
- generated indexes are regenerated from canonical sources;
- preserved artifacts have provenance;
- exact round-trip tests pass for each enabled codec layer;
- no actionable current review finding remains.

## Related automation

- `.github/workflows/pr-production-ledger.yml` — read-only SHA/timestamp/count ledger.
- `.github/workflows/pr390-master-realign.yml` — non-rewriting `master` convergence for PR #390.
- `.github/workflows/master-deletion-recovery.yml` — recovery of authoritative source/docs/tests without blind telemetry regeneration.
- `.github/workflows/agent-continuous-ops.yml` — unattended agent progression and debounce/loop controls.
- `.github/workflows/agent-feedback-linear-sync.yml` — review feedback projection into Linear.

## Provenance anchors

- PR #154 — historical Linguist/CedrLang and 70% diaspora evidence.
- Issue #175 — broader repair/alignment lineage.
- Issue #320 — notation taxonomy/Linguist research.
- Issue #324 — research/proposal expansion.
- PR #390 — production integration surface.
