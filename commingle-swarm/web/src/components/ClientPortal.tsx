import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ClientPortal = (reRender: () => void) => {
  let vaultText = 'Loading vault snapshot...';
  const load = async () => {
    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
    } catch (e) {
      vaultText = 'Failed to load vault.';
    }
    reRender();
  };

  // Defer initialization task using setTimeout to ensure parent completes instantiation first
  setTimeout(load, 0);

  return () => html`
    <section style="margin-top:16px;">
      <h2>Client portal</h2>
      <pre style="background:#121426; padding:12px; border-radius:8px;">${vaultText}</pre>
    </section>
  `;
};
