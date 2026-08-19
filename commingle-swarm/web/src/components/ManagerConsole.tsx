import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ManagerConsole = (reRender: () => void) => {
  let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
  const propose = async () => {
    const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
    const resp = await API.proposeTrade(trade);
    planText = JSON.stringify(resp, null, 2);
    reRender();
  };
  return () => html`
    <section style="margin-top:16px;">
      <h2>Manager console</h2>
      <button
        aria-label="Propose trade allocation plan"
        style="padding:8px 12px; background:#1e2738; color:#eaf0ff; border:0; border-radius:6px; cursor:pointer;"
        @click=${propose}
      >
        Propose trade
      </button>
      <pre
        aria-live="polite"
        aria-label="Trade proposal output"
        style="background:#121426; padding:12px; border-radius:8px; margin-top:12px;"
      >${planText}</pre>
    </section>
  `;
};
