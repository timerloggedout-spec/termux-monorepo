# SOFA search findings — termux-monorepo benefit, 2026-10-28

[MUSEai]@{role:{sofa-search}}

Scope: timerloggedout-spec/termux-monorepo ONLY (owner correction
2026-10-28). Lane is read-only: granted scopes `sofa.read` +
`sofa.identity.read` + `offline_access`; no post/reply/vote/verify.
Connection record: docs/ops/SOFA-CONNECTION-2026-10-28.md.

## Method

- `sofa_guidance` first: status unknown, current skill digest
  `e8a0407f0cb57a59cd0e4ee69222f6e50d2173b00c0844758b4ea0e5e749c2f7`;
  followed the recommended `refresh_sofa_skill` action (skill.md fetched).
- Helper v1 defect (found firsthand): urllib transport died with
  IncompleteRead/RemoteDisconnected on large responses (search,
  tools/list). Helper v2 (Inventory lane, same day) replaced transport
  with curl and added typed coverage of all 27 tools; defect closed.
- Session summary at close: 33 searches, 5 posts consulted (server
  projection).

## Coverage inventory (tools/list = 27, firsthand)

- Identity/session (4): sofa_connection_status, sofa_guidance,
  sofa_session_summary, sofa_attention.
- Search/read (10): sofa_search, sofa_get_post, sofa_tags,
  sofa_list_agent_leaderboard, sofa_search_external_links,
  sofa_search_link_assessments, sofa_lookup_external_link,
  sofa_pull_playbook, sofa_list_related_playbooks, sofa_my_verifications.
- Own-content (3): sofa_my_posts, sofa_get_draft, sofa_revise_draft.
- Write (10): sofa_ask, sofa_publish_blueprint, sofa_share_til,
  sofa_publish_playbook, sofa_reply, sofa_edit_post, sofa_delete_post,
  sofa_vote, sofa_verify_post, sofa_verify_external_link.
- Probed OK: connection_status, guidance, session_summary, attention,
  tags, leaderboard, search, get_post, search_external_links,
  search_link_assessments.
- Gap: sofa_my_posts fails — additionally requires `sofa.draft.read`,
  not granted. Own-contribution readback is unavailable under the
  current grant. Flagged only; scopes NOT widened by this lane.
- Gap: all 10 write tools are listed but unusable under read-only
  scopes. Widening is owner-gated.
- Unprobed: sofa_pull_playbook, sofa_lookup_external_link (read-class,
  no args settled), sofa_my_verifications (requires post_id).

## Finds (query -> result -> repo benefit)

1. `MCP OAuth dynamic client registration redirect_uri`
   -> TIL 3bb244bd-9c32-4b68-86f3-097caccfd6e4 (unscored): SOFA's DCR
   rejected `localhost`, accepted `127.0.0.1` on the same port/path
   (HTTP 400 -> 201). Registration, authorization, and transport are
   separate stages; a later `invalid_target` was the resource
   parameter, not the callback.
   -> Repo: matches this repo's SOFA + Platform201 connector records
   (localhost-only DCR allowlist, resource param required at token
   exchange). Stage-separate OAuth diagnosis for all connector wiring.

2. `client ID metadata document CIMD MCP OAuth`
   -> No CIMD-specific posts. Nearest: TIL ab1d1ab3 (trust +27) and
   TIL daff9f94 (trust +15): Entra offers neither DCR nor CIMD, and
   Claude/ChatGPT/Copilot need neither — pre-registered clients suffice.
   -> Repo: do not build a CIMD/DCR facade for providers that lack it;
   per-provider pre-registration is the working pattern for the repo's
   MCP/connector wiring.

3. `private_key_jwt MCP OAuth client authentication`
   -> No dedicated posts; results were generic DCR/headless only.
   Gap recorded; no repo action.

4. `MCP client registration Claude ChatGPT Cursor provider differences`
   -> daff9f94: Claude = pre-registered public client, PKCE, callback
   `/api/mcp/auth_callback`; ChatGPT = user-defined OAuth client
   (secret if confidential), callback
   `/connector_platform_oauth_redirect`; Copilot = Entra SSO, no own
   client. ab1d1ab3: strict clients (ChatGPT/Mistral) fail on empty
   protected-resource-metadata `scopes_supported`, issuer byte-mismatch
   (trailing slash; RFC 8414 section 3.3), and missing
   `openid-configuration`; Claude masks the first by hardcoding
   `offline_access`. ChatGPT requests exactly the PRM-listed scopes;
   advertise `openid` + `offline_access`.
   -> Repo: audit all three discovery documents before blaming a
   client — applies to the repo's termux-mcp hub and any MCP server
   the repo ships.

5. `Remote MCP OAuth headless CLI CI`
   -> TIL 7109a8bb (trust +18): OAuth 2.1 DCR auth-code flow fails
   silently in headless/CI/cron runs (tool list empty; /authorize hit
   with no following /token exchange). Fix: pre-provisioned
   bearer/API-key credential injected via env at process startup.
   -> Repo: explains and validates the repo's localhost-token SOFA
   route; interactive OAuth must never be assumed in Actions, cron,
   or subagent lanes.

6. `OAuth loopback localhost 127.0.0.1 state`
   -> TIL b6c7dd4f (trust +60): OAuth state verification failed only
   on `127.0.0.1`, worked on `localhost` (cookie scoping) — the
   inverse of find 1. Check both host forms, per stage.
   -> Repo: connector sign-in debugging checklist.

7. `agent identity profile multi-client fleet`
   -> Question c5ab0937, top answer trust +55: single shared identity
   beats per-client registrations; sessions are per-invocation (no
   shared-session hazard), reputation is per agent_id with no merge
   later (splitting = repeated cold starts), and attribution survives
   only in public reply prose (verification feedback is private).
   -> Repo: validates the owner's use-the-existing-agent ruling for
   SOFA; lane attribution belongs in [MUSEai]@{role:...} prose, not
   in new SOFA identities.

8. `rate limit shared token quota`
   -> Results: log every request to a shared file and self-cap below
   the limit (example: 8 per rolling 10 min against a ~10 limit);
   read `RateLimit-*` headers before assuming a burst limit — quotas
   can be hours-long and scoped per key.
   -> Repo: Delphi gate `defer_api` posture and the shared PAT-helper
   rate budget (live-derived counts rule unchanged).

9. `Temporal workflow durable execution` and
   `weighted voting panel oracle Delphi`
   -> No Temporal-specific and no Delphi/weighting posts found.
   Generic durable-workflow posts only (stale-finalization writes,
   ledger/idempotency expiry, resume-by-worktree-inspection).
   Gaps recorded; no repo action.

## Standing use

Re-run repo-scoped searches when a lane hits a live pain in: MCP
OAuth/registration, connector wiring, quota/rate behaviour, Delphi/DoE
process, or challenge-entry tooling. Report format stays:
query -> post id + trust -> repo benefit/how.
