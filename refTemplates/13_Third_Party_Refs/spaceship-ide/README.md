# Spaceship IDE — interaction design patterns

**Classification:** Tier C · pattern-only · metadata-only  
**Source revision:** `e567943134da28e337ccab6662e5a11fa4869fed`  
**License:** MIT · Copyright (c) 2026 Sun

## Source

- Fork: [timerloggedout-spec/spaceship_fork](https://github.com/timerloggedout-spec/spaceship_fork/tree/e567943134da28e337ccab6662e5a11fa4869fed)
- Upstream: [chuanqisun/spaceship](https://github.com/chuanqisun/spaceship)
- Live demo: [Spaceship IDE](https://chuanqisun.github.io/spaceship/)
- Provenance: [SOURCE.txt](./SOURCE.txt)

The fork and upstream `master` both resolve to the reviewed commit. The fork currently carries no independently observed customization delta, so this entry remains a design-pattern reference rather than an executable pin.

## Concepts

| Concept | Interaction model | Relevant repository lane |
|---|---|---|
| **Focus Monitor** | Per-line meters visualize how strongly text connects to the current knob sentence or hovered phrase; salient lines brighten. | `11_Evaluation_Quality`; human/model attention-alignment studies |
| **Attention Lock** | Draggable phrase boxes bind selected wording to the current knob and bias the generated continuation around those phrases. | `07_Prompt_Context`; phrase-level context and semantic steering |
| **Future Vector Steering** | A detachable future knob selects a semantic dimension; swing controls value, reach controls strength, and fulfillment is visualized before pinning to text. | `07_Prompt_Context`; candidate DoE/MVT factors |
| **Realtime Regeneration** | A playhead scrubs generated text; moving backward discards the speculative future and streams an alternative continuation. | `11_Evaluation_Quality`; latency, cancellation, coherence, and branch-diversity evaluation |

## Supporting interaction vocabulary

The source also includes knob-state studies, pointer variants, tray and bar layouts, style swatches, illustrations, and captured interaction clips. These assets help compare interaction affordances and visual treatments while the source application's runtime remains upstream.

Useful source paths:

- `extra/illustrations.html` — animated explanations of the four core concepts.
- `extra/knob-states.html` — main-knob buffer states.
- `extra/style-1.html` through `extra/style-4.html` — visual style explorations.
- `extra/pointer-1.html` through `extra/pointer-5.html` — pointer/drag affordances.
- `extra/tray-1.html` through `extra/tray-3.html` and `extra/bar-1.html` through `extra/bar-3.html` — layout variations.
- `extra/clips/` — concept illustrations and GIF recordings.

## Integration

- Primary source category: [`13_Third_Party_Refs`](../README.md).
- Prompt/context connection: [`07_Prompt_Context`](../../07_Prompt_Context/README.md).
- Evaluation connection: [`11_Evaluation_Quality`](../../11_Evaluation_Quality/README.md).
- Cross-lane design record: [Spaceship IDE design integration](../../../docs/ops/SPACESHIP-IDE-DESIGN-INTEGRATION.md).
- Research classification: [Research Integration Lane](../../../docs/ops/RESEARCH-INTEGRATION-LANE.md).

Treat these as design hypotheses and source-reported interaction descriptions. The source establishes the concepts and UI mechanics; it supplies no independently reproduced performance or usability results for this repository.

## Reuse boundary

Keep the entry metadata-only. Source code, media, and application runtime remain upstream. The source README describes browser-local storage for user API keys; treat that as source-specific demo behavior and keep provider credentials outside repository artifacts.

The Tier-C entry participates in reference inventory and relevant proposal/evidence lanes. It remains separate from the Tier-A research-template score, the 12-silo Delphi participant registry, and `refTemplates/smods/`.
