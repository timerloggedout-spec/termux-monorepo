# Optional Visual Review

| Field | Value |
|---|---|
| Type | object |
| Cluster | operations |
| Universe | live |
| Status | initiated |
| Entity | A file-backed visual review surface for ICM artifacts and human checkpoints |

## What this is

The repository’s ICM maintenance Pipeline remains file and Markdown first. Its initiated visual-review surface lives at [`../../_tv/README.md`](../../_tv/README.md): it mirrors named repository-native ICM artifacts as card files and reserves a caged response location for future human checkpoints.

The ICM CCTV fork remains the reviewed reference input. The monorepo now has canonical card artifacts, but does not start, deploy, require, or modify the CCTV renderer. The card files are usable as a future static mobile board source; a later GitHub Pages or equivalent publication requires its own reviewed workflow/deployment scope.

## Routing rule

Use this card only when a human-visible review checkpoint improves an already defined repository-native ICM process. Preserve the stage output under the monorepo’s own ICM path as the source of truth. A visual card may point to that output; it must not become a parallel canonical document.

Interactive response files must stay in [`../../_tv/responses/CONTEXT.md`](../../_tv/responses/CONTEXT.md)'s declared caged location and be consumed only by a named process after a human decision. Do not start a renderer, expose a localhost-only visual server, assume a second device, configure GitHub Pages, or create a permanent service from this reference pattern in the documentation-only phase.

## First-order impact

**Hits:** the ICM maintenance Pipeline, human checkpoint design, file-backed CCTV artifacts, future mobile-static publication review, and the BLU B160V/free-services envelope.
**Does not hit:** default ICM maintenance behavior, provider polling, GitHub Actions, Termux MCP/device access, network deployment, or application code automatically.

## Evidence

[1] [`refTemplates/smods/icm-cctv_fork/README.md`](../../../../refTemplates/smods/icm-cctv_fork/README.md) defines the optional visual layer, file-backed stage mirror, and checkpoint-response model.
[2] [`../../_tv/README.md`](../../_tv/README.md) is the repository-native card-artifact contract.
[3] [`../../maintenance/CLAUDE.md`](../../maintenance/CLAUDE.md) is the repository-native source-of-truth maintenance Pipeline.
