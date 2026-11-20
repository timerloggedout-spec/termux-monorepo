# Transport and Identity Decision Record

## Status

**Accepted for version one:** local Termux execution plus GitHub-backed structured jobs. **Deferred:** direct interactive agent transport. This decision keeps the BLU B160V private while the project develops a useful, free-tier automation baseline.

## Tailscale

The existing Tailscale API connector is an administrative control-plane integration. It can inspect the Android hub and, with explicit operator authorization, manage permitted temporary node/key lifecycle operations. It cannot create a route from an isolated agent sandbox to the phone by itself. The currently configured administrative API token is accepted only under the operator’s explicit authorization and must be migrated to tag-scoped OAuth trust credentials when the direct-control workflow is stable.

The Android device remains an authorized tailnet machine. It must not receive a router port-forward or public SSH exposure. Any future direct control host must validate the pinned OpenSSH host key and access only TCP port 8022 under a least-privilege tailnet grant.

## Cloudflare

The Cloudflare account is prepared but no active domain/site exists. The project will not use an unauthenticated quick tunnel or random public hostname for SSH or MCP administration. An authenticated Cloudflare Access tunnel is an optional later route after the user supplies an active site/domain and completes access policy configuration. The route must remain outbound-only from Android and preserve the `hub_mcp` capability envelope.

## Firebase and multi-factor authentication

Firebase account setup and user MFA/2SV enrollment remain human-operated. The project does not automate interactive MFA, capture second-factor secrets, scrape OTPs, or reverse engineer a user login session for `curl_cffi`, browser automation, or another client. Future automation must use a provider-supported machine identity, such as a restricted service account, workload identity, API key restricted to intended operations, or documented OAuth client credential. If an end-user product needs MFA, it must use Firebase/Identity Platform-supported enrollment and challenge flows with pricing reviewed before activation.

## Free-tier rule

The version-one delivery uses existing Termux, GitHub, and Tailscale resources. It does not depend on a paid VM, custom domain, 24/7 paid service, or hosted model. Any later service must be evaluated against a free/trial tier and documented before enablement.

## Direct transport options

| Option | Requirements | Current decision |
|---|---|---|
| Structured GitHub jobs | Private repository and local Termux polling/fetching through outbound HTTPS. | Active version-one path. |
| Private bridge host | An always-on user-controlled computer joined to the tailnet. | Deferred until such a host is available. |
| Authenticated Cloudflare Access tunnel | Cloudflare account, active domain/site, access policy, and `cloudflared` client on both ends. | Deferred; no public quick tunnel. |

## References

[1]: https://tailscale.com/docs/reference/tailscale-api "Tailscale API"
[2]: https://tailscale.com/docs/reference/trust-credentials "Tailscale trust credentials"
[3]: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-cloudflared-authentication/ "Cloudflare Access SSH"
[4]: https://firebase.google.com/docs/auth/web/multi-factor "Firebase multi-factor authentication"
