# Flywheel Routing Model — Extensible Collaborators, Contexts, and Projects

**Status:** design proposal for review. Existing channel protocols and the current registry remain authoritative until an approved migration changes them.

## 1. Design objective

Model the Flywheel as a multi-project collaboration fabric. Channels are communication routes; collaborators are actors; execution surfaces are identities through which actors operate; contexts define bounded work; artifacts remain in their source systems. The model supports many collaborators, projects, repositories, workstreams, and contexts without assigning a new channel to every task or duplicating project registries.

## 2. Separate the entities

| Entity | Stable identity | Responsibility |
|---|---|---|
| Collaborator | `peer_id` | Human, agent, team, or service identity |
| Execution surface | `surface_id` | GitHub connector, Web2API session, MCP, CLI, Termux device, provider API, or other actual execution surface |
| Channel | `channel_id` (`FLY-NNN`) | Store-and-forward route with its own protocol, store, cadence, owner, and scope |
| Project | `project_id` | Repository, workspace, product, or external project |
| Context | `context_id` | Bounded objective/workstream within one or more projects |
| Membership | peer + surface + channel + context | Explicit route authorization and participation scope |
| Artifact | typed source reference | Issue, PR, commit, file/blob, test, workflow run, export, or evidence record |
| Topic | `topic_id` | Cross-cutting subject that joins contexts without owning their source data |

This separation prevents a collaborator's Web2API session from being conflated with its GitHub connector, and prevents a project's identity from being conflated with one channel.

## 3. Effective permission and token scope

For an action on an artifact, calculate the effective permission as the intersection of all applicable grants:

`effective = token_scope ∩ repository_permission ∩ peer_membership ∩ surface_grant ∩ channel_acl ∩ context_scope ∩ action_policy`

- An empty intersection yields `deny`.
- Read, comment, content-write, workflow-write, and merge are separate action classes.
- A token's presence proves authentication only; its effective scope is constrained by the repository grant and the registered membership.
- Context membership cannot widen a token or repository permission.
- Default access is least-privilege; write access is explicit per action and context.
- Store credential names/roles or protected references only. Keep token values, cookies, browser profiles, and private payloads outside registry records and channel messages.
- Expiry, revocation, and observed access gaps are explicit membership states.

## 4. Context-aware route selection

A work event carries a compact routing envelope:

```json
{
  "event_id": "stable-event-id",
  "actor_id": "peer-id",
  "surface_id": "surface-id",
  "project_refs": ["owner/repo"],
  "context_ids": ["context-id"],
  "topic_ids": ["topic-id"],
  "channel_id": "FLY-NNN",
  "artifact_refs": [
    {"kind": "pull_request", "repo": "owner/repo", "number": 123, "head_sha": "40-hex"}
  ],
  "action": "review",
  "scope": ["read", "comment"],
  "reply_to": "prior-event-id"
}
```

Route resolution:
1. Resolve the project and context from explicit identifiers.
2. Resolve the collaborator and actual execution surface independently.
3. Select channels whose declared scope covers the context and whose participant/membership records include the peer.
4. Intersect requested actions with effective token, repository, surface, channel, context, and policy grants.
5. Choose the narrowest qualifying route; preserve explicit channel boundaries (for example FLY-005 exports vs FLY-006 non-export work).
6. Emit one append-only event with typed artifact references and an idempotent event identity.

A channel is a transport. It does not become the source of truth for a project's code, issue, test result, or provider quota.

## 5. Navigation projections

The central hub should expose several projections over the same identities:

- **By channel:** FLY-NNN → protocol → store → owner/cadence → linked work.
- **By collaborator:** peer → execution surfaces → memberships → active contexts → contribution evidence.
- **By project:** project/repository → contexts → channels → issues/PRs/files/tests/runs.
- **By context:** objective → participants → current state → relevant topics → artifacts → next action.
- **By topic:** cross-project references with source ownership retained.
- **By artifact:** immutable source reference → contexts, discussions, decisions, tests, and follow-up work.

The hub is a navigation layer, not a second task database or a copied artifact store.

## 6. Token efficiency and shared context

- Reuse one canonical artifact reference across collaborators instead of pasting the same source payload into multiple channels.
- Send compact deltas, immutable SHAs, and typed links; fetch full content only at the point of need.
- Batch oversight at stable checkpoints; keep active context to roughly four live work items.
- Separate verified evidence from candidates and recommendations.
- Preserve one event receipt per state change; use FLY-003 for export/completion confirmations as already governed.
- Share context through references and scoped summaries, while preserving each collaborator's independent review and attribution.

## 7. Registry evolution

The current `REGISTRY.json` remains the channel/peer authority. The additive [`CONTEXTS.json`](CONTEXTS.json) now carries project, context, surface, membership, and topic records under `flywheel-contexts/v1`; [`CONTEXTS.schema.json`](CONTEXTS.schema.json) defines the data contract. Membership action classes describe requested/observed scope and do not grant access.

Migration rules:
1. Preserve existing FLY-NNN IDs, channel paths, messages, and peer names.
2. Keep current channel and peer rows valid while the additive fields are introduced.
3. Do not copy quota registries, issue bodies, source files, or telemetry payloads into the Flywheel registry.
4. Keep unverified and pending memberships visibly pending; a connector membership does not complete a separate browser/Web2API onboarding task.
5. Add schema validation and round-trip fixtures before consumers rely on the new fields.

## 8. Current collaboration registration boundary

`chatgpt` remains the separate shared-Google Web2API session tracked by [QUE #5885](https://github.com/timerloggedout-spec/termux-monorepo/issues/5885). This PR proposes the GitHub connector surface as `chatgpt-github` for scoped FLY-006 project collaboration; its first ACK is recorded while registry and protocol review remain open. The two surfaces retain separate readiness, permissions, and evidence.

## 9. Acceptance

- Every registered channel has one canonical protocol/store route and a linked hub entry.
- Every active collaborator is represented separately from its execution surfaces.
- A peer may hold multiple context-scoped memberships without duplicating the peer or project registry.
- Effective access is the intersection of token, repository, peer, surface, channel, context, and action grants.
- Cross-project navigation resolves to canonical artifacts and immutable revisions.
- Pending onboarding, stale evidence, and unavailable surfaces remain explicit states.
- New channels, peers, contexts, and projects extend the registry without rewriting existing channel history.
