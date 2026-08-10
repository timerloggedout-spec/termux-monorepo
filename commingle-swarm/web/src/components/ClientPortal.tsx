import { html } from 'lit-html';
import * as API from '../api/NodeClient';

export const ClientPortal = (reRender: () => void) => {
  let vaultText = 'Loading vault snapshot...';
  let loading = false;

  const load = async () => {
    if (loading) return;
    loading = true;
    vaultText = 'Loading vault snapshot...';
    reRender();

    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
    } catch (e: any) {
      vaultText = `Failed to load vault. Error: ${e?.message || e}`;
    } finally {
      loading = false;
      reRender();
    }
  };

  // Deferred initial load using setTimeout to ensure parent completes rendering
  setTimeout(() => {
    load();
  }, 0);

  return () => html`
    <section style="margin-top:16px; background:#161b26; padding:16px; border-radius:8px;" aria-labelledby="client-portal-heading">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2 id="client-portal-heading" style="margin:0; font-size:1.25rem;">Client portal</h2>
        <button
          style="padding:6px 12px; background:${loading ? '#2d3748' : '#1e2738'}; color:${loading ? '#a0aec0' : '#eaf0ff'}; border:0; border-radius:6px; cursor:${loading ? 'not-allowed' : 'pointer'}; font-weight:bold; font-size:0.875rem; transition: background 0.2s; outline: none;"
          ?disabled=${loading}
          aria-label="Refresh vault snapshot"
          aria-busy=${loading ? 'true' : 'false'}
          @click=${load}
        >
          ${loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <div aria-live="polite" style="margin-top:12px;">
        <pre style="background:#121426; padding:12px; border-radius:8px; margin:0; overflow-x:auto; border: 1px solid #1e2738; font-family:monospace; font-size:0.875rem;">${vaultText}</pre>
      </div>
    </section>
  `;
};
