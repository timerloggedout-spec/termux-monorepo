const fs = require('fs');

const provider = String(process.env.INPUT_PROVIDER || '').trim();
const model = String(process.env.INPUT_MODEL || '').trim();
const promptPath = String(process.env.INPUT_PROMPT_PATH || '').trim();
const apiKey = String(process.env.INPUT_API_KEY || '');
const outputFile = process.env.GITHUB_OUTPUT;
const bodyFile = '/tmp/hw-llm-body.txt';

function setOutput(name, value) {
  if (!outputFile) return;
  fs.appendFileSync(outputFile, name + '=' + String(value) + '\n');
}
function mask(value) {
  if (value) process.stdout.write('::add-mask::' + value + '\n');
}
function endpointFor(name) {
  switch (name) {
    case 'openrouter': return 'https://openrouter.ai/api/v1/chat/completions';
    case 'felo': return 'https://openapi.felo.ai/api/v1/chat/completions';
    case 'omni': return 'https://cloud.omniroute.online/v1/chat/completions';
    default: return null;
  }
}
async function main() {
  const endpoint = endpointFor(provider);
  if (!endpoint || !model || !promptPath) throw new Error('invalid provider action inputs');
  mask(apiKey);
  if (!apiKey) { setOutput('skip', 'true'); console.log('::warning::missing API key for ' + provider); return; }
  const prompt = fs.readFileSync(promptPath, 'utf8');
  const payload = { model, messages: [{ role: 'user', content: prompt }], max_tokens: 2048, stream: false };
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + apiKey,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://github.com/timerloggedout-spec/termux-monorepo',
      'X-Title': 'help-wanted-llm-assist'
    },
    body: JSON.stringify(payload)
  });
  const raw = await response.text();
  let doc = null;
  try { doc = JSON.parse(raw); } catch (_) { doc = null; }
  if (!response.ok) { setOutput('skip', 'true'); console.log('::warning::provider ' + provider + ' returned HTTP ' + response.status); return; }
  const text = doc && doc.choices && doc.choices[0] && doc.choices[0].message && doc.choices[0].message.content;
  if (typeof text !== 'string' || !text.trim()) { setOutput('skip', 'true'); console.log('::warning::provider returned no assistant content'); return; }
  const body = [
    '### Help-wanted LLM assist (live catalog: `' + provider + '` / `' + model + '`)',
    '', text, '',
    '_Selection = live free/zero/trial catalog (openrouter|felo|omni). **Not** MoneyBall admission. Not legacy model-router residual chain._',
    ''
  ].join('\n');
  fs.writeFileSync(bodyFile, body, { mode: 0o600 });
  setOutput('skip', 'false');
  console.log('prepared help-wanted assist via ' + provider + '/' + model);
}
main().catch((error) => {
  setOutput('skip', 'true');
  console.log('::error::LLM assist invocation failed: ' + String(error.message || error));
  process.exitCode = 1;
});
