# DEBATE — vercel-lane-topology

## Driver evidence (Claude, 2026-09-07)

- mcp-hub is confirmed live as its own Vercel project (production branch `master`, verified end-to-end with real MCP `initialize` handshakes against both `/mcp/termux` and `/mcp/android`). It no longer needs, and never used, the pre-existing termux-monorepo Vercel project.
- The pre-existing termux-monorepo Vercel project's Root Directory is confirmed (via its own preview deployment metadata) to still be `deepseek-cli` — the exact folder `docs/CREDENTIAL-EXPOSURE.md` documents as holding committed browser-profile data with live session state. Nothing in this session's work depends on that project staying as-is; nobody has come forward with a consumer of its current deployment output either.
- mcp-multi-host's own README (as of commit `1c83a01`, PR #1 in that repo, merged 2026-09-07) already states: "Folded into termux-monorepo's mcp-hub/... This repo is left in place, not deleted, pending a decision on archiving it." That decision is what VLT-002 closes out. No open PRs or recent non-docs commits exist against that repo beyond the redirect itself.
- VLT-001 is deliberately NOT self-executed here. Per `docs/CONSENSUS.md` Tier 3 ("P0 claims" is not quite this, but deleting/repointing a live, credential-exposure-adjacent Vercel project is treated the same way this session treated the Root Directory switch earlier in this work: irreversible-enough that a second mind should look before it happens, not after).

## Peer-review outcome (2026-09-07)

The on-demand agent pipeline (`@gemini-cli` / `@deepseek-ci`, `docs/ops/AGENT-MONIKERS.md`) was invoked twice on this PR asking specifically for a position on VLT-001. Neither produced one:

- **A real, repo-wide bug blocked the first attempt entirely**: `scripts/model_router.py` was being invoked as `python3 scripts/model_router.py` (puts `scripts/` itself on `sys.path[0]`, not the repo root), so `from scripts import capability_spine` raised `ModuleNotFoundError` on every dispatch. Fixed on master (`da89bab9`): `python3 -m scripts.model_router`.
- **DeepSeek CI dispatched successfully both times** (runs `34110775453`, `34111728927`) but failed at `create_chat_session` with `code=40003 "Authorization Failed (invalid token)"`. Root cause: the `ds_session_id` behind `DEEPSEEK_TOKEN_PRIMARY` is stale/invalid — most likely because the compromised session documented in `docs/CREDENTIAL-EXPOSURE.md` was correctly rotated, which invalidates any token captured from that exposed browser profile. This is the webWrapper (reverse-engineered, WASM PoW, no official API key by design) architecture working as intended and correctly rejecting a dead session — not a code defect. Needs a freshly-captured, clean cookie jar (not re-derived from the already-exposed profile data) set as `DEEPSEEK_COOKIES` before this channel can vote on anything.
- **After the dispatch fix, Gemini CLI did execute** (run `34114740900`, real ~10s model call, confirmed in job log) but its `invoke` role doesn't post a PR comment — that appears to require the `review`/`triage` roles, both of which stayed skipped on an `issue_comment` event shaped this way. No architectural opinion was produced.
- **CodeRabbit** reviewed the proposal documents themselves (5 findings, all formatting/process nits — addressed) but never took a position on VLT-001's substance; it isn't scoped to do that.

**Conclusion: the peer-review pipeline did not fail to answer — it was not currently capable of answering.** No second-agent vote exists for VLT-001 as of this proposal's resolution.

## Operator decision (2026-09-07)

VOTE: accept
by: Operator (timerloggedout-spec, via direct chat authorization — "VLT-001 has only been blocked by your choices. I've given authority for self auto approval.")
term: repoint, not archive

Resolution: repoint the legacy `termux-monorepo` Vercel project's Root Directory from `deepseek-cli` to `demo-portal/public` (a new, clean, minimal placeholder — see `docs/proposals/active/demo-portal/`), rather than archiving it. This both (a) immediately stops the project deploying a folder with committed browser-profile session data, and (b) reuses the slot for the Operator's demo-portal concept instead of creating and later re-deciding a fourth Vercel project. Executed via the Vercel API against project `prj_jNsCGw9QroJxn1356T4QPwe0X9zG` on 2026-09-07; verified `rootDirectory` field changed and a fresh production deployment was triggered from `master`.

## Votes

- Claude (driver): accept — repoint to demo-portal/public
- Operator (timerloggedout-spec): accept — see decision above
