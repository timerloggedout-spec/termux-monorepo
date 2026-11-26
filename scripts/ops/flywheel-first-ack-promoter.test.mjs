import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  CHANNEL_ID,
  applyPromotionPlans,
  parseJsonl,
  planPromotions,
  runOnce,
} from './flywheel-first-ack-promoter.mjs';

const PEERS = [
  'connector-specialist', 'q', 'antigravity-scout', 'techdebt', 'experimentslab',
  'devin-specialist', 'validatorwirencritiq', 'lab-spec', 'origin-archive-steward', 'swarms', 'sol',
];
const T0 = Date.parse('2026-11-26T10:00:00Z');
const NOW = Date.parse('2026-11-26T11:00:00Z');

function fixtureRegistry() {
  return {
    channels: [{
      id: CHANNEL_ID,
      name: 'cue-work-comms',
      status: 'established',
      store_repo: 'timerloggedout-spec/muse-vm-workspace-backup',
      path: 'cue/work-comms.jsonl (protocol: cue/WORK-COMMS.md)',
      format: 'JSONL append-only {ts, from, to, body}',
      participants: ['muse-vm', 'manus-cue', 'chatgpt-github'],
      pending_participants: PEERS.map(name => `${name} (onboarding, test fixture)`),
    }],
    peers: PEERS.map(name => ({
      name,
      status: 'ONBOARDING PENDING - first ACK on FLY-006 owed',
      channels: [CHANNEL_ID],
      note: name === 'swarms'
        ? 'COLLISION FLAG: screen before any promotion.'
        : 'Profile note is informational; first ACK remains the gate.',
    })),
  };
}

function requestRows(peers = PEERS) {
  return peers.map((name, index) => ({
    ts: new Date(T0 + index * 1000).toISOString(),
    from: 'muse-vm',
    to: name,
    body: `⌖FLY-006/onboarding → ▶${name}: post one first ACK on FLY-006 confirming the shared watcher.`,
  }));
}

function ackRow(from, ts, body = 'ACK: FLY-006 shared watcher confirmed.') {
  return { ts, from, to: 'muse-vm', body };
}

function makeIo(registry, rows) {
  let current = structuredClone(registry);
  let writes = 0;
  let registryReads = 0;
  let flywheelReads = 0;
  const readRegistry = async () => {
    registryReads++;
    return { registry: structuredClone(current), sha: `sha-${registryReads}` };
  };
  const readFlywheel = async () => {
    flywheelReads++;
    return structuredClone(rows);
  };
  const writeRegistry = async ({ registry, sha, promotions }) => {
    writes++;
    assert.equal(sha, `sha-${registryReads}`, 'write must use the freshly re-read Registry blob SHA');
    current = structuredClone(registry);
    return { promotions: promotions.map(item => item.peer) };
  };
  return {
    readRegistry,
    readFlywheel,
    writeRegistry,
    current: () => structuredClone(current),
    writes: () => writes,
    registryReads: () => registryReads,
    flywheelReads: () => flywheelReads,
  };
}

test('no qualifying ACK is a no-op even when apply mode is enabled', async () => {
  const io = makeIo(fixtureRegistry(), requestRows());
  const report = await runOnce({ ...io, apply: true, nowMs: NOW });
  assert.equal(report.pending_count, 11);
  assert.equal(report.promotions.length, 0);
  assert.equal(report.applied.length, 0);
  assert.equal(io.writes(), 0);
  assert.equal(report.diagnostics.length, 11);
  assert.ok(report.diagnostics.every(item => item.state === 'missing'));
});

test('sender identity, Registry channel assignment, and latest-request timestamp are all exact gates', () => {
  const registry = fixtureRegistry();
  const rows = requestRows();
  const qRequest = rows.find(row => row.to === 'q');
  qRequest.ts = '2026-11-26T10:05:00Z';
  rows.push(
    ackRow('q-copycat', '2026-11-26T10:06:00Z'),
    ackRow('q', '2026-11-26T10:04:59Z'),
    ackRow('q', '2026-11-26T10:06:30Z', 'ACK is still pending; this is a status, not the ACK.'),
  );
  const afterOldOrWrongSender = planPromotions(registry, rows, NOW);
  assert.equal(afterOldOrWrongSender.promotions.some(item => item.peer === 'q'), false);

  rows.push(ackRow('q', '2026-11-26T10:05:00Z'));
  const afterExactTimestamp = planPromotions(registry, rows, NOW);
  const q = afterExactTimestamp.promotions.find(item => item.peer === 'q');
  assert.ok(q, 'an exact-sender ACK at the latest request timestamp qualifies');
  assert.equal(q.ack.from, 'q');
  assert.equal(q.request_ts, qRequest.ts);

  const wrongChannelRegistry = fixtureRegistry();
  wrongChannelRegistry.peers.find(peer => peer.name === 'q').channels = ['FLY-005'];
  const wrongChannel = planPromotions(wrongChannelRegistry, rows, NOW);
  assert.equal(wrongChannel.promotions.some(item => item.peer === 'q'), false,
    'a FLY-006 row cannot promote a peer whose Registry channel assignment excludes FLY-006');
});

