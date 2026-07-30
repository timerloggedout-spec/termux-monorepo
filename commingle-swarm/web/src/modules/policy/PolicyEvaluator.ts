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
