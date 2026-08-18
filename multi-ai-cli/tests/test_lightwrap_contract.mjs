import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  getProfile,
  hashObject,
  loadCatalog,
  parseArgs,
  pathsFor,
  readyToSend,
  saveStatus,
} from '../wrapper/lightwrap.mjs';

const catalog = loadCatalog();
assert.equal(catalog.schema_version, 1);
assert.deepEqual(
  catalog.providers.map((entry) => entry.id),
  ['deepseek', 'mistral', 'ai_studio', 'perplexity', 'openai_web', 'liner', 'openrouter'],
);

const args = parseArgs(['--action', 'probe', '--provider', 'deepseek', '--account', 'primary', '--headed']);
assert.equal(args.action, 'probe');
assert.equal(args.provider, 'deepseek');
assert.equal(args.account, 'primary');
assert.equal(args.headed, true);

const deepseek = getProfile(catalog, 'deepseek');
assert.equal(deepseek.kind, 'browser-wrapper');
assert.equal(deepseek.allow_send_after_probe, true);
const liner = getProfile(catalog, 'liner');
assert.equal(liner.state, 'discovery-required');
assert.equal(liner.allow_send_after_probe, false);

const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'lightwrap-contract-'));
try {
  const locations = pathsFor(temporaryRoot, 'deepseek', 'primary');
  const status = {
    observed_state: 'send-ready',
    profile_fingerprint: hashObject(deepseek),
    selector_summary: { input: true, submit: true, ready: true },
  };
  saveStatus(locations.statusPath, status);
  assert.equal(readyToSend(deepseek, status), true);
  assert.equal(fs.statSync(locations.statusPath).mode & 0o777, 0o600);
  assert.equal(readyToSend(liner, status), false);
} finally {
  fs.rmSync(temporaryRoot, { recursive: true, force: true });
}

console.log('lightwrap contract: ok');
