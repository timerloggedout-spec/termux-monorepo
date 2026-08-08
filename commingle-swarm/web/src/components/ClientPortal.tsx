import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ClientPortal = (reRender: () => void) => {
  let vaultText = 'Loading vault snapshot...';
  let isLoading = true;

  const load = async () => {
    isLoading = true;
    reRender();
    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
    } catch (e) {
      vaultText = 'Failed to load vault.';
    } finally {
      isLoading = false;
    }
    reRender();
  };

  // Defer initial load to the next event loop tick to ensure index.tsx completes instantiation first.
  setTimeout(load, 0);

  return () => html`
    <section style="margin-top:24px; padding: 16px; background: #161925; border-radius: 8px; border: 1px solid #23283d;">
      <h2 style="margin-top: 0; color: #82aaff; display: flex; align-items: center; gap: 8px;">
        Client Portal
        ${isLoading ? html`<span style="font-size: 14px; color: #8e94b1; font-weight: normal;">(Updating...)</span>` : ''}
      </h2>
      <pre style="background:#0f111a; padding:12px; border-radius:6px; overflow-x: auto; border: 1px solid #1e2235; font-family: monospace; color: #c3e88d;">${vaultText}</pre>
    </section>
  `;
};
