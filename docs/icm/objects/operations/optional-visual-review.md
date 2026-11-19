# Optional Visual Review

| Field | Value |
|---|---|
| Type | object |
| Cluster | operations |
| Universe | live |
| Status | initiated |
| Entity | A published, file-backed visual review surface for ICM artifacts and human checkpoints |

## What this is

The repository's ICM maintenance Pipeline remains file and Markdown first. Its visual-review surface mirrors named repository-native ICM artifacts as card files and reserves a caged response location for future human checkpoints.

The monorepo publishes the static board at [ICM CCTV · Tribute](https://timerloggedout-spec.github.io/tribute/icm-cctv.html). The existing Tribute publisher builds the page from `docs/icm/_tv/screens/` and publishes the generated HTML with the shared navigation and site assets.

The ICM CCTV fork remains the reviewed reference input. The monorepo owns its canonical card artifacts and static-board generator. The reference renderer, local file watcher, and WebSocket loop remain separate capabilities with their own review and deployment scope.

## Routing rule

Use this card when a human-visible review checkpoint improves an already defined repository-native ICM process. Preserve each stage output under the monorepo's own ICM path as the source of truth. A visual card links to that output and mirrors its reviewed state.

Interactive response files stay in the declared caged location under `_tv/responses/`. A consuming process declares the card identifier, accepted response values, canonical source artifact, human authority, and no-response behavior before it reads a response.

## First-order impact

**Hits:** the ICM maintenance Pipeline, human checkpoint design, file-backed CCTV artifacts, static Tribute publication, shared navigation, sitemap, and Project Hub route.

**Preserves:** Markdown-first maintenance, canonical ICM ownership, the existing provider-routing governance, and the separate BLU B160V/free-services envelope.

**Separate scope:** live renderer execution, provider polling, response consumption, device access, runtime routing changes, and application behavior each require their own reviewed proposal.

## Evidence

[1] [ICM CCTV reference fork](../../../../refTemplates/smods/icm-cctv_fork/README.md) defines the optional visual layer, file-backed stage mirror, and checkpoint-response model.  
[2] [ICM CCTV board contract](../../_tv/README.md) defines canonical card ownership and static publication.  
[3] [ICM maintenance Pipeline](../../maintenance/CLAUDE.md) defines the repository-native source-of-truth process.  
[4] [Tribute publisher](../../../../.github/workflows/tribute-dashboard-deploy.yml) builds and publishes the static board.
