# Stack Overflow for Agents (SOFA) — custom.stackoverflow-agents

SOFA is agents.stackoverflow.com — a knowledge exchange for AI agents. DISTINCT
from the standard user MCP at mcp.stackoverflow.com (so_search/get_content).

## Route (why not the hosted card)
SOFA's OAuth server (issuer https://agents.stackoverflow.com; authorize/token/
register under /mcp/oauth/) supports DCR + PKCE S256 + CIMD, token auth methods
none / private_key_jwt. Firsthand 2026-10-28: its DCR redirect allowlist accepts
**localhost only** — https://agent.meta.ai/api/hatch/oauth/callback, claude.ai,
chatgpt.com and cursor.com callbacks all return `invalid_redirect_uri`. So
Muse's hosted OAuth card flow cannot complete (same class as Platform201).
The API-key onboarding route exists (skill.md: /api/onboarding claim flow).
Owner claimed + authorized it 2026-10-28, but the flow's poll token was lost
in a local scratch cleanup before retrieval, so no API key was issued —
redundant with the verified OAuth route; start a fresh flow if a key is ever
wanted (and keep its poll token until registration completes).

## Working flow (landed 2026-10-28)
1. DCR-registered public client (client_id in bin/sofa.py; auth none) with
   redirect http://localhost:8765/callback, scopes sofa.read +
   sofa.identity.read + offline_access.
2. Owner's signed-in browser consented for the EXISTING agent
   `1337_inQuiπy_F1ⁿD3π+F1×3₹` (contributor, publish_directly). New agent was
   explicitly ruled out by the owner.
3. Code captured exactly from the parked browser tab URL after the expected
   ERR_CONNECTION_REFUSED redirect (browser agents do not relay codes).
4. Token exchange requires the `resource=https://agents.stackoverflow.com/mcp`
   parameter — omitting it returns `invalid_target`. Codes are single-use;
   a mid-flight connection drop consumes them (round 1 lost this way).
5. Refresh works from the VM and rotates the refresh token.

## Credential storage
Tokens live in `.tokens.json` next to this file (0600, git-ignored by location —
never commit, never print values). This is the Platform201-class exception:
no vault-registered connection exists because the hosted registration flow is
blocked by the provider's redirect allowlist.

## Use
`bin/sofa.py` — typed coverage of all **27** MCP tools (schema snapshot in
`tools-schema.json`, generated table in `TOOLS.md`):
- `status` — sofa_connection_status (identity/scope verify)
- `tools` — names + scope class; `describe <tool>` — full description + typed params
- `<tool> --param value ...` (or `call <tool> ...`) — named args, JSON-coerced,
  required-checked client-side; auto-refresh when <120s from expiry
- Transport is curl: urllib POSTs to the token endpoint intermittently die
  with RemoteDisconnected through the VM egress proxy; curl is reliable.

Scope classes (granted: sofa.read + sofa.identity.read + offline_access):
- READ (16): run now — search, get_post, tags, guidance, attention,
  session_summary, pull_playbook, related playbooks, external-link search/
  assessments/lookup, my_verifications, leaderboard, connection_status.
  Exception: `sofa_my_posts` + `sofa_get_draft` additionally require
  **sofa.draft.read** (verified live: insufficient_scope) — not granted.
- WRITE (11): typed + callable, server rejects — ask, reply, edit/delete post,
  publish blueprint/playbook, share TIL, revise draft, vote, verify post,
  verify external link. Scope widening (sofa.vote / sofa.write.* / sofa.draft.*)
  is **owner-gated**; not requested.

## Verified
2026-10-28: initialize OK (protocol 2025-03-26), tools/list = 27 tools,
sofa_connection_status confirms the existing agent + scopes, refresh exchange
OK, live calls OK: sofa_search, sofa_tags, sofa_guidance. (An earlier count of
28 in the first-day record was a miscount; corrected in repo PR.)
