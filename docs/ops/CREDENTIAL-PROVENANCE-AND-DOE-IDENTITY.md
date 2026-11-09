# Credential provenance × DoE configured-instance identity

**Status:** additive contract proposal; no credential values or live secret changes.
**Parent:** credential inventory issue #184; quota attribution contract; chat provenance v1.
**Purpose:** make PAT/App use attributable to the *consumer that made each request* without pretending GitHub can split a shared user-token bucket.

## Executive decision

Credential ownership, agent identity, inference endpoint identity, and execution identity are four different dimensions. Keep them separate and join them only through a dispatch-time record:

1. **Credential principal** — the GitHub user, GitHub App installation, Actions job token, or OAuth client that authenticated.
2. **Consumer identity** — the configured agent instance: signed moniker + role + DoE prompt/tools refs + context.
3. **Inference identity** — provider, model/version, endpoint, and non-secret inference-settings digest.
4. **Execution identity** — repository, workflow/run/attempt/job/step, event, and source SHA.

The event envelope in `schemas/ops/credential-use-provenance.schema.json` is the proposed canonical join record. It is a *reference and observation contract*, not a token inspector.

## Hard security boundary

Never record or derive a credential fingerprint from the credential value. Specifically, do not emit:
- token/PAT values, prefixes, suffixes, last-four characters, hashes, HMACs, or equality verdicts;
- authorization headers, request bodies containing credentials, cookies, private keys, or secret-store values;
- raw prompts, completions, or private context.

A `credential.ref` is a random/stable opaque identifier assigned by the operator in a names-only mapping. It is not computed from the secret. `credential.name` is the Actions secret or configured credential *name* only. `rotation_epoch` is a manually advanced, non-secret generation label (for example `2026q4-r1`), never a token-derived fingerprint. If the mapping is absent, use `null` and report `unmapped`; do not infer equality from matching names or aliases.

## DoE competition unit

The competition unit is the **configured inference instance**, not merely a model name and not merely an agent moniker:

`provider + model@version + endpoint_id + settings_digest + moniker + role + context + system_prompt_ref/hash + tools_ref/hash`.

The provider's model/version remains verbatim. `settings_digest` is a SHA-256 of a canonical, sanitized settings document after excluding credentials, headers, prompt content, private context, and other secret-bearing values. Prompt/tools content hashes follow the existing DoE ref scheme; only hash the exact dispatched content when it is retrievable. Missing evidence remains null/NOT ESTABLISHED.

An agent such as `[MUSEai]@{role:{<moniker>}}` is the **consumer**. It is not the credential principal. The same credential can serve several consumers; the same consumer can legitimately use different credential principals across provider routes. The four dimensions must not be collapsed.

## Attribution and confidence

Every dispatch that can make a billable, quota-consuming, or privileged API request emits the envelope before the request. The record includes:
- opaque credential ref + secret/config name + auth mode + principal kind/id, when known;
- signed moniker, role, context, DoE `instance_key`, prompt/tools refs and hashes;
- provider, model/version, endpoint id and sanitized settings digest;
- workflow/run/attempt/job/step, event, repository and exact source SHA;
- measured usage and its unit/window/source, or an explicit null reason;
- evidence legs and attribution state.

Attribution is **exact** only when the credential mapping and consumer stamp are both present and the execution join is unique. A GitHub actor, commit author, PR author, workflow actor, moniker, or secret name alone is not sufficient to prove which process used a credential. Preserve `single-leg`, `disputed`, `unattributed`, and `unmapped` outcomes. Never promote a display moniker to a GitHub account identity.

For shared PATs, one `credential.ref` can appear on multiple consumer records. The local dispatch ledger can attribute future requests by the signed consumer stamp; GitHub's aggregate user-token rate bucket still cannot provide a retroactive per-agent split. Keep aggregate GitHub readings separate from self-stamped per-dispatch usage. No historical burn reconstruction.

## Human collaborator reconciliation

The currently supplied operator context identifies `credkellar` as the only other human collaborator. Treat that as an operator-provided roster fact, not as proof of a particular event or token use. Previously observed unknown identities remain unresolved until a GitHub audit event or other independent source identifies the authenticated human. Do not attribute owner-PAT events to `credkellar`, to an agent, or to an unknown collaborator merely because the event is owner-attributed.

