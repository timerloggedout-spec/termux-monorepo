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
