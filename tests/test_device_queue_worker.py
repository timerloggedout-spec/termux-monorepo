"""P1 device pull-queue Worker contracts; no Cloudflare account or network.

Drives ops/device-queue/worker/src/index.js under node against an in-memory
D1 shim (same adapter interface the production D1Adapter implements), using
the repo's established node-harness pattern from test_quota_dashboard.py.
Covers brief acceptance tests 1 (round-trip), 2 (lease requeue/dead),
3 (dedupe), 4 (expiry), 6 (health counts), 7 (token matrix), plus release
semantics and the write-budget guard.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "ops/device-queue/worker/src/index.js"
SCHEMA = ROOT / "ops/device-queue/worker/schema.sql"
WRANGLER = ROOT / "ops/device-queue/worker/wrangler.toml"
QUEUECTL = ROOT / "ops/device-queue/queuectl.py"

HARNESS = r"""
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

const w = await import(pathToFileURL(process.argv[1]).href);
assert.deepEqual(w.KINDS, ['deepagent-run', 'git-commit-push', 'git-sync',
  'shell-allowlisted', 'heartbeat-only'], 'kind allowlist exported verbatim');

class InMemoryDb {
  constructor() { this.tasks = new Map(); this.events = []; }
  async insertTask(row) {
    if (this.tasks.has(row.id)) { const e = new Error('unique id'); e.code = 'unique_id'; throw e; }
    if (row.dedupe_key != null) {
      for (const t of this.tasks.values()) {
        if (t.dedupe_key === row.dedupe_key) {
          const e = new Error('unique dedupe'); e.code = 'unique_dedupe'; throw e;
        }
      }
    }
    this.tasks.set(row.id, { ...row });
    return { ...row };
  }
  async getTaskById(id) { const t = this.tasks.get(id); return t ? { ...t } : null; }
  async getTaskByDedupe(key) {
    for (const t of this.tasks.values()) if (t.dedupe_key === key) return { ...t };
    return null;
  }
  async listClaimsPastLease(nowIso) {
    return [...this.tasks.values()]
      .filter((t) => t.state === 'claimed' && t.lease_until < nowIso).map((t) => ({ ...t }));
  }
  async listQueuedPastExpiry(nowIso) {
    return [...this.tasks.values()]
      .filter((t) => t.state === 'queued' && t.expires_at <= nowIso).map((t) => ({ ...t }));
  }
  async transition(id, fromStates, patch, event) {
    const t = this.tasks.get(id);
    if (!t || !fromStates.includes(t.state)) return false;
    Object.assign(t, patch);
    if (event) this.events.push({ ...event });
    return true;
  }
  async claimNext({ role, deviceLabel, nowIso, leaseIso }) {
    const cand = [...this.tasks.values()]
      .filter((t) => t.state === 'queued' && t.expires_at > nowIso &&
        (t.role === role || t.role === 'any'))
      .sort((a, b) => (a.created_at < b.created_at ? -1 : a.created_at > b.created_at ? 1 : 0))[0];
    if (!cand) return null;
    cand.state = 'claimed'; cand.claimed_by = deviceLabel;
    cand.claimed_at = nowIso; cand.lease_until = leaseIso; cand.attempts += 1;
    return { ...cand };
  }
  async insertEvent(event) { this.events.push({ ...event }); }
  async countEventsSince(isoTs) { return this.events.filter((e) => e.at >= isoTs).length; }
  async healthCounts() {
    let queued = 0, claimed = 0, dead = 0, oldest = null;
    for (const t of this.tasks.values()) {
      if (t.state === 'queued') { queued++; if (!oldest || t.created_at < oldest) oldest = t.created_at; }
      else if (t.state === 'claimed') claimed++;
      else if (t.state === 'dead') dead++;
    }
    return { queued, claimed, dead, oldestQueuedCreatedAt: oldest };
  }
}

const TOKENS = [
  { value: 'prod-token', label: 'producer:cli', kind: 'producer' },
  { value: 'dev1-token', label: 'device:tmx-node-primary', kind: 'device' },
  { value: 'dev2-token', label: 'device:tmx-node-55619bd5', kind: 'device' },
];
const PROD = 'prod-token', DEV1 = 'dev1-token', DEV2 = 'dev2-token';

