import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const appEl = document.getElementById('app')!;

const reRender = () => {
  render(App(), appEl);
};

// Instantiate components once to maintain their state/closures
const managerConsole = ManagerConsole(reRender);
const clientPortal = ClientPortal(reRender);

const App = () => html`
  <main style="min-height:100vh; padding:24px; max-width:800px; margin:0 auto; font-family:system-ui, -apple-system, sans-serif;">
    <h1 style="border-bottom: 2px solid #1e2738; padding-bottom: 12px; margin-bottom: 24px; color:#f8fafc; font-size:32px; letter-spacing:-0.5px;">Commingle Swarm</h1>
    <div style="display:flex; flex-direction:column; gap:24px;">
      ${managerConsole()}
      ${clientPortal()}
    </div>
  </main>
`;

reRender();
