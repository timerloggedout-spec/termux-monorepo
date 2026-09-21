const fs = require('fs');
const { spawnSync } = require('child_process');

const root = process.env.GITHUB_WORKSPACE || process.cwd();
const outputFile = process.env.GITHUB_OUTPUT;
const catalogPath = '/tmp/model-catalog/catalog.json';
const keys = {
  openrouter: String(process.env.INPUT_OPENROUTER_KEY || ''),
  felo: String(process.env.INPUT_FELO_KEY || ''),
  omni: String(process.env.INPUT_OMNI_KEY || ''),
  omniroute: String(process.env.INPUT_OMNIROUTE_KEY || ''),
};

function setOutput(name, value) {
  if (outputFile) fs.appendFileSync(outputFile, name + '=' + String(value) + '\n');
}
function mask(value) {
  if (value) process.stdout.write('::add-mask::' + value + '\n');
}

async function main() {
  Object.values(keys).forEach(mask);
  fs.mkdirSync('/tmp/model-catalog', { recursive: true });
  const env = { ...process.env };
  if (keys.openrouter) env.OPENROUTER_API_KEY = keys.openrouter;
  if (keys.felo) env.FELO_AI_API = keys.felo;
  env.OMNI_API_KEY = keys.omni || keys.omniroute || '';
  const result = spawnSync(
    'python3',
    ['scripts/provider_model_catalog.py', '--providers', 'openrouter,felo,omni', '--output', catalogPath],
    { cwd: root, env, encoding: 'utf8' }
  );
  if (result.status !== 0) console.log('::warning::provider catalog exited non-zero; evaluating any emitted catalog');
  if (!fs.existsSync(catalogPath)) { setOutput('skip', 'true'); console.log('no catalog'); return; }
  const doc = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  const rows = Array.isArray(doc.models) ? doc.models : [];
  const eligible = rows.filter(r => r.pricing_classification === 'free_zero_price' || r.free_suffix || r.access_classification === 'free_trial');
  function score(r) {
    const mid = String(r.id || '').toLowerCase();
    let s = 0;
    if (['coder','code','qwen','deepseek','ox-alpha'].some(k => mid.includes(k))) s += 50;
    if (r.provider === 'openrouter') s += 20;
    if (r.provider === 'felo') s += 15;
    if (r.free_suffix || r.pricing_classification === 'free_zero_price') s += 10;
    return s;
  }
  eligible.sort((a,b) => score(b) - score(a));
  if (!eligible.length) {
    if (keys.openrouter) { setOutput('skip','false'); setOutput('provider','openrouter'); setOutput('model','qwen/qwen3-coder:free'); console.log('fallback list qwen3-coder:free'); return; }
    setOutput('skip','true'); console.log('no eligible free models'); return;
  }
  const top = eligible[0];
  setOutput('skip','false'); setOutput('provider', top.provider); setOutput('model', top.id);
  console.log('selected provider model from live catalog; models=' + rows.length + ' eligible=' + eligible.length);
}
main().catch(error => {
  setOutput('skip', 'true');
  console.log('::error::provider catalog action failed: ' + String(error.message || error));
  process.exitCode = 1;
});
