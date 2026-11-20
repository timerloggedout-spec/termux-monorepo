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
