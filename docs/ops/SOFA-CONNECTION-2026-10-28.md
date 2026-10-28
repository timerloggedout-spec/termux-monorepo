# SOFA (Stack Overflow for Agents) — Muse connection record, 2026-10-28

[MUSEai]@{role:{inventory}}

- Surface: agents.stackoverflow.com (SOFA) — distinct from the standard user
  MCP at mcp.stackoverflow.com.
- Agent (existing, owner-ruled "use it"): `1337_inQuiπy_F1ⁿD3π+F1×3₹`,
  contributor, publication policy publish_directly. No new agent created.
- Route: OAuth 2.0 authorization_code + refresh_token, DCR-registered public
  client (token auth method none, PKCE S256), scopes sofa.read +
  sofa.identity.read + offline_access. MCP endpoint
  https://agents.stackoverflow.com/mcp.
- Provider constraint (firsthand): SOFA's DCR redirect allowlist accepts
  localhost only; hosted callbacks (agent.meta.ai, claude.ai, chatgpt.com,
  cursor.com) return invalid_redirect_uri, so Muse's hosted OAuth card flow
  cannot complete — same class as Platform201. Tokens were obtained via a
  localhost-redirect flow with the owner's signed-in browser consent; the
  token exchange requires the resource parameter (omitting it returns
  invalid_target). Refresh works from the agent VM and rotates.
- Connector: custom.stackoverflow-agents (local connector doc + helper
  bin/sofa.py: status/tools/call/refresh, auto-refresh). Token values are
  never recorded here or anywhere in the repo (names/status only).
- Verified 2026-10-28 firsthand: MCP initialize OK, tools/list = 27 tools,
  sofa_connection_status confirms the existing agent + scopes, refresh
  exchange OK. (First-day count of 28 was a miscount, corrected here.)
- Expansion landed same day: helper now carries typed coverage of all 27
  tools (schema snapshot + generated TOOLS.md in the connector dir; per-tool
  subcommands with named, JSON-coerced, required-checked args; curl
  transport). Live-verified reads: search, tags, guidance. Scope nuance:
  sofa_my_posts / sofa_get_draft additionally require sofa.draft.read —
  not granted; the 11 write-class tools (ask/reply/vote/verify/publish/…)
  remain owner-gated on scope widening, unchanged.
- API-key onboarding claim flow (agent-directed, /api/onboarding): owner
  claimed + authorized 2026-10-28, but the flow's poll token was lost in a
  local scratch cleanup before the claim completed, so the one-time auth
  code was never retrieved and no API key was issued. Redundant with the
  verified OAuth route; a fresh flow can be started if a key is ever wanted.
  Vote/write scopes were not requested.
