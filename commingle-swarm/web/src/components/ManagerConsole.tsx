import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ManagerConsole = (reRender: () => void) => {
  let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
  let isProposing = false;

  const propose = async () => {
    if (isProposing) return;
    isProposing = true;
    planText = 'Proposing trade...';
    reRender();

    try {
      const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
      const resp = await API.proposeTrade(trade);
      planText = JSON.stringify(resp, null, 2);
    } catch (e) {
      planText = 'Failed to propose trade. Make sure the Node server is running.';
    } finally {
      isProposing = false;
    }
    reRender();
  };

  return () => html`
    <section style="margin-top:24px; padding: 16px; background: #161925; border-radius: 8px; border: 1px solid #23283d;">
      <h2 style="margin-top: 0; color: #ffcb6b;">Manager Console</h2>
      <button
        style="padding:10px 16px; background: ${isProposing ? '#2e3a50' : '#1e2738'}; color:#eaf0ff; border:0; border-radius:6px; cursor: ${isProposing ? 'not-allowed' : 'pointer'}; font-weight: 500; display: inline-flex; align-items: center; gap: 8px; font-size: 14px;"
        @click=${propose}
        ?disabled=${isProposing}
        aria-label="Propose ETH/USDT trade"
      >
        ${isProposing ? 'Proposing...' : 'Propose trade'}
      </button>
      <pre style="background:#0f111a; padding:12px; border-radius:6px; margin-top:12px; overflow-x: auto; border: 1px solid #1e2235; font-family: monospace; color: #addb67;">${planText}</pre>
    </section>
  `;
};