function freshApp() {
  const db = new InMemoryDb();
  let nowMs = Date.parse('2026-10-22T00:00:00.000Z');
  const app = w.createApp(db, { tokens: TOKENS, now: () => new Date(nowMs) });
  async function call(method, path, { token, body } = {}) {
    const headers = {};
    if (token) headers.authorization = 'Bearer ' + token;
    let data;
    if (body !== undefined) { headers['content-type'] = 'application/json'; data = JSON.stringify(body); }
    const res = await app(new Request('http://queue' + path, { method, headers, body: data }));
    const text = await res.text();
    let parsed = null;
    try { parsed = JSON.parse(text); } catch { /* 204 etc. */ }
    return { status: res.status, json: parsed, text };
  }
  return { db, call, advance: (ms) => { nowMs += ms; } };
}

const MIN = 60 * 1000;

// --- Test 1: enqueue -> claim -> receipt round-trip -------------------------
{
  const { db, call } = freshApp();
  const enq = await call('POST', '/tasks', { token: PROD,
    body: { kind: 'git-sync', dedupe_key: 'rt-1', payload: { ref: 'master' } } });
  assert.equal(enq.status, 201);
  assert.equal(enq.json.state, 'queued');
  const id = enq.json.id;
  assert.match(id, /^dq-\d{8}-[0-9a-f]{6}$/, 'generated id format');

  const claim = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  assert.equal(claim.status, 200);
  assert.equal(claim.json.task.id, id);
  assert.equal(claim.json.task.state, 'claimed');
  assert.equal(claim.json.task.claimed_by, 'device:tmx-node-primary');
  assert.equal(claim.json.task.attempts, 1);
  assert.deepEqual(JSON.parse(claim.json.task.payload), { ref: 'master' });

  const receipt = await call('POST', `/tasks/${id}/receipt`, { token: DEV1, body: {
    schema_version: 1, task_id: id, device_id: 'tmx-node-primary',
    receipt: { completion_status: 'completed', exit_code: 0 }, storage_free_mb: 4321 } });
  assert.equal(receipt.status, 200);
  assert.equal(receipt.json.state, 'done');

  const shown = await call('GET', `/tasks/${id}`, { token: PROD });
  assert.equal(shown.status, 200);
  assert.equal(shown.json.state, 'done');
  assert.ok(shown.json.receipt.includes('completed'), 'receipt body stored');
  assert.ok(shown.json.finished_at, 'finished_at set');

  const states = db.events.filter((e) => e.task_id === id).map((e) => e.to_state);
  assert.deepEqual(states, ['queued', 'claimed', 'done'], 'one event per transition');

  // A failed receipt lands in 'failed', not 'done'.
  const enq2 = await call('POST', '/tasks', { token: PROD, body: { kind: 'git-sync' } });
  const claim2 = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  const fail = await call('POST', `/tasks/${claim2.json.task.id}/receipt`, { token: DEV1, body: {
    schema_version: 1, task_id: claim2.json.task.id, device_id: 'tmx-node-primary',
    receipt: { completion_status: 'failed', exit_code: 1 }, storage_free_mb: 4000 } });
  assert.equal(fail.json.state, 'failed');
  assert.equal(enq2.status, 201);
}

// --- Test 3: dedupe ----------------------------------------------------------
{
  const { db, call } = freshApp();
  const a = await call('POST', '/tasks', { token: PROD,
    body: { kind: 'git-sync', dedupe_key: 'dup-1' } });
  const b = await call('POST', '/tasks', { token: PROD,
    body: { kind: 'git-sync', dedupe_key: 'dup-1' } });
  assert.equal(a.status, 201);
  assert.equal(b.status, 409);
  assert.equal(b.json.error, 'duplicate');
  assert.equal(b.json.id, a.json.id, '409 returns the original id');
  assert.equal([...db.tasks.values()].filter((t) => t.dedupe_key === 'dup-1').length, 1);

  const c = await call('POST', '/tasks', { token: PROD,
    body: { id: 'dq-fixed-1', kind: 'git-sync' } });
  const d = await call('POST', '/tasks', { token: PROD,
    body: { id: 'dq-fixed-1', kind: 'git-sync' } });
  assert.equal(c.status, 201);
  assert.equal(d.status, 409, 'duplicate explicit id also 409');
}

