import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ClientPortal = (reRender: () => void) => {
  let vaultText = 'Loading vault snapshot...';
  let isLoading = true;

  const load = async () => {
    isLoading = true;
    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
    } catch (e) {
      vaultText = 'Failed to load vault.';
    } finally {
      isLoading = false;
      reRender();
    }
  };

  // initial load deferred using setTimeout to ensure parent components complete instantiation first
  setTimeout(() => {
    load();
  }, 0);

  return () => html`
    <section style="padding:16px; background:#111625; border-radius:10px; border:1px solid #1e2738;">
      <h2 style="margin-top:0; color:#93c5fd; font-size:20px;">Client Portal</h2>
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        <span style="font-size:14px; color:#94a3b8;">Vault snapshot:</span>
        ${isLoading ? html`<span style="font-size:12px; color:#fbbf24; animation: pulse 1.5s infinite; font-weight:500;">⏳ Fetching...</span>` : ''}
      </div>
      <pre style="background:#090d16; padding:14px; border-radius:8px; border:1px solid #1a2035; overflow-x:auto; font-family:monospace; font-size:13px; color:#c7d2fe; margin-top:0;">${vaultText}</pre>
    </section>
  `;
};
