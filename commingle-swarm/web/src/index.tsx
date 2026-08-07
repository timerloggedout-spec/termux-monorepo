import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

export const reRender = () => {
  render(App(), document.getElementById('app')!);
};

const App = () => html`
  <main style="min-height:100vh; padding:16px;">
    <h1>Commingle Swarm</h1>
    ${ManagerConsole(reRender)}
    ${ClientPortal(reRender)}
  </main>
`;

reRender();
