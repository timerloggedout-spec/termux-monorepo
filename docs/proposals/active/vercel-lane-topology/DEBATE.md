# DEBATE — vercel-lane-topology

## Driver evidence (Claude, 2026-09-07)

- mcp-hub is confirmed live as its own Vercel project (production branch `master`, verified end-to-end with real MCP `initialize` handshakes against both `/mcp/termux` and `/mcp/android`). It no longer needs, and never used, the pre-existing termux-monorepo Vercel project.
- The pre-existing termux-monorepo Vercel project's Root Directory is confirmed (via its own preview deployment metadata) to still be `deepseek-cli` — the exact folder `docs/CREDENTIAL-EXPOSURE.md` documents as holding committed browser-profile data with live session state. Nothing in this session's work depends on that project staying as-is; nobody has come forward with a consumer of its current deployment output either.
- mcp-multi-host's own README (as of commit `1c83a01`, PR #1 in that repo, merged 2026-09-07) already states: "Folded into termux-monorepo's mcp-hub/... This repo is left in place, not deleted, pending a decision on archiving it." That decision is what VLT-002 closes out. No open PRs or recent non-docs commits exist against that repo beyond the redirect itself.
- VLT-001 is deliberately NOT self-executed here. Per `docs/CONSENSUS.md` Tier 3 ("P0 claims" is not quite this, but deleting/repointing a live, credential-exposure-adjacent Vercel project is treated the same way this session treated the Root Directory switch earlier in this work: irreversible-enough that a second mind should look before it happens, not after).

## Votes

_(none yet)_
