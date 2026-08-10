import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ManagerConsole = (reRender: () => void) => {
  let planText = 'Click "Propose trade" to generate an allocation plan via the node.';
  let loading = false;

  const propose = async () => {
    if (loading) return;
    loading = true;
    planText = 'Proposing trade allocation...';
    reRender();

    try {
      const trade = { asset: 'ETH/USDT', direction: 'buy', totalSize: 5, strategyId: 'S1' };
      const resp = await API.proposeTrade(trade);
      planText = JSON.stringify(resp, null, 2);
    } catch (e: any) {
      planText = `Error proposing trade: ${e?.message || e}`;
    } finally {
      loading = false;
      reRender();
    }
  };

  return () => html`
    <section style="margin-top:16px; background:#161b26; padding:16px; border-radius:8px;" aria-labelledby="manager-console-heading">
      <h2 id="manager-console-heading" style="margin-top:0; font-size:1.25rem;">Manager console</h2>
      <button
        style="padding:8px 12px; background:${loading ? '#2d3748' : '#1e2738'}; color:${loading ? '#a0aec0' : '#eaf0ff'}; border:0; border-radius:6px; cursor:${loading ? 'not-allowed' : 'pointer'}; font-weight:bold; transition: background 0.2s; outline: none;"
        ?disabled=${loading}
        aria-label="Propose trade allocation"
        aria-busy=${loading ? 'true' : 'false'}
        @click=${propose}
      >
        ${loading ? 'Proposing...' : 'Propose trade'}
      </button>
      <div aria-live="polite" style="margin-top:12px;">
        <pre style="background:#121426; padding:12px; border-radius:8px; margin:0; overflow-x:auto; border: 1px solid #1e2738; font-family:monospace; font-size:0.875rem;">${planText}</pre>
      </div>
    </section>
  `;
};