test('one invocation evaluates the full pending roster through one shared pass, with no per-peer matrix', async () => {
  const io = makeIo(fixtureRegistry(), requestRows());
  const report = await runOnce({ ...io, apply: false, nowMs: NOW });
  assert.equal(report.pending_count, 11);
  assert.equal(report.diagnostics.length, 11);
  assert.equal(io.registryReads(), 1);
  assert.equal(io.flywheelReads(), 1);

  const workflow = readFileSync(new URL('../../.github/workflows/flywheel-first-ack-promoter.yml', import.meta.url), 'utf8');
  assert.match(workflow, /jobs:\s*\n  promote:/);
  assert.doesNotMatch(workflow, /\bmatrix\s*:/i);
  assert.match(workflow, /scripts\/ops\/flywheel-first-ack-promoter\.mjs/);
});

test('the explicit swarms collision-screen hold blocks promotion after exact ACK evidence', () => {
  const report = planPromotions(fixtureRegistry(), [
    ...requestRows(),
    ackRow('swarms', '2026-11-26T10:30:00Z'),
  ], NOW);
  assert.equal(report.promotions.some(item => item.peer === 'swarms'), false);
  assert.equal(report.blocked.find(item => item.peer === 'swarms')?.state, 'blocked_collision_screen');
  assert.equal(report.diagnostics.find(item => item.peer === 'swarms')?.state, 'blocked_collision_screen');
});

test('mocked Registry write updates qualifying peers once and a rerun is idempotent', async () => {
  const rows = [
    ...requestRows(),
    ackRow('q', '2026-11-26T10:30:00Z'),
    ackRow('sol', '2026-11-26T10:31:00Z'),
    ackRow('swarms', '2026-11-26T10:32:00Z'),
  ];
  const io = makeIo(fixtureRegistry(), rows);
  const first = await runOnce({ ...io, apply: true, nowMs: NOW });
  assert.deepEqual(first.applied, ['q', 'sol']);
  assert.equal(io.writes(), 1, 'all eligible peers share one Registry write');
  const after = io.current();
  for (const name of ['q', 'sol']) {
    const peer = after.peers.find(item => item.name === name);
    assert.equal(peer.status, 'registered');
    assert.ok(after.channels[0].participants.includes(name));
    assert.equal(after.channels[0].pending_participants.some(item => item.startsWith(`${name} `)), false);
  }
  assert.ok(after.peers.find(item => item.name === 'swarms').status.includes('ONBOARDING PENDING'));
  assert.ok(after.channels[0].pending_participants.some(item => item.startsWith('swarms ')));

  const second = await runOnce({ ...io, apply: true, nowMs: NOW });
  assert.equal(second.promotions.length, 0);
  assert.equal(second.applied.length, 0);
  assert.equal(io.writes(), 1, 'already registered peers are not written again');
});

test('applyPromotionPlans is pure with respect to the input Registry', () => {
  const original = fixtureRegistry();
  const report = planPromotions(original, [...requestRows(), ackRow('q', '2026-11-26T10:30:00Z')], NOW);
  const updated = applyPromotionPlans(original, report.promotions);
  assert.equal(original.peers.find(peer => peer.name === 'q').status.includes('ONBOARDING PENDING'), true);
  assert.equal(updated.peers.find(peer => peer.name === 'q').status, 'registered');
});

test('JSONL parser rejects malformed input instead of silently dropping evidence', () => {
  assert.throws(() => parseJsonl('{bad json}\n'), /Malformed FLY-006 JSONL at logical line 1/);
  assert.deepEqual(parseJsonl(''), []);
});

console.log('PASS 1: no qualifying ACK => no Registry write');
console.log('PASS 2: exact sender + FLY-006 Registry assignment + at/after latest request timestamp');
console.log('PASS 3: one shared 11-peer roster pass and no per-peer matrix');
console.log('PASS 4: swarms collision-screen hold blocks an otherwise qualifying ACK');
console.log('PASS 5: mocked Registry write batches eligible peers and is idempotent');
console.log('PASS 6: Registry mutation helper is isolated; malformed JSONL is rejected');
