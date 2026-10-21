# Historical Backfill Promotion Gate

## Purpose

PR #523 must not promote the new master-anchored continuation layer while the existing `master-staging` historical backfill remains incomplete.

## Current evidence

- Authoritative `master` corpus snapshot: `next_start_page = 2`, observed `2026-08-19T07:53:15Z`.
- `master-staging` corpus is newer: observed `2026-09-07T12:33:24.770669Z`, but still reports `next_start_page = 2`.
- The old staging writer was manual-only and therefore could remain unchanged indefinitely.

## Immediate remediation

The staging writer now:

1. triggers on pushes to `master-staging` and manual dispatch;
2. reads `history_window.next_start_page` from the existing staging manifest;
3. never restarts from page 1 when a continuation page exists;
4. validates page advancement and canonical artifact/hash/count invariants;
5. commits only the validated corpus delta back to `master-staging`.

PR #523 also contains `historical-backfill-promotion-gate.yml`. That gate reads the authoritative `master-staging` manifest and fails while `next_start_page` is non-null. Therefore promotion is explicitly blocked until the current staging backfill reports `next_start_page = null`.

## Required state transition

`master-staging next_start_page=2`

→ execute page 2

→ validate authoritative effect

→ repeat from the newly committed `next_start_page`

→ `next_start_page=null`

→ promotion gate passes

→ only then can PR #523 establish the new master-anchored continuation layer.

A successful PR check, mergeability, or elapsed time is not evidence that the historical corpus completed.
