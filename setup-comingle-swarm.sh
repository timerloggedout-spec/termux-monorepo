#!/data/data/com.termux/files/usr/bin/bash
# setup-commingle-swarm.sh
# Build the future now: scaffold a distributed client-side swarm app (PWA + Termux headless).
set -e

ROOT_DIR="$HOME/commingle-swarm"
WEB_DIR="$ROOT_DIR/web"
TERMUX_DIR="$ROOT_DIR/termux"
SCRIPTS_DIR="$ROOT_DIR/scripts"
INFRA_DIR="$ROOT_DIR/infra"
ASSETS_DIR="$ROOT_DIR/assets"

echo "Creating directories..."
mkdir -p "$ROOT_DIR"
mkdir -p "$WEB_DIR/public" "$WEB_DIR/src/components" "$WEB_DIR/src/modules/allocation" \
         "$WEB_DIR/src/modules/policy" "$WEB_DIR/src/modules/ledger" "$WEB_DIR/src/modules/net" \
         "$WEB_DIR/src/modules/ipfs" "$WEB_DIR/sw" "$WEB_DIR/src/hooks" "$WEB_DIR/src/styles"
mkdir -p "$TERMUX_DIR/bin" "$TERMUX_DIR/src"
mkdir -p "$SCRIPTS_DIR" "$INFRA_DIR/ipfs-pinning" "$INFRA_DIR/webseed" "$ASSETS_DIR/icons"

echo "Writing root files..."
cat > "$ROOT_DIR/README.md" << 'EOF'
# Commingle Swarm

A distributed, client-side swarm app (PWA + Termux headless) for commingled execution with segregated accounting. Nodes run locally, receive allocation plans, attribute fills, and publish Merkle proofs to IPFS/WebTorrent. Built for alternative jurisdictions, functionality-first.

## Quick start (Termux)
- pkg install nodejs
- bash setup-commingle-swarm.sh
- cd commingle-swarm
- npm install
- npm run build:web
- npm run start:node

## Quick start (PWA)
- cd commingle-swarm/web
- npm install
- npm run build
- npm run serve
EOF

cat > "$ROOT_DIR/package.json" << 'EOF'
{
  "name": "commingle-swarm",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "build:web": "cd web && npm run build",
    "dev:web": "cd web && npm run dev",
    "serve:web": "cd web && npm run serve",
    "start:node": "ts-node --transpile-only termux/src/node.ts",
    "build:node": "tsc -p tsconfig.json && node dist/termux/src/node.js"
  },
  "devDependencies": {
    "esbuild": "^0.23.0",
    "typescript": "^5.6.2",
    "ts-node": "^10.9.2"
  }
}
EOF

cat > "$ROOT_DIR/tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "moduleResolution": "Node",
    "outDir": "dist",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["termux/src/**/*.ts"]
}
EOF

cat > "$ROOT_DIR/.env.example" << 'EOF'
# Example environment variables
RELAY_URL=https://relay.example
P2P_TRACKERS=wss://tracker.webtorrent.io,wss://tracker.openwebtorrent.com
IPFS_API=http://127.0.0.1:5001
DATA_DIR=$HOME/commingle-swarm/data
SWARM_NODE_ID=node-001
EOF

echo "Writing web project files..."
cat > "$WEB_DIR/package.json" << 'EOF'
{
  "name": "commingle-swarm-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "build": "esbuild src/index.tsx --bundle --outfile=public/bundle.js --sourcemap --define:process.env.NODE_ENV='\"production\"'",
    "dev": "esbuild src/index.tsx --bundle --outfile=public/bundle.js --sourcemap --watch",
    "serve": "node server.js"
  },
  "devDependencies": {
    "esbuild": "^0.23.0",
    "typescript": "^5.6.2"
  },
  "dependencies": {
    "lit-html": "^3.1.0"
  }
}
EOF

cat > "$WEB_DIR/tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "jsx": "react-jsx",
    "moduleResolution": "Node",
    "strict": true,
    "skipLibCheck": true
  }
}
EOF

cat > "$WEB_DIR/public/index.html" << 'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="manifest" href="./manifest.json" />
  <title>Commingle Swarm</title>
</head>
<body>
  <div id="app"></div>
  <script src="./bundle.js"></script>
</body>
</html>
EOF