For a human action, record the authenticated GitHub login from an authoritative event when available. For an agent action, record the agent consumer stamp and execution receipt. When a human delegates through an owner credential, the human initiator and credential principal are separate fields and both require evidence.

## Credential architecture policy

Preferred order for new automation:
1. job-scoped `GITHUB_TOKEN` for work confined to the current workflow/repository and its declared permissions;
2. short-lived GitHub App installation tokens for cross-workflow or service-role automation, with separate least-privilege Apps/installation scopes for collector, publisher, reviewer, gate, and lifecycle responsibilities;
3. provider-specific OAuth/client credentials scoped to the provider and inference purpose;
4. PAT only for a documented owner-interactive or migration exception with a named owner, scope, expiry/rotation plan, and explicit consumer allowlist.

Do not distribute an owner PAT to collaborators or agent runtimes. Do not use `ARCHWIZ_GITHUB_TOKEN`, `OPERATOR_GITHUB_TOKEN`, `OPERATOR_TOKEN`, `GH_PAT`, or `OPERATOR` as interchangeable aliases by default. The existing documents disagree about whether ARCHWIZ is a separate PAT or an alias; this contract deliberately marks the relationship **UNVERIFIED** until the owner checks the live GitHub token inventory and Actions secret-name bindings. Names do not establish that values are equal or different.

No autonomous workflow may enumerate, print, hash, compare, test, rotate, or revoke credential values. No automatic revocation is authorized by this proposal. Secret-store presence checks may report names only. Principal/permission readback should use GitHub App metadata or owner-visible settings, never the private value.

## Rollout and acceptance

| Phase | Work | Acceptance evidence |
|---|---|---|
| 0 — reconcile | Owner reviews live PAT list and Actions secret names; resolves ARCHWIZ/OPERATOR naming conflict without exposing values | names-only inventory with owner, principal kind, scope class, expiry/rotation epoch, consumers, and last-used class |
| 1 — stamp | Add the envelope to existing quota/telemetry lane at dispatch time; reuse DoE instance key and current attribution ledger | schema tests; exact run/SHA/step joins; missing stamp fails closed for post-mandate records |
| 2 — isolate | Move publisher/reviewer/gate/lifecycle consumers to dedicated GitHub App installations or job tokens | effective permission receipts; no shared Owner PAT fallback for migrated consumers |
| 3 — retire | Remove legacy PAT aliases only after every consumer has migrated and a rollback path is tested | zero active workflow references to retired names; canary checks green; owner confirms revocation |

The existing quota-attribution status vocabulary remains authoritative: `established`, `activity-only`, `waived`, `fault`, `pending`. Missing usage is never zero. A shared-bucket aggregate cannot be allocated across agents by inference.

## Known baseline and gaps

- The names-only inventory in `data/ops/credential-surfaces.jsonl` was last observed 2026-10-10; it is not a live token inventory.
- `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` describes ARCHWIZ as a second administrator PAT; `docs/ops/SECRET-NAMING-CONVENTION.md` treats it as an OPERATOR alias. This is a documentation/control-plane conflict, not proof of shared token material.
- The PAT-era correlation snapshot covers 599 PRs and leaves 53 actors null. It is an attribution population snapshot, not a credential-value-to-agent map.
- Current telemetry contracts already distinguish App IDs, workflow names, signed lane roles, DoE prompt/tools refs, model versions, and context. This proposal joins those dimensions to an opaque credential reference at request time.
- GitHub App fleet telemetry documentation says Collector is read-only and Publisher is separate; remaining service roles are not all provisioned/operationally verified. Preserve that staged status.

## Non-goals

This contract does not identify which agent a third-party chat UI internally used unless that surface emits a verifiable session/dispatch receipt. It does not recover historical shared-PAT consumption, reveal token equality, prove human intent from an owner login, or authorize credential changes. Platform-withheld reasoning remains withheld; provenance records tool/action receipts and outcomes, not private chain-of-thought.


## Unsafe credential-family probe retired

The former `.github/workflows/credential-family-probe.yml` sent the same `DEEPSEEK_API_KEY` value to both GitHub and DeepSeek endpoints to infer its family. That is unsafe when the stored value may be a GitHub PAT: the credential is disclosed to an unrelated provider even if logs omit it. The workflow is now a manual owner-review reminder with `contents: read` only; it reads no secrets and makes no network requests. Classify credentials through owner-visible GitHub settings and the names-only inventory, never by cross-provider credential submission.
