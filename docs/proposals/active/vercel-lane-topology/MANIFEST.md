---
id: vercel-lane-topology
title: "Vercel deployment lane topology: legacy project fate, mcp-multi-host retirement, lanes registry"
author: Claude
posted_at: 2026-09-07
source: (none - direct proposal)
status: accepted
priority: P1
reviewers:
  - id: Claude
    role: author+driver
    status: posted
related_prs: [442, 445, 446]
related_branches:
  - docs/proposals/vercel-lane-topology
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — vercel-lane-topology

## Summary

One paragraph: mcp-hub now ships as its own dedicated Vercel project (see mcp-hub/README.md "Why a separate Vercel project"). That decision left two loose ends this proposal resolves: (1) what happens to the original, pre-existing termux-monorepo Vercel project (Root Directory still `deepseek-cli`, the folder documented in docs/CREDENTIAL-EXPOSURE.md as holding committed browser-profile/session data) now that it's not the vehicle for mcp-hub, and (2) whether the standalone mcp-multi-host repo (already redirected to point at mcp-hub per its own PR #1, merged 2026-09-07, by a separate concurrent agent/operator action) should now be archived. Also proposes a lightweight docs/DEPLOYMENT-LANES.md as the single source of truth going forward so a third Vercel-lane ambiguity doesn't recur.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| Claude | author+driver | accepted | 2026-09-07 | Opened proposal; self-executed the two reversible, Tier 1-2 items under merit path (see CONSENSUS.md); held VLT-001 for Tier 3 pending a second agent or Operator. |
| Operator (timerloggedout-spec) | reviewer+approver | accepted | 2026-09-07 | Direct chat authorization for VLT-001 after the peer-review pipeline was invoked twice and produced no substantive position (see DEBATE.md "Peer-review outcome"). Recorded VOTE in DEBATE.md. |

## Review log

### 2026-09-07 — Claude

- Disposition: posted
- Notes: Registering per PROCESS.md ingest→register→itemize lifecycle. See ITEMS.md for the three items and DEBATE.md for driver evidence. VLT-002 and VLT-003 are being executed in the same PR as this manifest since they are reversible/no-risk (repo archive is reversible via unarchive; a new docs file has no blast radius). VLT-001 is NOT executed here — proposed only, pending a second mind or Operator per Tier 3.

### 2026-09-07 — Claude (closing)

- Disposition: accepted
- Notes: Invoked `@gemini-cli`/`@deepseek-ci` twice for VLT-001; found and fixed a real repo-wide dispatch bug (`scripts/model_router.py` module-invocation, master `da89bab9`) along the way, but neither channel produced a substantive position (see DEBATE.md). Operator then gave direct authorization to resolve VLT-001 without further waiting. Executed: repointed the legacy project's Root Directory from `deepseek-cli` to `demo-portal/public` via the Vercel API, seeded with a real placeholder commit (`4abf90f1`), verified and redeployed. All three items now executed.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] At least one non-author review recorded (Operator decision, see Reviewers table)
- [x] Status -> accepted before VLT-001 execution merges
- [x] PRs cite `Implements: <ITEM-ID>` (this PR carries VLT-002, VLT-003; VLT-001 implemented via master commit `4abf90f1` + out-of-band API call)
- [x] Gates green on merge (docs-only change; repo-gate / proposal-lifecycle apply)
- [ ] Closed + moved to `closed/` when terminal (leave in `active/` for one more review cycle before archiving the folder)

## Links

- ITEMS: ./ITEMS.md
- Debate/votes: ./DEBATE.md
- Related: mcp-hub/README.md ("Why a separate Vercel project"), docs/CREDENTIAL-EXPOSURE.md, PR #442, mcp-multi-host PR #1
