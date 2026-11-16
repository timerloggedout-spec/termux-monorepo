# Legacy mesh census suite — archive (provenance)

The original chat-side census tooling of the Integration Mesh Matrix lane
(2026-10-21 → 2026-10-23), archived in-repo 2026-10-28 under the owner's
all-work-in-repo order so the provenance of the matrix is reproducible by
any collaborator. **Superseded for live use** by the repo-native poll:
`../integration_mesh_poll.py` + `.github/workflows/integration-mesh-poll.yml`
(PR #1606 / #1608). Nothing here is wired into CI; these files are the
historical source the workflow port was built from, kept verbatim
(including their hardcoded workspace paths).

## Census scripts (run via the vault-backed PAT helper, names/metadata only)

| File | Role |
|---|---|
| `census.py` | v1 census: account, orgs, repo hooks/secrets(names)/workflows, check apps on recent heads, actors, deployments |
| `census2.py` | v2 full-pagination census: 30-head check apps, all-PRs/authors, submitted reviews (created frame), true-issue totals, new-app detail |
| `census3.py` | Personal-account census: cross-repo check-suite reach (60 pushed repos), sign-in surfaces |
| `secrets_plus.py` | Every secret-NAME store (repo/env/org/user) + Issue #184 body capture — names only, values never fetched |
| `reviews_updated.py` | Submitted-review census on the 150 most recently *updated* PRs |
| `apps_detail.py` | `/apps/{slug}` detail harvest for newly seen check apps |
| `mesh-installations-probe.yml` | One-shot Actions probe (2026-10-21) that established which stored token classes can read org installations; results on Issue #184 (comment 6321665538). Never landed on master as a standing workflow — the Actions workflow registry entry for it is a phantom for this branch-only file |

## One-off publishers (their outputs are the PRs/issues named in each file)

`publish_refresh.py` (#1508), `publish_probe.py`, `push_amendment.py`,
`push_amendment2.py`, `push_doc_update.py`, `push_review_fixes.py`,
`reply_resolve_threads.py`, `fix_i1.py` (#1545),
`publish_integration_mesh_poll.py` (#1606),
`publish_integration_mesh_poll_fix.py` (#1608).

## Intentionally NOT archived here

- **Census snapshot JSONs** (`census*.json`, `secrets_plus.json`,
  `reviews_updated.json`, `*.prev.json`, `org_installs.json`,
  `apps_detail.json`) — generated poller output. Per the owner's standing
  rule (matrix §9(4)) poller output is never committed: it burns
  Vercel/Render deploy quota. The live successors are the Actions poll's
  cache state + 30-day run artifacts.
- **Issue #184 dumps** (`issue184_body.txt`, `comments184*.txt/json`) —
  verbatim copies of content that lives on GitHub (Issue #184); the issue
  is the copy of record.
- **Superseded matrix drafts** (`INTEGRATION-MESH-MATRIX.md` pre-refresh
  copy, `matrix_refresh_*.md`) — drafts whose final content landed on
  master via refresh PRs #1508/#1539/#1542/#1555/#1578/#1583/#1601;
  master is the copy of record.
- `publish_spec.json` — a one-run parameter file for `push_doc_update.py`
  whose content is fully reflected in the PR it produced.
