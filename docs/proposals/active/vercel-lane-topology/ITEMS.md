# ITEMS — vercel-lane-topology

| ID | Item | Tier (CONSENSUS.md) | Status | Notes |
|----|------|------|--------|-------|
| VLT-001 | Decide fate of the pre-existing termux-monorepo Vercel project (Root Directory currently `deepseek-cli`) now that mcp-hub has its own dedicated project: archive/delete the project, or repoint its Root Directory to a real folder and document it as an explicit lane, or leave as-is with rationale recorded | 3 (Quorum) | executed | Peer-review pipeline invoked twice, produced no substantive position (see DEBATE.md "Peer-review outcome" — one real bug found+fixed along the way, one channel correctly hard-failed on a rotated/invalid session token, no comment-posting path for the other). Resolved by Operator decision recorded in DEBATE.md: repointed Root Directory from `deepseek-cli` to `demo-portal/public` via the Vercel API on 2026-09-07 (project `prj_jNsCGw9QroJxn1356T4QPwe0X9zG`), verified and redeployed. |
| VLT-002 | Archive the standalone `mcp-multi-host` GitHub repo now that its README already redirects to mcp-hub (its own PR #1, merged) and it carries no server code of its own | 1-2 (Driver/Light) | executed (out-of-band) | Archived via the GitHub API on 2026-09-07 (repo `archived: true`, confirmed via `GET /repos/timerloggedout-spec/mcp-multi-host`). Not in this PR's diff because a repo-archive flag is a GitHub API/settings action, not a file change — this PR documents the decision, the API call executed it. Reversible via GitHub unarchive. |
| VLT-003 | Add `docs/DEPLOYMENT-LANES.md`: one table listing every Vercel project tied to this GitHub org (project name, Root Directory, purpose, owning proposal/PR), so a future third lane doesn't repeat this ambiguity | 1 (Driver) | executed in this PR | Pure documentation, no blast radius. |

## Implements tags

This PR's commits/PR body cite `Implements: VLT-002` and `Implements: VLT-003`. VLT-001 is implemented by the `demo-portal` placeholder commit (`4abf90f1`, master) plus the out-of-band Vercel API call recorded in DEBATE.md.
