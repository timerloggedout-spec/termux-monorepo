# OPS-EVENT HITL Control Plane

Batch: P0 + P1 + P2 implementation contract  
Lineage: #672 → #732 telemetry provider → #733 dashboard provider → feat/ops-hitl-control-plane

## Interaction model

The canonical product is a dual-pane synchronized control surface.

- Replay pane: SeekLog time-series, context constellation, .mmd topology, optional Gource replay, and ICM-CCTV observatory strip.
- HITL pane: selected entity context, comment/PR/Issue/Sprint controls, proposed commands, policy state, approval, runtime effect, and evidence.
- Shared cursor: both panes resolve the same snapshot_id, event range, source SHA, and selected entity.
- Read-only default: visualization/replay cannot mutate GitHub.
- Mutation path: proposal → context → policy check → approval → dispatch → observation → effect → evidence → reconciliation.

### Why replay belongs inside the HITL plane

Replay is the temporal navigation mechanism for command context. A maintainer can scrub to a comment, PR review, Sprint transition, collaborator observation, or provider failure and immediately inspect its action/effect/evidence chain. Conversely, a command selection can pin the replay cursor to the causal window that produced it.

This is intentionally closer to an Ableton/timeline editor interaction grammar than a generated Gource video: time is navigable, objects are selectable, lanes are synchronized, and every operational object has a context/action surface.

## P0

1. Typed HITL OPS-EVENT envelope.
2. Immutable command correlation IDs and explicit state machine.
3. SeekLog bounded replay adapter.
4. Context graph adapter with verified/candidate separation.
5. GitHub comment/PR context inspector using exact permalink/entity identity.
6. Command deck with preview-only default.

## P1

1. Sprint/cycle cadence events.
2. Collaborator synchronization planner with observed/explicit/proposed/confirmed states.
3. Shared MDX/MMD/image projection manifest.
4. Gource parallel projection from the same event range.
5. Owner policy/RBAC gate.
6. Audit/reconciliation chain.

## P2

1. n8n-style workflow export as a declarative adapter only.
2. Replay snapshot A/B comparison and event diff.
3. ICM-CCTV observability strip: independent evidence/telemetry camera, not an authority.
4. Multi-surface scene manifest for Pages/Vercel/Render and future WebGL/WASM consumers.

## Foreign-repo / CONTRIBUTING controls

Foreign repositories are first-class context targets, but not authority substitutes. The inspector should surface the target repository's CONTRIBUTING.md, issue/PR templates, CODEOWNERS, labels, and review conventions as repository-local policy context before proposing a reply, PR action, or synchronization request.

A clarification is an interaction object:

foreign-repo → policy context → comment/PR context → proposed clarification → approval → external effect → evidence

No inferred collaborator relationship or graph proximity is sufficient to trigger outreach.

## Projection contract

Every .mmd, MDX narrative, image, Gource log, ICM-CCTV frame, or interactive scene must expose:

- snapshot_id
- source_sha
- event_start
- event_end
- event_count
- projection_kind

## n8n boundary

The workflow vocabulary may be represented as:

trigger → enrich → branch → approve → dispatch → observe → reconcile

The adapter exports a graph. GitHub, OPS-EVENT, and evidence remain authoritative.

## Acceptance

The batch is complete when the control surface can:

- seek/pause/resume a bounded event range;
- select an event and focus the same entity in the command/context pane;
- preview a reply/PR/Issue/Sprint/collaborator action without execution;
- reject unapproved mutation;
- carry exact correlation/causation IDs through dispatch/effect/evidence;
- distinguish partial/unverified corpus state;
- show verified and candidate graph edges separately;
- emit a Gource-compatible projection from the same range;
- export MDX/MMD/image provenance;
- compare two snapshots without changing either source;
- render telemetry/ICM-CCTV separately from control state.
