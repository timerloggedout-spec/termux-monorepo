#!/usr/bin/env node
const readline = require('readline');
const { execSync } = require('child_process');

const rl = readline.createInterface({ input: process.stdin });

let buffer = '';
rl.on('line', (line) => {
  buffer += line;
  try {
    const req = JSON.parse(buffer);
    buffer = '';
    handle(req);
  } catch (_) { /* wait for more lines */ }
});

function handle(req) {
  const { method, params, id } = req;
  let result = null;
  if (method === 'tools/list') {
    result = {
      tools: [
        { name: 'cedar_validate', description: 'Validate CEDARscript syntax' },
        { name: 'cedar_eval',     description: 'Evaluate CEDARscript policy' }
      ]
    };
  } else if (method === 'tools/call') {
    const { name, arguments: args } = params;
    if (name === 'cedar_validate') {
      const code = Buffer.from(args.code, 'base64').toString();
      result = { content: [{ type: 'text', text: execSync(`cedar validate --schema ${args.schema} -p ${code}`).toString() }] };
    } else if (name === 'cedar_eval') {
      const code = Buffer.from(args.code, 'base64').toString();
      result = { content: [{ type: 'text', text: execSync(`cedar evaluate --schema ${args.schema} --input ${args.input}`).toString() }] };
    }
  }
  process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id, result }) + '\n');
}
