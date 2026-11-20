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
