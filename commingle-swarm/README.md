# Commingle Swarm

A distributed, client-side swarm app (PWA + Termux headless) for commingled execution with segregated accounting.
This upgrade adds REST endpoints to the headless node and wires the PWA to call the node.

## Termux quick start
- pkg install nodejs-lts
- chmod +x upgrade-commingle-swarm.sh && ./upgrade-commingle-swarm.sh
- cd commingle-swarm
- npm install
- ./termux/bin/headless-node.sh
- In a second session:
  - cd commingle-swarm/web
  - pnpm install
  - pnpm run build
  - pnpm run serve
- Open http://localhost:8088 in Chrome

Note: `web/` is governed by the Lane 3 (Palette) guardrail in
`docs/ops/LANE_CONSOLIDATION_SSOT.md`, which mandates pnpm for this
directory ("Node-bound files MUST never use npm or yarn"). Only
`web/pnpm-lock.yaml` is committed; do not regenerate a
`package-lock.json` here.