cat > "$WEB_DIR/public/manifest.json" << 'EOF'
{
  "name": "Commingle Swarm",
  "short_name": "Swarm",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b0f1a",
  "theme_color": "#0b0f1a",
  "icons": []
}
EOF

cat > "$WEB_DIR/server.js" << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const base = path.join(__dirname, 'public');

const server = http.createServer((req, res) => {
  let pathname = req.url === '/' ? '/index.html' : req.url;
  const filePath = path.join(base, pathname);
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200); res.end(data);
  });
});

server.listen(8088, () => console.log('PWA served at http://localhost:8088'));
EOF

cat > "$WEB_DIR/src/index.tsx" << 'EOF'
import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const App = () => html`
  <main style="font-family: system-ui; color: #eaf0ff; background:#0b0f1a; min-height:100vh; padding:16px;">
    <h1>Commingle Swarm</h1>
    <section>
      ${ManagerConsole()}
      ${ClientPortal()}
    </section>
  </main>
`;

render(App(), document.getElementById('app')!);
EOF

cat > "$WEB_DIR/src/components/ManagerConsole.tsx" << 'EOF'
import { html } from 'lit-html';
import { proposeAllocation } from '../modules/allocation/AllocationEngine';
import { DEFAULT_VISIBLE_WEIGHT, DEFAULT_HIDDEN_WEIGHT } from '../modules/allocation/AllocationConfig';

export const ManagerConsole = () => {
  const placeholderClients = [
    { clientId: 'C001', walletAddress: 'w1', totalCapital: 10000, visibleAllocationPercent: DEFAULT_VISIBLE_WEIGHT, hiddenAllocationPercent: DEFAULT_HIDDEN_WEIGHT, policyIds: [], feeProfileId: 'F1', performanceMetrics: { cumulativePnL: 0, lastNAV: 10000, highWaterMark: 10000 } },
    { clientId: 'C002', walletAddress: 'w2', totalCapital: 25000, visibleAllocationPercent: DEFAULT_VISIBLE_WEIGHT, hiddenAllocationPercent: DEFAULT_HIDDEN_WEIGHT, policyIds: [], feeProfileId: 'F1', performanceMetrics: { cumulativePnL: 0, lastNAV: 25000, highWaterMark: 25000 } }
  ];

  const trade = { id: 'TX1', asset: 'ETH/USDT', direction: 'buy', totalSize: 5, timestamp: Date.now(), strategyId: 'S1' };

  const plan = proposeAllocation(trade as any, placeholderClients as any);

  return html`
    <section style="margin-top:16px;">
      <h2>Manager console</h2>
      <pre style="background:#121426; padding:12px; border-radius:8px;">${JSON.stringify(plan, null, 2)}</pre>
    </section>
  `;
};
EOF

cat > "$WEB_DIR/src/components/ClientPortal.tsx" << 'EOF'
import { html } from 'lit-html';
export const ClientPortal = () => html`
  <section style="margin-top:16px;">
    <h2>Client portal</h2>
    <p>View holdings, activity, and performance. (Placeholder)</p>
  </section>
`;
EOF

cat > "$WEB_DIR/src/modules/allocation/AllocationConfig.ts" << 'EOF'
export const DEFAULT_VISIBLE_WEIGHT = 0.25;
export const DEFAULT_HIDDEN_WEIGHT = 0.75;
export const MIN_LOT = 0.001LING = 'round-robin';
export const DUST_THRESHOLD_USD = 0.5;
EOF

cat > "$WEB_DIR/src/modules/policy/PolicyEvaluator.ts" << 'EOF'
export type ClientProfile = {
  clientId: string;
  walletAddress: string;
  totalCapital: number;
  visibleAllocationPercent?: number;
  hiddenAllocationPercent?: number;
  policyIds: string[];
  feeProfileId: string;
  performanceMetrics: { cumulativePnL: number; lastNAV: number; highWaterMark: number };
};

export type TradeProposal = {
  id: string;
  asset: string;
  direction: 'buy' | 'sell';
  totalSize: number;
  timestamp: number;
  strategyId: string;
  priceLimit?: number;
  tags?: string[];
};

