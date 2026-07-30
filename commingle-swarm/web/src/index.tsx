import { html, render } from 'lit-html';
import { ManagerConsole } from './components/ManagerConsole';
import { ClientPortal } from './components/ClientPortal';

const App = () => html`
  <main style="min-height:100vh; padding:16px;">
    <h1>Commingle Swarm</h1>
    ${ManagerConsole()}
    ${ClientPortal()}
  </main>
`;
render(App(), document.getElementById('app')!);
