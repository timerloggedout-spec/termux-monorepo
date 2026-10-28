# Platform201 MCP connection — full issue log from initial attempt
Compiled 2026-10-28 (Connector Specialist lane). Space: timerloggedout-space.
Target: MCP server https://api.platform201.com/mcp/v1 (Streamable HTTP, OAuth 2.0)
as Muse custom connector `custom.platform201`. No credential values appear
in this log — names/identifiers only, per fleet credential discipline.

## Established provider facts (firsthand)
- OAuth metadata: issuer https://api.platform201.com/mcp/oauth; authorize
  …/authorize; token …/token; register …/register; PKCE S256; token endpoint
  auth method: none; grants: authorization_code + refresh_token ONLY
  (no device-code, no client-credentials).
- Redirect allowlist (observed): localhost ✅; https://claude.ai/api/mcp/auth_callback ✅;
  https://agent.meta.ai/api/hatch/oauth/callback ❌.
- Docs position (verbatim): "There's no API key to manage: the server uses OAuth."
- Console check (2026-10-28, firsthand): Space Settings, Project Settings and
  Account Settings contain NO MCP/API-key/PAT section. OAuth is the only route.

## Issue log (chronological)
1. **Hosted Muse OAuth flow — DCR rejection.** Platform201's dynamic client
   registration rejects the Muse callback `https://agent.meta.ai/api/hatch/oauth/callback`
   (redirect_uri not allowed).
2. **Post-consent rejection (same flow).** Owner reached the allow screen,
   approved, and still received:
   {"error":"invalid_request","error_description":"redirect_uri is not allowed"}.
3. **Manual flow via localhost redirect — works up to code issuance.**
   client_id = owner kp_ User ID (an identifier, NOT a credential; Bearer test
   against the MCP endpoint → 401 "token could not be verified"; the endpoint
   verifies real JWT access tokens against JWKS at auth.platform201.com).
   Consent approved by owner ×3 for space timerloggedout-space; authorization
   codes issued (each ~4,934-char base64url JSON {n,e,p}).
4. **Transcription hazard (process issue, fixed).** One code was corrupted by
   hand-copying. Rule adopted: extract codes EXACTLY from session JSONL
   (~/agents/agent-*/sessions/*.jsonl, regex on state); never hand-copy.
   PKCE verifier is generated once and LOCKED until an exchange succeeds
   (overwriting it orphaned one otherwise-valid code).
5. **FINAL BLOCKER — token exchange from the agent VM fails.** POST to the
   token endpoint via the VM egress proxy returns, twice (python and curl):
   502 {"detail":"token refresh not allowed through egress proxy","error":"refresh_rejected"}.
6. **Alternate token hosts fail.** auth.platform201.com/oauth2/token → 400
   not_found; api.platform201.com/oauth2/token → 404.
7. **Browser route cannot relay.** Browser agents refuse to relay codes/tokens
   (policy, ×2). A VM listener on 127.0.0.1:8765 works locally, but the
   browser's Chromium is not on the VM's localhost (ERR_CONNECTION_REFUSED).
8. **Device route unavailable.** The owner's B160V device exposes no
   shell/HTTP command path for an exchange.
9. **Muse custom-connector setup (2026-10-28).** The generated
   `custom.platform201` OAuth setup uses the same rejected callback
   (agent.meta.ai/api/hatch/oauth/callback) — withheld from the owner rather
   than burning another authorize/consent cycle on a known failure.

## What would unblock (any one)
- Platform201 adds `https://agent.meta.ai/api/hatch/oauth/callback` to the
  MCP OAuth redirect allowlist; OR
- Platform201 issues any non-OAuth credential for the MCP server (docs say
  none exists today); OR
- An off-VM OAuth exchange path whose callback Platform201 already allows.

## Support ask (owner-approved 2026-10-28)
Allowlist the Muse callback above for the MCP OAuth server, and confirm the
credit-intake questions in the drafted inquiry (referral/invite/partner credit
programmes for existing Solo accounts; Redeem-coupon code sources; whether
the 14-day Pro trial remains claimable on an account that started on Solo).