export const PolicyEvaluator = {
  isEligible(client: ClientProfile, asset: string) {
    // Placeholder: everyone eligible, asset allowlist could be attached by client
    return { eligible: true, reasons: [] as string[] };
  }
};
EOF

cat > "$WEB_DIR/src/modules/allocation/AllocationEngine.ts" << 'EOF'
import { PolicyEvaluator, ClientProfile, TradeProposal } from '../policy/PolicyEvaluator';
import { DEFAULT_VISIBLE_WEIGHT, DEFAULT_HIDDEN_WEIGHT, MIN_LOT } from './AllocationConfig';

export type AllocationEntry = {
  clientId: string;
  allocatedSize: number;
  allocationSource: 'visible' | 'hidden';
  constraintsApplied: string[];
  notes?: string;
};

export type AllocationPlan = {
  tradeId: string;
  asset: string;
  direction: 'buy' | 'sell';
  allocations: AllocationEntry[];
  fillStatus: 'pending' | 'partial' | 'complete';
  createdAt: number;
  planHash: string;
};

function hashPlan(seed: string) {
  // Deterministic simple hash placeholder
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h << 5) - h + seed.charCodeAt(i);
  return 'PLAN-' + (h >>> 0).toString(16);
}

export function proposeAllocation(trade: TradeProposal, clients: ClientProfile[]): AllocationPlan {
  const eligible = clients.filter(c => PolicyEvaluator.isEligible(c, trade.asset).eligible);
  const caps = eligible.map(c => {
    const visibleCap = c.totalCapital * (c.visibleAllocationPercent ?? DEFAULT_VISIBLE_WEIGHT);
    const hiddenCap = c.totalCapital * (c.hiddenAllocationPercent ?? DEFAULT_HIDDEN_WEIGHT);
    return { clientId: c.clientId, visibleCap, hiddenCap };
  });

  const totalVis = caps.reduce((s, x) => s + x.visibleCap, 0);
  const totalHid = caps.reduce((s, x) => s + x.hiddenCap, 0);

  const allocations: AllocationEntry[] = [];
  // Visible layer
  for (const c of caps) {
    const w = totalVis > 0 ? c.visibleCap / totalVis : 0;
    let size = Math.floor((trade.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'visible', constraintsApplied: [] });
  }
  // Hidden layer
  for (const c of caps) {
    const w = totalHid > 0 ? c.hiddenCap / totalHid : 0;
    let size = Math.floor((trade.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'hidden', constraintsApplied: [] });
  }

  // Residual handling: round-robin (placeholder)
  const allocatedSum = allocations.reduce((s, a) => s + a.allocatedSize, 0);
  let residual = trade.totalSize - allocatedSum;
  let idx = 0;
  while (residual >= MIN_LOT && allocations.length > 0) {
    allocations[idx % allocations.length].allocatedSize += MIN_LOT;
    residual -= MIN_LOT;
    idx++;
  }

  const createdAt = Date.now();
  const planHash = hashPlan(JSON.stringify({ trade, allocations, createdAt }));
  return { tradeId: trade.id, asset: trade.asset, direction: trade.direction, allocations, fillStatus: 'pending', createdAt, planHash };
}

export function attributeFill(plan: AllocationPlan, fills: { size: number }[]) {
  // Placeholder: sequentially assign fills to allocation entries
  let remaining = fills.reduce((s, f) => s + f.size, 0);
  for (const entry of plan.allocations) {
    const take = Math.min(entry.allocatedSize, remaining);
    entry.notes = `Attributed ${take}`;
    remaining -= take;
    if (remaining <= 0) break;
  }
  plan.fillStatus = remaining > 0 ? 'partial' : 'complete';
  return plan;
}
EOF

cat > "$WEB_DIR/src/modules/ledger/PositionVault.ts" << 'EOF'
export type Lot = { asset: string; qty: number; price: number; ts: number };
export type ClientLots = { [clientId: string]: Lot[] };

