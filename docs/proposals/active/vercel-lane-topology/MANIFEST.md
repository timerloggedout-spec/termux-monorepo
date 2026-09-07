---
id: vercel-lane-topology
title: "Vercel deployment lane topology: legacy project fate, mcp-multi-host retirement, lanes registry"
author: Claude
posted_at: 2026-09-07
source: (none - direct proposal)
status: posted
priority: P1
reviewers:
  - id: Claude
    role: author+driver
    status: posted
related_prs: [442, 445, 446]
related_branches:
  - docs/proposals/vercel-lane-topology
gates_required: [repo-gate]
---

# MANIFEST — vercel-lane-topology

## Summary

One paragraph: mcp-hub now ships as its own dedicated Vercel project (see mcp-hub/README.md "Why a separate Vercel project"). That decision left two loose ends this proposal resolves: (1) what happens to the original, pre-existing termux-monorepo Vercel project (Root Directory still `deepseek-cli`, the folder documented in docs/CREDENTIAL-EXPOSURE.md as holding committed browser-profile/session data) now that it's not the vehicle for mcp-hub, and (2) whether the standalone mcp-multi-host repo (already redirected to point at mcp-hub per its own PR #1, merged 2026-09-07, by a separate concurrent agent/operator action) should now be archived. Also proposes a lightweight docs/DEPLOYMENT-LANES.md as the single source of truth going forward so a third Vercel-lane ambiguity doesn't recur.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| Claude | author+driver | posted | 2026-09-07 | Opened proposal; self-executing the two reversible, Tier 1-2 items now under merit path (see CONSENSUS.md); holding VLT-001 for Tier 3 (quorum: second agent OR Operator) because it is a destructive, likely-irreversible action (deleting or repointing a live Vercel project) touching a project whose current root is the subject of an existing credential-exposure finding. |
| (open) | reviewer | requested | | Any agent picking up registry.yaml next, or the Operator, may record a VOTE in DEBATE.md for VLT-001. |

## Review log

### 2026-09-07 — Claude

- Disposition: posted
- Notes: Registering per PROCESS.md ingest→register→itemize lifecycle. See ITEMS.md for the three items and DEBATE.md for driver evidence. VLT-002 and VLT-003 are being executed in the same PR as this manifest since they are reversible/no-risk (repo archive is reversible via unarchive; a new docs file has no blast radius). VLT-001 is NOT executed here — proposed only, pending a second mind or Operator per Tier 3.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded (open — see Reviewers table)
- [ ] Status -> accepted before VLT-001 execution merges
- [x] PRs cite `Implements: <ITEM-ID>` (this PR carries VLT-002, VLT-003)
- [x] Gates green on merge (docs-only change; repo-gate / proposal-lifecycle apply)
- [ ] Closed + moved to `closed/` when terminal (VLT-001 still open)

## Links

- ITEMS: ./ITEMS.md
- Debate/votes: ./DEBATE.md
- Related: mcp-hub/README.md ("Why a separate Vercel project"), docs/CREDENTIAL-EXPOSURE.md, PR #442, mcp-multi-host PR #1