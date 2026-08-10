---
id: leaderboard-aggregation
title: "Public leaderboard aggregation protocol (reporting features only)"
author: jules
posted_at: 2026-08-10
source: source.md
status: posted
priority: P2
reviewers:
  - id: jules
    role: author
    status: posted
  - id: devin-review
    role: reviewer
    status: changes_requested
related_issues: [122]
related_prs: [123]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — leaderboard-aggregation

## Summary

Aggregate a small set of documented, machine-readable public LLM benchmark
leaderboards (Hugging Face dataset leaderboard API, LiveBench, a HELM release
summary, and optionally Artificial Analysis behind an operator-provided key)
into a compact, generated `docs/leaderboard.md`. Public leaderboard values are
**features for reporting only**. They never replace or feed
`docs/schemas/model-success-matrix.yaml` / the internal ELO++ (3L0) index used
by `scripts/model_router.py` for triage/review/invoke routing decisions.
`docs/schemas/llm-leaderboard-matrix.yaml` (added under `LBA-01`) is the
schema for the public, feature-only data; it is a distinct artifact from the
routing matrix and must never be merged into or read by the router.

## Scope boundaries (acceptance criteria)

- Public leaderboard values are features for reporting. They do not replace
  internal ELO++/3L0 routing labels in `docs/schemas/model-success-matrix.yaml`.
- Phase 1 supports only documented machine-readable sources (no browser
  scraping, no inferred/undocumented APIs, no source requiring an API key
  that is unavailable to this repository).
- Phase 1 does not commit raw API responses, credentials, unbounded history,
  or generated Parquet files to git. Parquet, if produced, is a
  retention-bounded CI artifact only.
- This proposal must reach `accepted` before any `LBA-02`..`LBA-05`
  implementation work begins.
- All implementation commits and the implementation PR must cite
  `Implements: LBA-xx`.
- The implementation PR must target `master-staging`.
- The all-zero-weight configuration must not synthesize an average; it must
  emit `composite_rank: null` plus coverage metadata until at least one
  benchmark weight is positive.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| jules | author | posted | 2026-08-10 | Carried the original automation blueprint into PR #123 |
| devin-review | reviewer | changes_requested | 2026-08-10 | Technical planning review; see Review log |

## Review log

### 2026-08-10 — jules (source blueprint recorded)

- Disposition: **posted**
- The full automation blueprint (endpoint list, raw/processed Parquet schema,
  zero-weight ranking config, `update_leaderboard.yml` sketch) that was
  pasted into PR #123 is recorded verbatim in `./source.md` as the source
  proposal for this item. It is background only — see Scope boundaries above
  for what phase 1 actually implements.

### 2026-08-10 — devin-review (technical planning review)

- Disposition: **changes_requested**
- The aggregator must be a separate P2 proposal; it must not change routing
  authority. `docs/schemas/llm-leaderboard-matrix.yaml` defines public
  leaderboard data as features only; `docs/schemas/model-success-matrix.yaml`
  and internal ELO++/3L0 remain the routing labels.
- Two repository conditions currently block implementation on this branch:
  1. No accepted, itemized proposal existed for this system (this MANIFEST +
     `ITEMS.md` close that gap by registering one at `status: posted`).
  2. The documented gate files (`scripts/ci/repo_gate.py`,
     `scripts/ci/termux_smoke.py`) are absent from this checkout, so the
     required gate commands cannot be verified here. Verification is
     inconclusive until the integration branch or restored gate files are
     available.
- Phase-1 implementation must not commit daily Parquet history (no
  data-retention policy exists yet); publish compact Markdown, upload data
  snapshots as retention-bounded workflow artifacts, and store only source
  configuration/schema/methodology in git.
- The all-zero configuration must not compute a synthetic average; it must
  emit `composite_rank: null` and coverage metadata until one or more
  benchmark weights are positive.
- Given the above, this change registers the proposal only (`LBA-01`) and
  defers `LBA-02`..`LBA-05` (source collection, ranking, workflow, tests)
  until the proposal is `accepted` and the gate files are restored.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized (`LBA-01`..`LBA-05`)
- [x] At least one non-author review recorded (devin-review, changes_requested)
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge (blocked: `scripts/ci/repo_gate.py` /
      `scripts/ci/termux_smoke.py` absent from this checkout)
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md