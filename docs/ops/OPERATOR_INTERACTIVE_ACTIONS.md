# Operator Interactive Actions

## Purpose

Some external PR agents expose a provider-owned checkbox, button, or toggle instead of an API or comment command. The peer-review workflow records these controls as **pending operator actions** and waits for verified provider completion. It does not select controls, scrape browser state, or handle browser cookies.

> A copied checkbox in a GitHub comment is context only. The actionable target is the original provider comment/control, on the exact pull request SHA recorded in the peer-response state comment.

## Responsibilities

| Component | May do | Must not do |
| --- | --- | --- |
| `peer-review-orchestrator.yml` | Observe controls, publish the active PR/SHA state, ingest provider responses, and block downstream review. | Select UI controls, accept a relay as proof, or access browser cookies. |
| Operator Action Executor | Select an allowlisted provider control from an authorized, named account; then publish a constrained acknowledgement. | Reuse a different account, copy/export cookies, perform undeclared actions, or act on a stale SHA. |
| `gemini-after-peers.yml` | Run the second pass only after `responses_collected` and `ready: true`. | Treat timeout, acknowledgement, or a copied control as a completed response. |

## Authorized action procedure

1. Find the current `<!-- agent-peer-response-state:v2 -->` comment for the PR and confirm its `head_sha` matches the live PR head.
2. Confirm the provider, source URL, and `control_id` are present under **Authorized interactive controls**.
3. Use the named, approved operator profile for that provider. If the account is not signed in, lacks permission, or shows a different control, stop and report the state; do not substitute a different identity.
4. Select only the requested control. Capture the provider source URL and the visible after-action result for the audit trail.
5. Post the following acknowledgement from an `OWNER`, `MEMBER`, or `COLLABORATOR` account. Use the exact cycle and control values from the state comment.

```text
<!-- operator-action-ack:v1 -->
cycle_id: pr-<number>-<sha-prefix>
provider: <provider>
control_id: <provider-control-id>
action: <allowlisted-action>
```

6. Wait for provider output. The workflow will ingest a matching review, provider comment, or completed provider check. An acknowledgement only changes the state to `action_acknowledged`; it does not release downstream review.

## State meanings

| State | Meaning | Operator action |
| --- | --- | --- |
| `pending_operator_action` | A provider-owned control was found but has not been selected. | Review and act through the authorized provider UI. |
| `action_acknowledged` | A permitted UI action was acknowledged, but the provider has not completed review. | Wait for the provider response; investigate if it does not arrive. |
| `awaiting_provider_response` | No provider response has been ingested for one or more required providers. | Confirm provider configuration or resolve its operational blocker. |
| `responses_collected` | Every configured required provider has completion evidence for the active SHA. | No action; second pass is eligible. |

## Credential and account boundary

Keep browser profiles, cookies, session exports, and provider secrets out of GitHub Actions caches, artifacts, pull-request comments, and `refTemplates`. A multi-account setup must use distinct, named profiles and a policy mapping from provider/action to profile; it must never use cookie copying as account routing.

The executor may record only non-secret operational evidence: cycle ID, provider, source URL, control ID, actor profile label, timestamps, and terminal provider URL/check. Follow `SECURITY.md` for credential handling and use the repository’s credentialing opt-in path for any credential-related maintenance.
