#!/data/data/com.termux/files/usr/bin/bash
# upgrade-commingle-swarm.sh
# Do everything now: REST API in node, PWA wired to node, shared AllocationEngine in Termux.
set -e

ROOT="$HOME/commingle-swarm"
WEB="$ROOT/web"
TERMUX="$ROOT/termux"
SCRIPTS="$ROOT/scripts"
INFRA="$ROOT/infra"
ASSETS="$ROOT/assets"

mkdir -p "$ROOT" "$WEB/public" "$WEB/src/components" "$WEB/src/modules/allocation" \
  "$WEB/src/modules/policy" "$WEB/src/modules/ledger" "$WEB/src/modules/net" \
  "$WEB/src/modules/ipfs" "$WEB/src/api" "$WEB/sw" "$WEB/src/hooks" "$WEB/src/styles"
mkdir -p "$TERMUX/bin" "$TERMUX/src/allocation"
mkdir -p "$SCRIPTS" "$INFRA/ipfs-pinning" "$INFRA/webseed" "$ASSETS/icons"

echo "Updating root files..."
cat > "$ROOT/README.md" << 'EOF'
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
EOF

cat > "$ROOT/package.json" << 'EOF'
{
  "name": "commingle-swarm",
  "version": "0.2.0",
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

cat > "$ROOT/tsconfig.json" << 'EOF'
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

cat > "$ROOT/.env.example" << 'EOF'
RELAY_URL=https://relay.example
P2P_TRACKERS=wss://tracker.webtorrent.io,wss://tracker.openwebtorrent.com
IPFS_API=http://127.0.0.1:5001
DATA_DIR=$HOME/commingle-swarm/data
SWARM_NODE_ID=node-001
EOF

echo "Updating web project..."
cat > "$WEB/package.json" << 'EOF'
{
  "name": "commingle-swarm-web",
  "version": "0.2.0",
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

cat > "$WEB/tsconfig.json" << 'EOF'
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

cat > "$WEB/public/index.html" << 'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="manifest" href="./manifest.json" />
  <title>Commingle Swarm</title>
</head>
<body style="background:#0b0f1a;color:#eaf0ff;font-family:system-ui;">
  <div id="app"></div>
  <script src="./bundle.js"></script>
</body>
</html>
EOF

cat > "$WEB/public/manifest.json" << 'EOF'
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

cat > "$WEB/server.js" << 'EOF'
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

cat > "$WEB/src/index.tsx" << 'EOF'
import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const App = () => html`
  <main style="min-height:100vh; padding:16px;">
    <h1>Commingle Swarm</h1>
    ${ManagerConsole()}
    ${ClientPortal()}
  </main>
`;
render(App(), document.getElementById('app')!);
EOF

cat > "$WEB/src/api/NodeClient.ts" << 'EOF'
const BASE = 'http://127.0.0.1:8080';

export async function status() {
  const res = await fetch(`${BASE}/status`);
  return res.json();
}

export async function proposeTrade(payload: any) {
  const res = await fetch(`${BASE}/proposeTrade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function getPlans() {
  const res = await fetch(`${BASE}/plans`);
  return res.json();
}

export async function getVault(clientId?: string) {
  const url = clientId ? `${BASE}/vault/${clientId}` : `${BASE}/vault`;
  const res = await fetch(url);
  return res.json();
}
EOF

cat > "$WEB/src/components/ManagerConsole.tsx" << 'EOF'
import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ManagerConsole = () => {
  let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
  const propose = async () => {
    const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
    const resp = await API.proposeTrade(trade);
    planText = JSON.stringify(resp, null, 2);
    renderView();
  };
  const renderView = () => html`
    <section style="margin-top:16px;">
      <h2>Manager console</h2>
      <button style="padding:8px 12px; background:#1e2738; color:#eaf0ff; border:0; border-radius:6px;" @click=${propose}>
        Propose trade
      </button>
      <pre style="background:#121426; padding:12px; border-radius:8px; margin-top:12px;">${planText}</pre>
    </section>
  `;
  return renderView();
};
EOF

cat > "$WEB/src/components/ClientPortal.tsx" << 'EOF'
import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ClientPortal = () => {
  let vaultText = 'Loading vault snapshot...';
  const load = async () => {
    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
    } catch (e) {
      vaultText = 'Failed to load vault.';
    }
    renderView();
  };
  // initial load
  load();

  const renderView = () => html`
    <section style="margin-top:16px;">
      <h2>Client portal</h2>
      <pre style="background:#121426; padding:12px; border-radius:8px;">${vaultText}</pre>
    </section>
  `;
  return renderView();
};
EOF

cat > "$WEB/src/modules/allocation/AllocationConfig.ts" << 'EOF'
export const DEFAULT_VISIBLE_WEIGHT = 0.25;
export const DEFAULT_HIDDEN_WEIGHT = 0.75;
export const MIN_LOT = 0.001;
export const ROUNDING_STRATEGY = 'round-down';
export const RESIDUAL_HANDLING = 'round-robin';
export const DUST_THRESHOLD_USD = 0.5;
EOF

cat > "$WEB/src/modules/policy/PolicyEvaluator.ts" << 'EOF'
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
  id?: string;
  asset: string;
  direction: 'buy' | 'sell';
  totalSize: number;
  timestamp?: number;
  strategyId: string;
  priceLimit?: number;
  tags?: string[];
};

export const PolicyEvaluator = {
  isEligible(_client: ClientProfile, _asset: string) {
    return { eligible: true, reasons: [] as string[] };
  }
};
EOF

cat > "$WEB/src/modules/allocation/AllocationEngine.ts" << 'EOF'
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
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h << 5) - h + seed.charCodeAt(i);
  return 'PLAN-' + (h >>> 0).toString(16);
}

export function proposeAllocation(trade: TradeProposal, clients: ClientProfile[]): AllocationPlan {
  const t = { ...trade, id: trade.id || 'TX-' + Date.now(), timestamp: Date.now() };
  const eligible = clients.filter(c => PolicyEvaluator.isEligible(c, t.asset).eligible);
  const caps = eligible.map(c => {
    const visibleCap = c.totalCapital * (c.visibleAllocationPercent ?? DEFAULT_VISIBLE_WEIGHT);
    const hiddenCap = c.totalCapital * (c.hiddenAllocationPercent ?? DEFAULT_HIDDEN_WEIGHT);
    return { clientId: c.clientId, visibleCap, hiddenCap };
  });
  const totalVis = caps.reduce((s, x) => s + x.visibleCap, 0);
  const totalHid = caps.reduce((s, x) => s + x.hiddenCap, 0);
  const allocations: AllocationEntry[] = [];
  for (const c of caps) {
    const w = totalVis > 0 ? c.visibleCap / totalVis : 0;
    let size = Math.floor((t.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'visible', constraintsApplied: [] });
  }
  for (const c of caps) {
    const w = totalHid > 0 ? c.hiddenCap / totalHid : 0;
    let size = Math.floor((t.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'hidden', constraintsApplied: [] });
  }
  const allocatedSum = allocations.reduce((s, a) => s + a.allocatedSize, 0);
  let residual = t.totalSize - allocatedSum;
  let idx = 0;
  while (residual >= MIN_LOT && allocations.length > 0) {
    allocations[idx % allocations.length].allocatedSize += MIN_LOT;
    residual -= MIN_LOT; idx++;
  }
  const createdAt = Date.now();
  const planHash = hashPlan(JSON.stringify({ t, allocations, createdAt }));
  return { tradeId: t.id!, asset: t.asset, direction: t.direction, allocations, fillStatus: 'pending', createdAt, planHash };
}
EOF

echo "Updating Termux headless node with REST API..."
cat > "$TERMUX/bin/headless-node.sh" << 'EOF'
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
chmod +x "$TERMUX/bin/headless-node.sh"

cat > "$TERMUX/src/allocation/AllocationEngine.ts" << 'EOF'
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
  id?: string;
  asset: string;
  direction: 'buy' | 'sell';
  totalSize: number;
  timestamp?: number;
  strategyId: string;
  priceLimit?: number;
  tags?: string[];
};

const DEFAULT_VISIBLE_WEIGHT = 0.25;
const DEFAULT_HIDDEN_WEIGHT = 0.75;
const MIN_LOT = 0.001;

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
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h << 5) - h + seed.charCodeAt(i);
  return 'PLAN-' + (h >>> 0).toString(16);
}

export function proposeAllocation(trade: TradeProposal, clients: ClientProfile[]): AllocationPlan {
  const t = { ...trade, id: trade.id || 'TX-' + Date.now(), timestamp: Date.now() };
  const caps = clients.map(c => {
    const visibleCap = c.totalCapital * (c.visibleAllocationPercent ?? DEFAULT_VISIBLE_WEIGHT);
    const hiddenCap = c.totalCapital * (c.hiddenAllocationPercent ?? DEFAULT_HIDDEN_WEIGHT);
    return { clientId: c.clientId, visibleCap, hiddenCap };
  });
  const totalVis = caps.reduce((s, x) => s + x.visibleCap, 0);
  const totalHid = caps.reduce((s, x) => s + x.hiddenCap, 0);
  const allocations: AllocationEntry[] = [];
  for (const c of caps) {
    const w = totalVis > 0 ? c.visibleCap / totalVis : 0;
    let size = Math.floor((t.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'visible', constraintsApplied: [] });
  }
  for (const c of caps) {
    const w = totalHid > 0 ? c.hiddenCap / totalHid : 0;
    let size = Math.floor((t.totalSize * w) / MIN_LOT) * MIN_LOT;
    if (size > 0) allocations.push({ clientId: c.clientId, allocatedSize: size, allocationSource: 'hidden', constraintsApplied: [] });
  }
  const allocatedSum = allocations.reduce((s, a) => s + a.allocatedSize, 0);
  let residual = t.totalSize - allocatedSum;
  let idx = 0;
  while (residual >= MIN_LOT && allocations.length > 0) {
    allocations[idx % allocations.length].allocatedSize += MIN_LOT;
    residual -= MIN_LOT; idx++;
  }
  const createdAt = Date.now();
  const planHash = hashPlan(JSON.stringify({ t, allocations, createdAt }));
  return { tradeId: t.id!, asset: t.asset, direction: t.direction, allocations, fillStatus: 'pending', createdAt, planHash };
}
EOF

cat > "$TERMUX/src/node.ts" << 'EOF'
import http from 'http';
import fs from 'fs';
import path from 'path';
import url from 'url';
import { proposeAllocation, TradeProposal, ClientProfile } from './allocation/AllocationEngine';

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
const VAULT_FILE = path.join(DATA_DIR, 'vault.json');
const PLANS_FILE = path.join(DATA_DIR, 'plans.json');

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(LOG_DIR, { recursive: true });
if (!fs.existsSync(VAULT_FILE)) fs.writeFileSync(VAULT_FILE, JSON.stringify({ lots: {}, clients: {} }, null, 2), 'utf8');
if (!fs.existsSync(PLANS_FILE)) fs.writeFileSync(PLANS_FILE, JSON.stringify({ plans: [] }, null, 2), 'utf8');

function readJSON(file: string) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return {}; }
}
function writeJSON(file: string, obj: any) {
  fs.writeFileSync(file, JSON.stringify(obj, null, 2), 'utf8');
}

const defaultClients: ClientProfile[] = [
  { clientId: 'C001', walletAddress: 'w1', totalCapital: 10000, policyIds: [], feeProfileId: 'F1', performanceMetrics: { cumulativePnL: 0, lastNAV: 10000, highWaterMark: 10000 } },
  { clientId: 'C002', walletAddress: 'w2', totalCapital: 25000, policyIds: [], feeProfileId: 'F1', performanceMetrics: { cumulativePnL: 0, lastNAV: 25000, highWaterMark: 25000 } }
];

function cors(res: http.ServerResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

const server = http.createServer(async (req, res) => {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  const parsed = url.parse(req.url || '', true);
  const pathname = parsed.pathname || '/';

  if (pathname === '/status' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', nodeId: env.SWARM_NODE_ID || 'unknown', dataDir: DATA_DIR }));
    return;
  }

  if (pathname === '/plans' && req.method === 'GET') {
    const plans = readJSON(PLANS_FILE);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(plans));
    return;
  }

  if (pathname?.startsWith('/vault') && req.method === 'GET') {
    const vault = readJSON(VAULT_FILE);
    const parts = pathname.split('/').filter(Boolean);
    if (parts.length === 2) {
      const clientId = parts[1];
      const clientLots = (vault.lots || {})[clientId] || [];
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ clientId, lots: clientLots }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(vault));
    return;
  }

  if (pathname === '/proposeTrade' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const payload = JSON.parse(body || '{}') as Partial<TradeProposal>;
        const trade: TradeProposal = {
          id: payload.id,
          asset: payload.asset || 'ETH/USDT',
          direction: (payload.direction as any) || 'buy',
          totalSize: payload.totalSize || 5,
          timestamp: Date.now(),
          strategyId: payload.strategyId || 'S1'
        };
        const plans = readJSON(PLANS_FILE);
        const plan = proposeAllocation(trade, defaultClients);
        plans.plans = (plans.plans || []);
        plans.plans.push(plan);
        writeJSON(PLANS_FILE, plans);

        // update vault with credited lots (placeholder: add lots per allocation)
        const vault = readJSON(VAULT_FILE);
        vault.lots = vault.lots || {};
        for (const entry of plan.allocations) {
          vault.lots[entry.clientId] = vault.lots[entry.clientId] || [];
          vault.lots[entry.clientId].push({ asset: plan.asset, qty: entry.allocatedSize, price: 0, ts: Date.now() });
        }
        writeJSON(VAULT_FILE, vault);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(plan));
      } catch (e: any) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid payload', detail: e?.message }));
      }
    });
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(8080, () => {
  console.log('Headless node API at http://127.0.0.1:8080');
});
EOF

echo "Scripts & infra placeholders..."
cat > "$SCRIPTS/build.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
npm install
npm run build:web
EOF
chmod +x "$SCRIPTS/build.sh"

cat > "$SCRIPTS/publish-webtorrent.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
echo "Placeholder: WebTorrent publishing not yet implemented."
EOF
chmod +x "$SCRIPTS/publish-webtorrent.sh"

cat > "$INFRA/ipfs-pinning/pin-config.json" << 'EOF'
{ "pinningService": "custom", "api": "http://127.0.0.1:5001" }
EOF

cat > "$INFRA/webseed/nginx.conf" << 'EOF'
server { listen 8089; root /var/www/commingle-swarm; }
EOF

echo "Assets placeholders..."
echo "# icons placeholder" > "$ASSETS/icons/.keep"

echo "Upgrade complete."
echo "Next:"
echo "1) cd $ROOT"
echo "2) npm install"
echo "3) ./termux/bin/headless-node.sh   # starts API on :8080"
echo "4) In a second session: cd $WEB && npm install && npm run build && npm run serve"
echo "5) Open http://localhost:8088 and click 'Propose trade' to hit the node."
