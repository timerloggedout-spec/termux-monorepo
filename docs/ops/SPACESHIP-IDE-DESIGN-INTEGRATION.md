# Spaceship IDE — design reference integration

**Status:** reference-only · Tier C pattern source  
**Reviewed:** 2026-11-23  
**Source revision:** `e567943134da28e337ccab6662e5a11fa4869fed`  
**Owner lane:** `refTemplates/13_Third_Party_Refs/spaceship-ide/`

## Decision

Register Spaceship IDE as a metadata-only design-pattern reference. Its four interaction concepts map to existing prompt/context, evaluation, and DoE/MVT lanes. The source and its media remain upstream; this integration adds provenance, navigation, and validation metadata.

The fork's `master` and upstream `master` both resolve to the same reviewed commit. Customization delta observed: none. Keep it outside `refTemplates/smods/` until a deliberate adaptation, immutable reviewed pin, compatibility evidence, and dual-gate result exist.

## Concept-to-lane map

| Source concept | Observed interaction | Internal lane | Candidate evaluation questions |
|---|---|---|---|
| Focus Monitor | Per-line salience meters respond to the current knob sentence or hovered phrase. | `11_Evaluation_Quality`; human/model attention alignment | Does the display help users locate task-relevant evidence? How often does salience misdirect attention? |
| Attention Lock | Draggable phrase boxes bind key wording to the current knob and bias future text around the selected phrases. | `07_Prompt_Context` | Does phrase-level control improve instruction adherence and preserve semantic intent? |
| Future Vector Steering | A detachable knob selects a semantic dimension; swing sets value, reach sets strength, and fulfillment is shown as text arrives. | `07_Prompt_Context` + DoE/MVT candidate | Which dimensions and control strengths improve directional control while preserving coherence? |
| Realtime Regeneration | A playhead scrubs speculative text; rewinding discards the future and starts an alternative continuation. | `11_Evaluation_Quality` + async/runtime verification | What are latency, cancellation correctness, state consistency, coherence, and alternative-branch diversity? |

Shared source vocabulary includes knobs, pointers, tray/bar layouts, style swatches, illustrations, and interaction clips. These are reference affordances for future UI work; adoption state remains reference-only.

## Lane associations

| Lane | Association | Integration action |
|---|---|---|
| `refTemplates/13_Third_Party_Refs` | Primary source home | Store README + SOURCE metadata and immutable source revision. |
| `refTemplates/07_Prompt_Context` | Attention Lock and Future Vector Steering | Cross-link the source for phrase-level and semantic-context interaction patterns. |
| `refTemplates/11_Evaluation_Quality` | Focus Monitor and Realtime Regeneration | Cross-link evaluation questions; retain source intent separately from measured outcomes. |
| Research Integration Lane | Tier-C pattern harvest | Make the source discoverable to proposals, evidence, and priority work while preserving its Tier-C pattern classification separately from research-scaffold adoption. |
| refTemplates Actions evaluation | Metadata integrity | Validate child README + SOURCE files under `13_Third_Party_Refs/`; keep scoring scoped to `15_Research_Repo_Templates/`. |
| DoE / MVT | Future UX experiment candidate | Use the existing experiment family if an owner admits a bounded comparison; record factors, outcomes, cohort, and uncertainty in its canonical campaign record. |
| ICM reference inputs | Knowledge navigation | Link the reference as an external pattern source; workspace runtime role: none. |

## Explicit scope boundaries

- Keep the reference in Tier C under `13_Third_Party_Refs/`; Tier A under `15_Research_Repo_Templates/` remains reserved for full research scaffolds.
- Keep the 12-silo Delphi participant registry scoped to Tier-A research templates. Spaceship IDE remains outside that participant set as a Tier-C pattern reference.
- Keep the source outside `refTemplates/smods/` while the fork and upstream share the same revision and custom compatibility delta observed: none.
- Keep `08_Swarm_References` and `12_External_Agents` unchanged; the source describes a single-user interactive human/LLM writing surface, while multi-agent coordination runtime remains a separate domain.
- Keep the source application's provider-key and browser-local-storage behavior source-specific; credential-flow adoption: none.

## DoE/MVT experiment sketch

A future owner-admitted study could compare interaction treatments such as attention visualization, phrase locking, vector controls, and regeneration preview/scrubbing. Candidate outcomes include task success, time-to-correct-edit, user steering effort, semantic drift, coherence, cancellation correctness, generation latency, and alternative diversity.

Use the existing [DoE taxonomy](DOE-TAXONOMY.md) and [DoE family](DOE-FAMILY.md). MVT names input factors; record multiple outcome variables as outcomes rather than conflating the terms. This sketch is a research lead. Campaign state: unadmitted, unexecuted. Measured effect sizes: unavailable.

## Evidence and source links

- [Reviewed fork revision](https://github.com/timerloggedout-spec/spaceship_fork/tree/e567943134da28e337ccab6662e5a11fa4869fed)
- [Upstream project](https://github.com/chuanqisun/spaceship)
- [Upstream demo](https://chuanqisun.github.io/spaceship/)
- [MIT license](https://github.com/timerloggedout-spec/spaceship_fork/blob/e567943134da28e337ccab6662e5a11fa4869fed/LICENSE)
- [Curated refTemplates entry](../../refTemplates/13_Third_Party_Refs/spaceship-ide/README.md)
- [Research Integration Lane](RESEARCH-INTEGRATION-LANE.md)
- [Research Silo Delphi boundary](RESEARCH-SILO-DELPHI.md)
- [refTemplates workflow hooks](REFTEMPLATES-WORKFLOW-HOOKS.md)
