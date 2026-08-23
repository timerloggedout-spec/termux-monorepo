# Docs-branch index

Automated inventory of remote `docs/*` (and `docs-lane-*`) branches for navigation and amendment tracking. Policy: debate lanes stay until promoted; master holds pointers — see `docs/CONSENSUS.md` §10 and #175.

**Generated:** `pending-first-CI-run` UTC  
**Generator:** `scripts/ops/generate_docs_branch_index.py`  
**Repo:** `timerloggedout-spec/termux-monorepo`  
**Count:** (seed)

Do **not** hand-edit the generated table below. Amend via PR or registry.

<!-- BEGIN:docs-branch-index (generated; do not edit) -->

| Branch | SHA | Open PR(s) | Registry proposal(s) | Notes |
|--------|-----|------------|----------------------|-------|
| _seed — run `python3 scripts/ops/generate_docs_branch_index.py` or workflow `docs-branch-index`_ | — | — | — | placeholder |

<!-- END:docs-branch-index -->

## How this is maintained

- **CI:** `.github/workflows/docs-branch-index.yml` (schedule + `workflow_dispatch`).
- **Local:** `python3 scripts/ops/generate_docs_branch_index.py`
- **Check freshness:** `python3 scripts/ops/generate_docs_branch_index.py --check`
- **Promotion:** open a small PR from a docs lane → master; do not wholesale-merge.
- **Registry:** `docs/proposals/registry.yaml` `related_branches` / `source_branch`.

## Related

- Issue #175 (actions / lane visibility)
- `docs/CONSENSUS.md`
- `docs/ops/LANE_CONSOLIDATION_SSOT.md`
