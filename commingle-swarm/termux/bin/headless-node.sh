#!/data/data/com.termux/files/usr/bin/bash
set -e
export RELAY_URL="${RELAY_URL:-https://relay.example}"
export P2P_TRACKERS="${P2P_TRACKERS:-wss://tracker.webtorrent.io,wss://tracker.openwebtorrent.com}"
export IPFS_API="${IPFS_API:-http://127.0.0.1:5001}"
export DATA_DIR="${DATA_DIR:-$HOME/commingle-swarm/data}"
export SWARM_NODE_ID="${SWARM_NODE_ID:-node-001}"

cd "$HOME/commingle-swarm"
npm install
npx ts-node --transpile-only termux/src/node.ts
