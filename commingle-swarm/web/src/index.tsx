import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const doRender = () => {
  render(App(), document.getElementById('app')!);
};

// Instantiate components once to maintain their local closures/state across re-renders
const consoleCmp = ManagerConsole(doRender);
const portalCmp = ClientPortal(doRender);

const App = () => html`
  <main style="min-height:100vh; padding:24px; max-width:800px; margin:0 auto; font-family:system-ui, -apple-system, sans-serif;">
    <h1 style="border-bottom: 2px solid #1e2738; padding-bottom: 12px; margin-bottom: 24px; color:#eaf0ff;">Commingle Swarm</h1>
    ${consoleCmp()}
    ${portalCmp()}
  </main>
`;

doRender();
