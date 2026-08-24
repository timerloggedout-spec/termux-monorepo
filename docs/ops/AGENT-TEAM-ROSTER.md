# Agent Team Roster / Coordination Contract

This roster distinguishes **observed repository collaborators** from merely configured or mentioned integrations. Presence in history is not proof of current availability.

| Participant | Role | Admission / evidence | Manager treatment |
|---|---|---|---|
| Gemini CLI | high-context review/triage/invoke specialist | existing Gemini workflows + #272/#268 | use according to live quota and role fit; never claim execution without a run |
| OpenRouter / OX Alpha | experimental model lane | live catalog + MVT receipts | selectable experimental player during verified quota window |
| Felo | provider/model catalog + experimental lane | `FELO_AI_API` + live `/models` observation | automatic lane only for observed free/zero candidates; paid/unknown requires explicit experiment |
| OmniRoute | peer provider lane | existing routing work + MVT lane | independent peer when credential/capacity is available |
| Jules / google-labs-jules | bounded builder/escalation | historical Jules branches/workflows | admit when expected marginal value exceeds another peer pass; not default review sink |
| CodeRabbit | review/autofix collaborator | repository branches + #300/#95 | review signal must be classified as disposition/probe/status before feeding forward |
| Devin | implementation specialist | repository `devin/*` branches + prior integration work | bounded task worker; attribution remains provenance-based |
| Mistral / Vibe | provider/CLI collaborator | repository `vibe/mistralai-*` history | candidate specialist; availability must be observed |
| Manus | replay/recon/automation specialist | #265 + `manus/*` branches | evidence/recon and specialized automation; not a generic reviewer |
| Blocks | GitHub collaboration integration | observed `blocksorg[bot]` issue comments | treat generated onboarding/command responses as external collaboration signals, not correctness evidence |
| Dependabot | dependency/security automation | existing issue/workflow governance in #175 | autonomous security/dependency signal; do not duplicate as a permanent model role |
| Mintlify | documentation publication integration | docs/Mintlify branches and setup work | documentation pipeline, not an engineering correctness judge |

## Quota / cooldown contract

Quota is a **capacity constraint**, not a quality score. A cooldown or exhausted provider produces a routing/availability observation. It must not lower model correctness unless the model actually executed and produced an incorrect result.

`SKIPPED_CAPACITY` is operationally healthy when the policy intentionally avoids an unavailable/paid route. It is not a model PASS. `UNRESOLVED` means evidence is insufficient.

## Manager / Conductor

The Manager is the policy layer, not a single agent. It selects:

1. task decomposition
2. context scope
3. simultaneous lanes
4. waiting dependencies
5. escalation/admission
6. integration and verification
7. experiment promotion/culling

The Lead/Lag monitor independently records whether those decisions produced observable progress.

## Steering / continuation

Long-running work is governed by progress, not a fixed wall-clock budget. A task can continue while producing new evidence. The monitor escalates `STALLED` / `LOOP_SUSPECTED` conditions and can request a Continue-style next attempt. Each attempt receives a new immutable event/attempt identity; successful consolidation promotes a winning trunk without rewriting prior evidence.
