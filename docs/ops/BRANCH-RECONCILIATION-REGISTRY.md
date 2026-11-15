# Branch Reconciliation Registry

This is the programmatic branch-accounting gate for `timerloggedout-spec/termux-monorepo`.

## Run locally

Requirements: authenticated GitHub CLI (`gh`), Git, Python 3.10+.

```bash
gh auth status
python scripts/branch_reconciliation_registry.py \
  --repo timerloggedout-spec/termux-monorepo \
  --default-branch master
```

Outputs:
- `artifacts/branch-reconciliation/inventory.json`: versioned machine-readable registry.
- `artifacts/branch-reconciliation/inventory.md`: human triage report.

## Decision policy

Every remote branch is inventoried from GitHub's paginated branches endpoint. All pull requests (open, closed, and merged) are associated by head branch. Git ancestry is compared with the default branch after fetching remote branch refs.

| Disposition | Meaning | Required action |
|---|---|---|
| `ahead-only` | Branch has commits not in default | Review unique commits and tests; determine promotion target |
| `diverged` | Branch and default both have unique commits | Reconcile against its declared PR base; resolve conflicts and semantic overlap |
| `behind-only` | No branch-only commits relative to default | Retain history; verify PR/issue/context before archival |
| `identical` | Same commit tip as default | Retain history; verify references before archival |
| `unresolved-local-ref` | API tip and fetched local ref do not agree | Re-fetch and investigate; never infer disposition |
| `unrelated-or-unavailable-history` | No usable merge base | Investigate shallow/missing/unrelated history |

## Promotion is a separate gate

This tool is intentionally read-only. It never merges, closes PRs, pushes commits, or deletes branches. Before promotion, reviewers must inspect:
1. Unique commits and changed paths, including cherry-picks and equivalent patches.
2. The PR's declared base (which may not be the default branch).
3. CI/checks on the exact head SHA, review state, conflicts, and required approvals.
4. Whether the work is already integrated, superseded, duplicated, intentionally deferred, or rejected—with evidence and links.
5. Runtime/production rollout and rollback requirements where applicable.

A branch is not disposable merely because it is behind, has no open PR, or has a similar name. Unknown means unresolved, not stale. No automatic promotion or deletion is permitted by this registry.