export class PositionVault {
  private lots: ClientLots = {};
  constructor(private persist: (state: ClientLots) => void, private load: () => ClientLots | null) {
    const state = this.load();
    if (state) this.lots = state;
  }
  credit(clientId: string, asset: string, qty: number, price: number) {
    if (!this.lots[clientId]) this.lots[clientId] = [];
    this.lots[clientId].push({ asset, qty, price, ts: Date.now() });
    this.persist(this.lots);
  }
  debit(clientId: string, asset: string, qty: number) {
    const arr = this.lots[clientId] || [];
    let remaining = qty;
    for (const lot of arr) {
      if (lot.asset !== asset) continue;
      const take = Math.min(remaining, lot.qty);
      lot.qty -= take;
      remaining -= take;
      if (remaining <= 0) break;
    }
    this.lots[clientId] = arr.filter(l => l.qty > 0 || l.asset !== asset);
    this.persist(this.lots);
  }
  snapshot() { return JSON.parse(JSON.stringify(this.lots)); }
}
EOF

cat > "$WEB_DIR/src/modules/net/P2PNode.ts" << 'EOF'
export class P2PNode {
  constructor(private opts: { trackers: string[] }) {}
  async start() {
    // Placeholder for WebRTC/WebTorrent bootstrap
    console.log('P2PNode start with trackers:', this.opts.trackers);
  }
  async publish(topic: string, payload: any) {
    console.log('Publish', topic, payload);
  }
  async subscribe(topic: string, handler: (msg: any) => void) {
    console.log('Subscribe', topic);
  }
}
EOF

cat > "$WEB_DIR/src/modules/ipfs/IpfsStore.ts" << 'EOF'
export class IpfsStore {
  constructor(private api: string) {}
  async publish(obj: any) {
    // Placeholder: return fake CID
    const cid = 'bafy' + Math.random().toString(36).slice(2, 10);
    console.log('Published to IPFS', cid);
    return cid;
  }
}
EOF

cat > "$WEB_DIR/sw/service-worker.ts" << 'EOF'
// Placeholder service worker
self.addEventListener('install', (_: any) => {
  // @ts-ignore
  self.skipWaiting();
});
self.addEventListener('activate', (_: any) => {
  console.log('SW activated');
});
EOF

echo "Writing Termux headless node..."
cat > "$TERMUX_DIR/src/node.ts" << 'EOF'
import http from 'http';
import fs from 'fs';
import path from 'path';

type Env = {
  RELAY_URL?: string;
  P2P_TRACKERS?: string;
  IPFS_API?: string;
  DATA_DIR?: string;
  SWARM_NODE_ID?: string;
};

const env: Env = process.env as Env;
const DATA_DIR = env.DATA_DIR || path.join(process.env.HOME || '.', 'commingle-swarm', 'data');
const LOG_DIR = path.join(DATA_DIR, 'logs');

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(LOG_DIR, { recursive: true });

const stateFile = path.join(DATA_DIR, 'vault.json');
if (!fs.existsSync(stateFile)) fs.writeFileSync(stateFile, JSON.stringify({}), 'utf8');

const server = http.createServer((_req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'ok', nodeId: env.SWARM_NODE_ID || 'unknown', dataDir: DATA_DIR }));
});

server.listen(8080, () => {
  console.log('Headless node running at http://127.0.0.1:8080');
});
EOF

cat > "$TERMUX_DIR/bin/headless-node.sh" << 'EOF'
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
EOF
chmod +x "$TERMUX_DIR/bin/headless-node.sh"

echo "Writing scripts..."
cat > "$SCRIPTS_DIR/build.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
npm install
npm run build:web
EOF
chmod +x "$SCRIPTS_DIR/build.sh"

cat > "$SCRIPTS_DIR/publish-webtorrent.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
echo "Placeholder: prepare WebTorrent publishing (attach magnet on landing page)."
EOF
chmod +x "$SCRIPTS_DIR/publish-webtorrent.sh"

echo "Infra placeholders..."
cat > "$INFRA_DIR/ipfs-pinning/pin-config.json" << 'EOF'
{ "pinningService": "custom", "api": "http://127.0.0.1:5001" }
EOF

cat > "$INFRA_DIR/webseed/nginx.conf" << 'EOF'
# Placeholder webseed config
server { listen 8089; root /var/www/commingle-swarm; }
EOF

echo "Assets placeholders..."
cat > "$ASSETS_DIR/icons/.keep" << 'EOF'
# icons placeholder
EOF

echo "Setup complete."
echo "Next steps:"
echo "1) cd $ROOT_DIR"
echo "2) npm install"
echo "3) npm run build:web"
echo "4) $TERMUX_DIR/bin/headless-node.sh"
