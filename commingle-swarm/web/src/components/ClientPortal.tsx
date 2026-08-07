import { html } from 'lit-html';
import * as API from '../api/NodeClient';

let vaultText = 'Waiting to load vault snapshot...';
let isRefreshing = false;
let initialized = false;
let lastUpdated: string | null = null;

export const ClientPortal = (reRender: () => void) => {
  const load = async () => {
    if (isRefreshing) return;
    isRefreshing = true;
    reRender();

    try {
      const v = await API.getVault();
      vaultText = JSON.stringify(v, null, 2);
      lastUpdated = new Date().toLocaleTimeString();
    } catch (e: any) {
      vaultText = `Failed to connect to the swarm headless node.\nEnsure the node is running with:\n  pnpm start:node`;
      lastUpdated = null;
    } finally {
      isRefreshing = false;
      reRender();
    }
  };

  if (!initialized) {
    initialized = true;
    load();
  }

  return html`
    <section style="margin-top:32px; border-top: 1px solid #1c2333; padding-top:24px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; flex-wrap:wrap; gap:12px;">
        <h2 style="font-size:1.5rem; font-weight:600; margin:0;">Client Portal</h2>
        <div style="display:flex; align-items:center; gap:12px;">
          ${lastUpdated ? html`<span style="font-size:0.85rem; color:#7d8a9e;" aria-live="polite">Last sync: ${lastUpdated}</span>` : ''}
          <button
            style="padding:8px 14px; background:${isRefreshing ? '#151b26' : '#222d42'}; color:${isRefreshing ? '#7d8a9e' : '#eaf0ff'}; border:1px solid #334464; border-radius:6px; cursor:${isRefreshing ? 'not-allowed' : 'pointer'}; font-weight:500; font-size:0.85rem; transition: background 0.2s ease;"
            ?disabled=${isRefreshing}
            aria-busy=${isRefreshing ? 'true' : 'false'}
            aria-label="Refresh vault snapshot data"
            @click=${load}
          >
            ${isRefreshing ? '🔄 Refreshing...' : '🔄 Refresh Vault'}
          </button>
        </div>
      </div>
      <p style="font-size:0.95rem; color:#a2b1c6; margin-top:0; margin-bottom:12px;">
        Monitor real-time balance allocations, credited asset lots, and client vault status across all swarm addresses.
      </p>
      <pre
        style="background:#121426; padding:14px; border-radius:8px; border:1px solid #1a1f36; overflow-x:auto; font-family:monospace; font-size:0.9rem;"
        aria-live="polite"
      >${vaultText}</pre>
    </section>
  `;
};
