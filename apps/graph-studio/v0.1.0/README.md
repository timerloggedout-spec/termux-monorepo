# Termux Graph Studio · parallel release v0.1.0

Independent graph exploration surface for the termux-monorepo cross-plane graph contract.

## Guardrails
- Additional, regenerable view; never a source of truth.
- Imports graph edge JSON/JSONL locally; included fixture is illustrative, not live data.
- Never writes to plane indexes, collectors, or upstream repositories.
- Retains plane, source record, derivation method and observed_at per edge.
- Does not read tweet text, challenge metrics_internal, or infer identity by name matching.

## Run
```sh
npm install
npm run dev
npm test
npm run build
```

## Import
Accepts graph-edges/v1 JSONL (one edge per line) or JSON containing nodes[] and edges[], or an edge array. Nodes are inferred if metadata is absent.

## Release
- Version: 0.1.0
- Canonical GitHub Pages: https://timerloggedout-spec.github.io/termux-monorepo/graph-studio/
- Preview: https://termux-graph-studio-ueqxv4.v2.appdeploy.ai/
- Isolated source directory: apps/graph-studio/v0.1.0/
- Pages publication is performed by `tribute-dashboard-deploy.yml` after the change lands on `master`.
- Preview does not imply production promotion or live data ingestion.
