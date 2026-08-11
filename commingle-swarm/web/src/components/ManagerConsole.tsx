import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ManagerConsole = (reRender: () => void) => {
  let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
  let isProposing = false;

  const propose = async () => {
    if (isProposing) return;
    isProposing = true;
    planText = 'Generating allocation plan...';
    reRender();

    try {
      const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
      const resp = await API.proposeTrade(trade);
      planText = JSON.stringify(resp, null, 2);
    } catch (e) {
      planText = 'Failed to generate allocation plan.';
    } finally {
      isProposing = false;
      reRender();
    }
  };

  return () => html`
    <section style="padding:16px; background:#111625; border-radius:10px; border:1px solid #1e2738;">
      <h2 style="margin-top:0; color:#93c5fd; font-size:20px;">Manager Console</h2>
      <button
        style="padding:10px 16px; background:${isProposing ? '#1e293b' : '#2563eb'}; color:${isProposing ? '#94a3b8' : '#ffffff'}; border:0; border-radius:6px; cursor:${isProposing ? 'not-allowed' : 'pointer'}; font-weight:500; font-size:14px; display:inline-flex; align-items:center; gap:8px; box-shadow:0 1px 2px rgba(0,0,0,0.05);"
        ?disabled=${isProposing}
        aria-busy=${isProposing ? 'true' : 'false'}
        aria-label="Propose trade allocation plan"
        @click=${propose}
      >
        ${isProposing ? '⏳ Proposing trade...' : '🚀 Propose trade'}
      </button>
      <pre style="background:#090d16; padding:14px; border-radius:8px; margin-top:14px; border:1px solid #1a2035; overflow-x:auto; font-family:monospace; font-size:13px; color:#c7d2fe;">${planText}</pre>
    </section>
  `;
};
