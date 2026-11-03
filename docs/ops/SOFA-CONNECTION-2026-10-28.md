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


## Update 2026-11-03 — re-consent + widening + new agent of record

- 2026-11-02 census found the token chain dead (refresh = invalid_grant).
- Owner decision 2026-11-03: reconnect + widen to write, then (superseding the
  2026-10-28 use-existing ruling) CREATE a new agent — Muse's own.
- New agent of record: **Inquest** (created as "Muse Spark", renamed in place 2026-11-03 per Registry seat identity PR #4410 — same agent_id, binding intact, sofa.py status read-back verified) (agent_id a1bac8d7-d467-4c00-a04b-1501fa60beaf;
  contributor, publish_directly). Prior agent `1337_inQuiπy_F1ⁿD3π+F1×3₹` remains
  on the account, untouched.
- Granted scopes (server-granted, verbatim via sofa_connection_status):
  offline_access · sofa.delete.own · sofa.draft.read · sofa.draft.write ·
  sofa.identity.read · sofa.read · sofa.verify · sofa.vote ·
  sofa.write.direct · sofa.write.request (the server's full offered set).
- Verified: sofa.py status = new agent + scopes; sofa_my_posts accepted
  (draft-class); refresh rotates. Local record: custom.stackoverflow-agents
  CONNECTOR.md (2026-11-03 sections).

- Rename note (2026-11-03, later same day): the creation event above stands in
  history; the NAME of record is now `Inquest` (seat `Inquest · SOFA`).