// --- Test 4: expiry ----------------------------------------------------------
{
  const { db, call, advance } = freshApp();
  const enq = await call('POST', '/tasks', { token: PROD, body: { kind: 'heartbeat-only' } });
  // default TTL is 6h; jump past it
  advance(7 * 60 * MIN);
  const claim = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  assert.equal(claim.status, 204, 'expired task is never claimed');
  const shown = await call('GET', `/tasks/${enq.json.id}`, { token: PROD });
  assert.equal(shown.json.state, 'expired');
  assert.ok(db.events.some((e) => e.task_id === enq.json.id && e.to_state === 'expired'),
    'expiry transition wrote an event');
}

// --- Test 2: lease expiry requeue, then dead at max_attempts -----------------
{
  const { call, advance } = freshApp();
  const enq = await call('POST', '/tasks', { token: PROD,
    body: { kind: 'deepagent-run', id: 'dq-lease-1' } });
  assert.equal(enq.status, 201);
  for (let attempt = 1; attempt <= 3; attempt++) {
    const claim = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
    assert.equal(claim.status, 200, `claim ${attempt} succeeds`);
    assert.equal(claim.json.task.attempts, attempt);
    advance(46 * MIN); // lease (45 min) lapses with no receipt
  }
  const claim4 = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  assert.equal(claim4.status, 204, 'nothing left to claim after death');
  const shown = await call('GET', '/tasks/dq-lease-1', { token: PROD });
  assert.equal(shown.json.state, 'dead');
}

// --- Release: returns the claim without consuming an attempt -----------------
{
  const { call } = freshApp();
  await call('POST', '/tasks', { token: PROD, body: { kind: 'git-sync', id: 'dq-rel-1' } });
  const claim = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  assert.equal(claim.json.task.attempts, 1);
  const rel = await call('POST', '/tasks/dq-rel-1/release', { token: DEV1, body: { note: 'shutdown' } });
  assert.equal(rel.status, 200);
  assert.equal(rel.json.state, 'queued');
  const claim2 = await call('GET', '/tasks/next?role=engineer', { token: DEV2 });
  assert.equal(claim2.status, 200, 'released task claimable by another device');
  assert.equal(claim2.json.task.attempts, 2, 'release itself consumed no attempt');
}

// --- Test 6: health counts after a 20-task burst -----------------------------
{
  const { call } = freshApp();
  for (let i = 0; i < 20; i++) {
    const r = await call('POST', '/tasks', { token: PROD,
      body: { kind: 'heartbeat-only', dedupe_key: `burst-${i}` } });
    assert.equal(r.status, 201);
  }
  for (let i = 0; i < 3; i++) {
    const c = await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
    assert.equal(c.status, 200);
  }
  const health = await call('GET', '/health'); // public: no token
  assert.equal(health.status, 200);
  assert.equal(health.json.ok, true);
  assert.equal(health.json.queued, 17);
  assert.equal(health.json.claimed, 3);
  assert.equal(health.json.dead, 0);
  assert.equal(typeof health.json.oldest_queued_age_s, 'number');
  assert.ok(!('task' in health.json) && !health.text.includes('burst-'), 'health leaks no task data');
}

// --- Test 7: token matrix + validation ---------------------------------------
{
  const { call } = freshApp();
  assert.equal((await call('POST', '/tasks', { body: { kind: 'git-sync' } })).status, 401, 'no token');
  assert.equal((await call('POST', '/tasks', { token: 'nope',
    body: { kind: 'git-sync' } })).status, 401, 'bad token');
  assert.equal((await call('POST', '/tasks', { token: DEV1,
    body: { kind: 'git-sync' } })).status, 403, 'device token cannot enqueue');
  assert.equal((await call('GET', '/tasks/next?role=engineer', { token: PROD })).status, 403,
    'producer token cannot claim');
  assert.equal((await call('POST', '/tasks', { token: PROD,
    body: { kind: 'rm-rf' } })).status, 400, 'kind outside allowlist');
  assert.equal((await call('POST', '/tasks', { token: PROD,
    body: { kind: 'git-sync', payload: 'x'.repeat(5000) } })).status, 400, 'oversize payload');

  await call('POST', '/tasks', { token: PROD, body: { kind: 'git-sync', id: 'dq-tok-1' } });
  await call('GET', '/tasks/next?role=engineer', { token: DEV1 });
  const wrongReceipt = await call('POST', '/tasks/dq-tok-1/receipt', { token: DEV2, body: {
    schema_version: 1, task_id: 'dq-tok-1', device_id: 'tmx-node-55619bd5',
    receipt: { completion_status: 'completed' }, storage_free_mb: 1 } });
  assert.equal(wrongReceipt.status, 403, 'receipt from non-claimant device');
  const wrongRelease = await call('POST', '/tasks/dq-tok-1/release', { token: DEV2, body: {} });
  assert.equal(wrongRelease.status, 403, 'release from non-claimant device');
  const wrongShow = await call('GET', '/tasks/dq-tok-1', { token: DEV2 });
  assert.equal(wrongShow.status, 403, 'device cannot read a task it did not claim');
  const missing = await call('GET', '/tasks/dq-absent', { token: PROD });
  assert.equal(missing.status, 404, 'unknown task id');
}

