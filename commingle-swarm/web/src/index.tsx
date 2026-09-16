import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const container = document.getElementById('app')!;

const reRender = () => {
  render(App(), container);
};

// Initialize the subcomponents once as factory closures accepting the reRender callback
const renderManager = ManagerConsole(reRender);
const renderClient = ClientPortal(reRender);

const App = () => html`
  <main aria-label="Commingle Swarm Dashboard" style="min-height:100vh; padding:16px;">
    <h1>Commingle Swarm</h1>
    ${renderManager()}
    ${renderClient()}
  </main>
`;

// Initial mount
reRender();
