# Optional Visual Review

| Field | Value |
|---|---|
| Type | object |
| Cluster | operations |
| Universe | live |
| Status | verified |
| Entity | An optional file-backed visual review surface for ICM stage artifacts and human checkpoints |

## What this is

The repository’s ICM maintenance Pipeline remains file and Markdown first. A visual review surface is optional: it may mirror a named stage output as a card and capture a human response as a bounded response artifact. The ICM CCTV fork is the reviewed reference input for this pattern; the monorepo does not run, deploy, or require that renderer by default.

## Routing rule

Use this card only when a human-visible review checkpoint would improve an already defined repository-native ICM process. Preserve the stage output under the monorepo’s own maintenance path as the source of truth. A visual card may point to that output; it must not become a parallel canonical document.

Interactive response files must stay in a declared, caged location and be consumed by a named process after a human decision. Do not expose a localhost-only visual server, assume a second device, or create a permanent service from this reference pattern.

## First-order impact

**Hits:** the maintenance Pipeline, human checkpoint design, optional local visual-review configuration, and the BLU B160V/free-services envelope.
**Does not hit:** the default ICM maintenance flow, Termux MCP/device access, network deployment, or application code automatically.

## Evidence

[1] [`refTemplates/smods/icm-cctv_fork/README.md`](../../../../refTemplates/smods/icm-cctv_fork/README.md) defines the optional visual layer, file-backed stage mirror, and checkpoint-response model.
[2] [`../../maintenance/CLAUDE.md`](../../maintenance/CLAUDE.md) is the repository-native source-of-truth maintenance Pipeline.
