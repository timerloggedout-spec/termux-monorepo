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
