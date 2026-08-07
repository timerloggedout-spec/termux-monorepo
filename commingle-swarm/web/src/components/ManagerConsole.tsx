import { html } from 'lit-html';
import * as API from '../api/NodeClient';

let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
let isProposing = false;

export const ManagerConsole = (reRender: () => void) => {
  const propose = async () => {
    if (isProposing) return;
    isProposing = true;
    planText = 'Generating allocation plan...';
    reRender();

    try {
      const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
      const resp = await API.proposeTrade(trade);
      planText = JSON.stringify(resp, null, 2);
    } catch (e: any) {
      planText = `Failed to generate trade allocation plan: ${e?.message || e}`;
    } finally {
      isProposing = false;
      reRender();
    }
  };

  return html`
    <section style="margin-top:24px;">
      <h2 style="font-size:1.5rem; font-weight:600; margin-bottom:8px;">Manager Console</h2>
      <button
        style="padding:10px 16px; background:${isProposing ? '#151b26' : '#1e2738'}; color:${isProposing ? '#7d8a9e' : '#eaf0ff'}; border:1px solid #2d3b55; border-radius:6px; cursor:${isProposing ? 'not-allowed' : 'pointer'}; font-weight:500; font-size:0.95rem; transition: background 0.2s ease;"
        ?disabled=${isProposing}
        aria-busy=${isProposing ? 'true' : 'false'}
        aria-label="Propose trade and generate allocation plan"
        @click=${propose}
      >
        ${isProposing ? '⏳ Generating Plan...' : '💼 Propose Trade'}
      </button>
      <pre style="background:#121426; padding:14px; border-radius:8px; margin-top:12px; border:1px solid #1a1f36; overflow-x:auto; font-family:monospace; font-size:0.9rem;">${planText}</pre>
    </section>
  `;
};
