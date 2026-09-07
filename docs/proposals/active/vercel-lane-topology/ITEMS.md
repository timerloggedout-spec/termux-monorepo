# ITEMS — vercel-lane-topology

| ID | Item | Tier (CONSENSUS.md) | Status | Notes |
|----|------|------|--------|-------|
| VLT-001 | Decide fate of the pre-existing termux-monorepo Vercel project (Root Directory currently `deepseek-cli`) now that mcp-hub has its own dedicated project: archive/delete the project, or repoint its Root Directory to a real folder and document it as an explicit lane, or leave as-is with rationale recorded | 3 (Quorum) | proposed, not executed | Irreversible-ish (Vercel project delete/repoint) touching the folder named in docs/CREDENTIAL-EXPOSURE.md. Needs a second agent's VOTE or Operator sign-off in DEBATE.md before execution. Do not action on driver-only say-so. |
| VLT-002 | Archive the standalone `mcp-multi-host` GitHub repo now that its README already redirects to mcp-hub (its own PR #1, merged) and it carries no server code of its own | 1-2 (Driver/Light) | executed in this PR | Reversible via GitHub unarchive; no code, no live traffic depends on it being unarchived. |
| VLT-003 | Add `docs/DEPLOYMENT-LANES.md`: one table listing every Vercel project tied to this GitHub org (project name, Root Directory, purpose, owning proposal/PR), so a future third lane doesn't repeat this ambiguity | 1 (Driver) | executed in this PR | Pure documentation, no blast radius. |

## Implements tags
This PR's commits/PR body cite `Implements: VLT-002` and `Implements: VLT-003`. VLT-001 has no implementing commit yet — it is registered as `proposed` only.