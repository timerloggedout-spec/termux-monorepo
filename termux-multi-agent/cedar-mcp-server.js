#!/usr/bin/env node
const readline = require('readline');
const { execFileSync } = require('child_process');

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

function safeExecCedar(argsList) {
  try {
    return execFileSync('cedar', argsList).toString();
  } catch (error) {
    const out = error.stdout ? error.stdout.toString() : '';
    const err = error.stderr ? error.stderr.toString() : '';
    if (out || err) {
      return (out + '\n' + err).trim();
    }
    return error.message;
  }
}

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
      const code = args.code ? Buffer.from(args.code, 'base64').toString() : '';
      const output = safeExecCedar(['validate', '--schema', args.schema || '', '-p', code]);
      result = { content: [{ type: 'text', text: output }] };
    } else if (name === 'cedar_eval') {
      const output = safeExecCedar(['evaluate', '--schema', args.schema || '', '--input', args.input || '']);
      result = { content: [{ type: 'text', text: output }] };
    }
  }
  process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id, result }) + '\n');
}
