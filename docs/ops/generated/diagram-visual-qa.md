# Diagram Visual QA Notes

## Render pass 1

| Asset | Result | Findings |
|---|---|---|
| `automation-overview.png` | Pass | The overview renders without clipping. The entry lanes, autonomous-development lanes, evidence convergence, authority outcomes, and postcondition/rollback branch are all legible at full size. The layered design avoids a monolithic workflow map. |
| `model-routing-3l0.png` | Pass | The vertical decision tree renders without clipped nodes. The Gemini primary, temporary Omni decommissioning branch, OpenRouter live/cache/stale/legacy availability states, free-model gate, 3L0 ranking, soft-budget test, and explicit no-route terminal state are visible. The tall aspect ratio is intentional for sequential routing; the Markdown guide supplies an adjacent text/table explanation. |

## Rendering policy

Further diagram changes require re-rendering the affected PNG and appending a visual QA entry. The Mermaid source remains authoritative; PNG assets are reviewable render artifacts.

## Render pass 2

| Asset | Result | Findings |
|---|---|---|
| `peer-provider-review.png` | Pass | The rendered tree clearly exposes the CodeRabbit default, explicit Qodo/Devin opt-in, exact authorized marker check, current-SHA evidence gate, advisory-versus-enforced pending state, cooldown branch, and second-pass completion route. The tall vertical form is legible and the adjacent Markdown text provides a compact policy table. |
| `autonomous-writer-rollback.png` | Pass | The writer tree renders all fail-closed preconditions, lease/idempotency branch, dry-run/diff gate, provenance record, fixed-scope mutation, postcondition test, circuit breaker, bounded rollback, and manual incident branch. No node clipping was observed. |

## Render pass 3

| Asset | Result | Findings |
|---|---|---|
| `timing-resilience.png` | Needs layout correction | Mermaid selected an extremely wide horizontal layout, producing a 3120×300 image that is not readable in a normal documentation viewport. The source is syntactically valid, but it will be revised into layered subgraphs/vertical orientation before publication. |
| `role-authority-hierarchy.png` | Pass | The role map renders cleanly and distinguishes operator policy, least-privilege workflow token, OPERATOR token lane, provider credentials, bounded writers, postcondition/rollback, review, and separate acceptance. |

## Render pass 4

| Asset | Result | Findings |
|---|---|---|
| `timing-resilience.png` after layout revision | Pass | The revised 3120×2008 vertical/layered render is readable at standard documentation width. It preserves the event/concurrency entry, bounded execution loop, cache and refresh states, quota/no-route terminals, cooldown/retry loop, and the separate scheduled-control-plane lane. |

## Render pass 5

| Asset | Result | Findings |
|---|---|---|
| `leaderboard-data-lineage.png` | Pass | The diagram clearly separates public leaderboard references, local 3L0 labels, live availability/allowlist input, soft-budget input, policy gating, selected route, explicit no-route, and normalized outcome evidence. The dotted public-board edge makes the “never sole authority” rule visible. |
