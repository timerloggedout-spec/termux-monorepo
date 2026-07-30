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
  - npm install
  - npm run build
  - npm run serve
- Open http://localhost:8088 in Chrome
