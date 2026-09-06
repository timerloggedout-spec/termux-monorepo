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
      vaultText = 'Failed to load vault. Click refresh to retry.';
    } finally {
      isLoading = false;
      reRender();
    }
  };

  // Defer initialization task using setTimeout to ensure parent completes instantiation first
  setTimeout(load, 0);

  return () => html`
    <section style="margin-top:16px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
        <h2>Client portal</h2>
        <button
          aria-label="Refresh vault snapshot"
          aria-busy="${isLoading}"
          ?disabled=${isLoading}
          style="padding:6px 12px; background:#1e2738; color:#eaf0ff; border:0; border-radius:6px; cursor:${isLoading ? 'not-allowed' : 'pointer'}; opacity:${isLoading ? '0.7' : '1'}; transition: opacity 0.2s ease;"
          @click=${load}
        >
          ${isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <pre
        aria-live="polite"
        aria-label="Vault snapshot output"
        style="background:#121426; padding:12px; border-radius:8px;"
      >${vaultText}</pre>
    </section>
  `;
};
