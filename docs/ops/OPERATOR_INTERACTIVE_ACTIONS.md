# OPERATOR Provider Review Execution

## Purpose

The repository has one operational device: the **BLU B160V Android Termux hub**. The user is **not** an execution fallback. GitHub Actions uses the existing full-scope OPERATOR token to autonomously invoke every provider’s documented GitHub-side review command, publish SHA-bound state, and ingest evidence. The Termux hub is a separate fallback lane only for a provider authentication, MFA/2FA/2SV, or UI operation that has no documented GitHub command or API path.

> A full-scope GitHub token authorizes GitHub API operations. It does not confer authority to mutate a provider-owned checkbox. The peer gate uses documented provider commands rather than emulating a provider UI or copying checkbox markup.

## Execution ownership

| Component | Required responsibility | Boundary |
|---|---|---|
| `peer-review-orchestrator.yml` | Detect every required provider, post one SHA-bound documented trigger command per provider through the OPERATOR token, ingest evidence, and fail while review is unresolved. | Does not use browser state, emulate provider controls, or claim that a request is a completed review. |
| `agent-continuous-ops.yml` | Once per scheduled sweep, parse an elapsed CodeRabbit cooldown and post one marked OPERATOR-token retry for that exact cooldown source. | Does not retry early or loop identical requests. |
| BLU B160V Termux OPERATOR lane | Handle a provider operation only when no supported GitHub comment/API trigger exists: device-local login, MFA/2FA/2SV, or a provider-owned UI action. | Uses named device-local profiles; never exports cookies or session stores to Actions, Git, comments, artifacts, or `refTemplates`. |
| User | Receives escalation only when both the documented GitHub trigger and the Termux OPERATOR fallback are unavailable, or a provider explicitly requires unrecoverable user-only verification. | Never the normal review-trigger executor. |

## Documented provider-command contract

| Provider | Autonomous OPERATOR command | Completion evidence |
|---|---|---|
| CodeRabbit | `@coderabbitai full review` | Current-SHA substantive CodeRabbit review or provider check; cooldown notices are non-completing. |
| Qodo | `/agentic_review` | Current-SHA substantive Qodo review/comment or provider check. |
| Devin | `/devin review` | Current-SHA Devin review/comment or provider check. The OPERATOR identity must satisfy Devin’s linked-account write-permission prerequisite. |

Every request has an `<!-- operator-provider-review:v1 -->` marker containing the active cycle ID, head SHA, provider, and `trigger_review` action. The orchestrator posts at most one such command for each provider/cycle/SHA, so event retries remain idempotent. A provider request is acknowledgement only; `responses_collected` is the sole completion state.

## CodeRabbit cooldown contract

1. When CodeRabbit returns a review-limit/cooldown notice, the peer gate classifies it as `provider_cooldown`.
2. The hourly continuous OPERATOR sweep waits for the stated interval and posts one marked `@coderabbitai full review` retry for that exact cooldown source.
3. The gate accepts only current-SHA substantive provider evidence. Checkbox notices, acknowledgement notices, and cooldown notices do not release the peer gate.
4. Only `responses_collected` with `ready: true` may dispatch the verified second-pass workflow.

## Termux-only fallback contract

Use the Android device lane only for a provider that cannot be requested through a documented GitHub comment/API path. The device service consumes the current `<!-- agent-peer-response-state:v2 -->` comment, verifies the live `head_sha`, provider, `cycle_id`, and action allowlist, then acts through its named device-local profile. Any MFA/2FA/2SV challenge stays on-device. The service returns only non-secret completion metadata: cycle ID, provider, source URL/control ID, action timestamp, and terminal provider URL/check.

The service must reject a stale SHA, an unknown provider/action tuple, an unrecognized profile, or any request to copy cookies, session exports, or OTP material. If it cannot complete a provider action, it leaves the gate blocked and writes a precise non-secret failure state for OPERATOR triage. It does not transfer work to the user by default.

## Required configuration

Use the established full-scope token priority: `ARCHWIZ_GITHUB_TOKEN`, then `OPERATOR_GITHUB_TOKEN`, then `OPERATOR_TOKEN`. Each is a GitHub API credential only, with the permissions necessary to create/update pull-request comments and dispatch `gemini-after-peers.yml`; it is not a provider-browser credential. Set `PEER_STATE_PUBLISHER_LOGINS` to the exact token identity used to post authenticated gate state.

The default `OPERATOR_ALLOWED_ACTIONS` allowlist is `coderabbit:trigger_review,qodo:trigger_review,devin:trigger_review`. Remove a tuple only when the repository deliberately disables that provider. `peer-review-orchestrator / collect-peer-responses` fails closed if no authorized publisher token is available.

To make the gate merge-enforcing, configure `peer-review-orchestrator / collect-peer-responses` as a required branch-protection or ruleset status check. A passing state requires `responses_collected` and `ready: true`; neither a command comment, checkbox edit, acknowledgement, nor cooldown notice is merge-ready.

## Security boundary

Keep browser profiles, cookies, session exports, device keys, MFA/2FA/2SV secrets, and provider secrets on the BLU B160V Termux device. Do not place them in GitHub Actions secrets unless they are a deliberately scoped API/PAT credential, and never write them to Git, comments, caches, artifacts, or `refTemplates`. The GitHub workflow and Termux lane communicate only through attributable GitHub state comments and provider evidence URLs.

## References

[1]: https://docs.qodo.ai/code-review/use-qodo-in-prs/code-review "Qodo: How to run a code review"
[2]: https://docs.devin.ai/work-with-devin/devin-review "Devin Review"
