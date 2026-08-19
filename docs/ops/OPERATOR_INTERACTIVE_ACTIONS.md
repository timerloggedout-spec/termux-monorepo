# OPERATOR Provider Review Execution

## Purpose

The repository has one operational device: the **BLU B160V Android Termux hub**. The user is **not** an execution fallback. GitHub Actions uses the existing full-scope OPERATOR token to make supported GitHub-side requests; the Termux hub is reserved for the separate device-local automation lane that must handle a provider login, MFA/2FA/2SV, or a provider UI control for which no supported GitHub-side command exists.

> A full-scope GitHub token authorizes GitHub API operations. It does not confer authority to mutate a CodeRabbit-owned comment or expose an unsupported GitHub task-checkbox mutation. The peer gate therefore uses CodeRabbit's documented `@coderabbitai full review` command as its primary trigger instead of trying to tick the provider checkbox.

## Execution ownership

| Component | Required responsibility | Boundary |
| --- | --- | --- |
| `peer-review-orchestrator.yml` | Detect a CodeRabbit control, publish SHA-bound state, post one marked `@coderabbitai full review` request with the OPERATOR token, ingest evidence, and fail while review is unresolved. | Does not use browser state or claim that a request is a completed review. |
| `agent-continuous-ops.yml` | Once per scheduled sweep, parse an elapsed CodeRabbit cooldown and post one marked OPERATOR-token `@coderabbitai full review` retry for that exact cooldown source. | Does not retry early, loop identical requests, or use the user account. |
| BLU B160V Termux OPERATOR lane | Handle only provider operations that lack a supported comment/API route: device-local login, MFA/2FA/2SV, or a provider-owned UI action. Post constrained completion evidence through the existing OPERATOR token. | Uses named device-local profiles; never exports cookies or session stores to Actions, Git, comments, artifacts, or `refTemplates`. |
| User | Receives escalation only when the Termux OPERATOR lane is unavailable or a provider explicitly requires an unrecoverable user-only verification. | Must not be used as the normal checkbox/retry executor. |

## CodeRabbit contract

1. When CodeRabbit exposes `> - [ ] <!-- {"checkboxId":"…"} --> 🔍 Trigger review`, the peer gate creates one `<!-- operator-coderabbit-review:v1 -->` comment for the active PR/SHA with `@coderabbitai full review`. This is the preferred supported OPERATOR trigger and must be attempted before any device-local checkbox fallback.
2. A checked form, `> - [x] <!-- {"checkboxId":"…"} --> 🔍 Trigger review`, is useful audit evidence that a UI action occurred, but it is **not** review completion and does not release the peer gate.
3. The gate accepts only current-SHA substantive CodeRabbit review evidence. Checkbox notices, acknowledgement notices, and `Review limit reached` / `Next review available in` messages are non-completing states.
4. A cooldown becomes `provider_cooldown`. The hourly continuous OPERATOR sweep waits until the stated interval has elapsed and posts one marked `@coderabbitai full review` retry. It then waits again for substantive output.
5. `responses_collected` is the sole completion state. Only then may the verified second-pass workflow be dispatched.

## Termux-only fallback contract

Use the Android device lane only for a provider that cannot be requested through a supported GitHub comment/API path. The device service consumes the current `<!-- agent-peer-response-state:v2 -->` comment, verifies the live `head_sha`, provider, `cycle_id`, and action allowlist, then acts through its named device-local profile. Any MFA/2FA/2SV challenge stays on-device. The service returns only non-secret completion metadata: cycle ID, provider, source URL/control ID, action timestamp, and terminal provider URL/check.

The service must reject a stale SHA, an unknown provider/action tuple, an unrecognized profile, or any request to copy cookies, session exports, or OTP material. If it cannot complete a provider action, it leaves the gate blocked and writes a precise non-secret failure state for OPERATOR triage. It does not transfer work to the user by default.

## Required configuration

Use the established full-scope token priority: `ARCHWIZ_GITHUB_TOKEN`, then `OPERATOR_GITHUB_TOKEN`, then `OPERATOR_TOKEN`. Each is a GitHub API credential only, with the permissions necessary to create/update pull-request comments and dispatch `gemini-after-peers.yml`; it is not a provider-browser credential. Set `PEER_STATE_PUBLISHER_LOGINS` to the exact token identity used to post authenticated gate state. `peer-review-orchestrator / collect-peer-responses` fails closed if no authorized publisher token is available.

To make the gate merge-enforcing, configure `peer-review-orchestrator / collect-peer-responses` as a required branch-protection or ruleset status check. A passing state requires `responses_collected` and `ready: true`; neither a command comment, checkbox edit, acknowledgement, nor cooldown notice is merge-ready.

## Security boundary

Keep browser profiles, cookies, session exports, device keys, MFA/2FA/2SV secrets, and provider secrets on the BLU B160V Termux device. Do not place them in GitHub Actions secrets unless they are a deliberately scoped API/PAT credential, and never write them to Git, comments, caches, artifacts, or `refTemplates`. The GitHub workflow and Termux lane communicate only through signed/attributable GitHub state comments and provider evidence URLs.