// --- Write-budget guard --------------------------------------------------------
{
  const { db, call } = freshApp();
  const dayStart = '2026-10-22T00:00:00.000Z';
  for (let i = 0; i < 80001; i++) {
    db.events.push({ task_id: 'flood', at: dayStart, actor: 'producer:cli',
      from_state: null, to_state: 'queued', note: 'seed' });
  }
  const r = await call('POST', '/tasks', { token: PROD, body: { kind: 'git-sync' } });
  assert.equal(r.status, 503);
  assert.equal(r.json.error, 'write_budget');
}

console.log('WORKER-HARNESS-OK');
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required for Worker harness")
def test_worker_scenarios_via_node():
    result = subprocess.run(
        ["node", "--input-type=module", "-e", HARNESS, str(WORKER)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"node harness failed:\n{result.stdout}\n{result.stderr}"
    assert "WORKER-HARNESS-OK" in result.stdout


def test_schema_and_wrangler_static_contract():
    schema = SCHEMA.read_text()
    for needle in ("CREATE TABLE tasks", "CREATE TABLE events",
                   "idx_tasks_claim", "idx_events_task", "dedupe_key"):
        assert needle in schema, f"schema.sql missing {needle}"
    wrangler = WRANGLER.read_text()
    assert 'name = "tmx-device-queue"' in wrangler
    assert "workers_dev = true" in wrangler
    assert 'binding = "DB"' in wrangler
    assert 'database_id = "REPLACE_AT_DEPLOY"' in wrangler


def test_no_secret_values_in_worker_files():
    worker_src = WORKER.read_text()
    # Secret *names* are expected; anything resembling a committed value is not.
    for name in ("DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS", "DEVICE_QUEUE_PRODUCER_TOKEN_CLI",
                 "DEVICE_QUEUE_DEVICE_TOKEN_PRIMARY", "DEVICE_QUEUE_DEVICE_TOKEN_SECONDARY"):
        assert name in worker_src, f"worker does not reference secret name {name}"
    for path in (WORKER, WRANGLER, QUEUECTL):
        text = path.read_text()
        assert "Bearer " not in text or "Bearer {token}" in text or "Bearer'" in text, path
        lowered = text.lower()
        for marker in ("api_key =", "api-key:", "password =", "private_key"):
            assert marker not in lowered, f"{path} contains suspicious marker {marker!r}"


def test_queuectl_help_and_token_never_printed(tmp_path):
    help_run = subprocess.run(
        [sys.executable, str(QUEUECTL), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert help_run.returncode == 0
    assert "enqueue" in help_run.stdout and "health" in help_run.stdout

    canary = "canary-token-value-must-not-appear"
    env = {
        **os.environ,
        "DEVICE_QUEUE_URL": "http://127.0.0.1:9",  # nothing listens there
        "DEVICE_QUEUE_TOKEN": canary,
    }
    run = subprocess.run(
        [sys.executable, str(QUEUECTL), "show", "dq-nonexistent"],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert run.returncode != 0, "unreachable queue must fail nonzero"
    assert canary not in run.stdout + run.stderr, "token leaked into CLI output"


def test_queuectl_missing_url_is_a_clean_error():
    env = {k: v for k, v in os.environ.items() if k != "DEVICE_QUEUE_URL"}
    run = subprocess.run(
        [sys.executable, str(QUEUECTL), "health"],
        capture_output=True, text=True, timeout=30, env=env,
    )
    assert run.returncode == 2
    assert "DEVICE_QUEUE_URL" in run.stderr
