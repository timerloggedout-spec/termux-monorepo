# Historical Context Coverage Bootstrap Request

**Purpose:** Wake the canonical, bounded Historical Context Relationship backfill after the coverage-ledger contract and its master-push trigger have been merged.

## Why this file exists

The canonical `workspace/llm_map/context_relationships/manifest.json` still represents a late-page legacy snapshot (observed at `2026-10-15T19:16:02.945529Z`, `history_window.start_page = 13`) and does not contain the new `history_coverage` ledger. The separate `temporal-current.json` value `coverage = COMPLETE` is not proof of a contiguous history prefix.

PRs #1618 and #1619 merged the continuity ledger and bootstrap path filter. The latest observed canonical manifest still lacks the ledger, so the required page-one bootstrap has not been evidenced by a resulting canonical manifest yet.

## Trigger semantics

This document is included in the path filter for `.github/workflows/context-relationship-backfill.yml`. Merging its first version on `master` should cause the workflow to run from canonical `master` and bootstrap from page 1 because the legacy manifest has no verifiable coverage chain.

This file is **not** a completion receipt and is not a command to repeat the bootstrap on every later run. The workflow remains page-bounded, serialized, and fail-closed.

## Required post-run verification

Do not mark the objective complete until a real Actions run and its resulting commit are observed. Verify:

1. the run used the current `master` lineage and expected source SHA;
2. the generated manifest includes `history_coverage.schema_version = "1.0"`;
3. the legacy late-page prefix is classified `UNVERIFIED` and the requested continuation starts at page 1;
4. the recorded coverage ledger advances only from collected evidence and preserves source SHA, observed-at timestamp, and input/manifest hashes;
5. validator and temporal snapshot agree on the current window;
6. `COMPLETE` is emitted only after a contiguous page-one chain reaches completion for both issues and pull requests;
7. the post-commit watcher re-fetches the exact resulting master SHA and verifies the manifest rather than inferring success from a green job alone.

If the push-triggered run does not appear, use the authorized workflow-dispatch path or diagnose the Actions trigger/permissions. Do not fabricate a run ID, edit generated coverage facts by hand, or promote a stale staging branch.
