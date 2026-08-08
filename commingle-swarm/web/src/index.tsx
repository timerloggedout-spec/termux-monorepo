import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const reRender = () => {
  render(App(), document.getElementById('app')!);
};

const managerConsole = ManagerConsole(reRender);
const clientPortal = ClientPortal(reRender);

function App() {
  return html`
    <main style="min-height:100vh; padding:16px; font-family: system-ui, -apple-system, sans-serif; background: #0f111a; color: #eaf0ff;">
      <h1 style="border-bottom: 1px solid #1e2738; padding-bottom: 12px; margin-bottom: 24px;">Commingle Swarm</h1>
      ${managerConsole()}
      ${clientPortal()}
    </main>
  `;
}

reRender();
