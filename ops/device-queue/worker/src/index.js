// tmx-device-queue — Cloudflare Worker rendezvous for the P1 device pull-queue.
//
// Design: docs/ops/P1-PULL-QUEUE-SPEC.md + docs/ops/DEVICE-PULL-QUEUE.md.
// The Worker stays thin: bearer-token auth, validation, and a small set of SQL
// statements against D1. Producers enqueue; devices poll, claim atomically,
// and post receipts. No secret values live in this file — the four tokens
// arrive as Worker secrets (env bindings) named:
//   DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS   -> label producer:actions
//   DEVICE_QUEUE_PRODUCER_TOKEN_CLI       -> label producer:cli
//   DEVICE_QUEUE_DEVICE_TOKEN_PRIMARY     -> label device:tmx-node-primary
//   DEVICE_QUEUE_DEVICE_TOKEN_SECONDARY   -> label device:tmx-node-55619bd5
//
// All data access goes through a tiny adapter interface so the claim / lease /
// reaper logic can be unit-tested against an in-memory shim (see
// tests/test_device_queue_worker.py). Adapter methods (all async):
//   insertTask(row)                       -> row; throws err.code 'unique_id' | 'unique_dedupe'
//   getTaskById(id)                       -> row | null
//   getTaskByDedupe(key)                  -> row | null
//   listClaimsPastLease(nowIso)           -> [row]  (state='claimed', lease_until < now)
//   listQueuedPastExpiry(nowIso)          -> [row]  (state='queued', expires_at <= now)
//   transition(id, fromStates, patch, ev) -> bool   (conditional update + event row)
//   claimNext({role, deviceLabel, nowIso, leaseIso}) -> row | null  (atomic claim)
//   insertEvent(event)                    -> void
//   countEventsSince(isoTs)               -> int
//   healthCounts()                        -> {queued, claimed, dead, oldestQueuedCreatedAt}

export const KINDS = [
  'deepagent-run',
  'git-commit-push',
  'git-sync',
  'shell-allowlisted',
  'heartbeat-only',
];

const PAYLOAD_MAX_BYTES = 4096;
const LEASE_MS = 45 * 60 * 1000; // 3 device poll cycles
const DEFAULT_TTL_MS = 6 * 60 * 60 * 1000;
const WRITE_BUDGET_EVENTS_PER_DAY = 80000; // safety-0.8 of the 100k D1 free cap

const TOKEN_SPECS = [
  ['DEVICE_QUEUE_PRODUCER_TOKEN_ACTIONS', 'producer:actions', 'producer'],
  ['DEVICE_QUEUE_PRODUCER_TOKEN_CLI', 'producer:cli', 'producer'],
  ['DEVICE_QUEUE_DEVICE_TOKEN_PRIMARY', 'device:tmx-node-primary', 'device'],
  ['DEVICE_QUEUE_DEVICE_TOKEN_SECONDARY', 'device:tmx-node-55619bd5', 'device'],
];

export function tokensFromEnv(env) {
  const out = [];
  for (const [name, label, kind] of TOKEN_SPECS) {
    const value = env ? env[name] : undefined;
    if (typeof value === 'string' && value.length > 0) out.push({ value, label, kind });
  }
  return out;
}

// Constant-time comparison: length check, then an XOR sweep with no early exit.
export function constantTimeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function authenticate(request, tokens) {
  const header = request.headers.get('authorization') || '';
  const match = /^Bearer\s+(.+)$/i.exec(header.trim());
  if (!match) return null;
  const presented = match[1];
  let actor = null;
  for (const t of tokens) {
    if (constantTimeEqual(presented, t.value)) actor = { label: t.label, kind: t.kind };
  }
  return actor;
}

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

function genId(now) {
  const day = now.toISOString().slice(0, 10).replace(/-/g, '');
  const bytes = new Uint8Array(3);
  crypto.getRandomValues(bytes);
  const hex = [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
  return `dq-${day}-${hex}`;
}

function dayStartIso(now) {
  const d = new Date(now.getTime());
  d.setUTCHours(0, 0, 0, 0);
  return d.toISOString();
}

async function readJsonBody(request) {
  const text = await request.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return undefined; // sentinel: unparseable
  }
}

// Reaper: expired queued tasks die of old age; claims past their lease are
// re-queued, or marked dead once attempts are exhausted. One event per
// transition. Runs at the top of every claim request (no cron needed).
async function reap(db, actorLabel, nowIso) {
  for (const row of await db.listQueuedPastExpiry(nowIso)) {
    await db.transition(row.id, ['queued'], { state: 'expired', finished_at: nowIso }, {
      task_id: row.id, at: nowIso, actor: actorLabel,
      from_state: 'queued', to_state: 'expired', note: 'ttl_expired',
    });
  }
  for (const row of await db.listClaimsPastLease(nowIso)) {
    if (row.attempts >= row.max_attempts) {
      await db.transition(row.id, ['claimed'], { state: 'dead', finished_at: nowIso }, {
        task_id: row.id, at: nowIso, actor: actorLabel,
        from_state: 'claimed', to_state: 'dead', note: 'lease_expired_max_attempts',
      });
    } else {
      await db.transition(row.id, ['claimed'],
        { state: 'queued', claimed_by: null, claimed_at: null, lease_until: null }, {
          task_id: row.id, at: nowIso, actor: actorLabel,
          from_state: 'claimed', to_state: 'queued', note: 'lease_expired_requeue',
        });
    }
  }
}

export function createApp(db, opts) {
  const tokens = (opts && opts.tokens) || [];
  const nowFn = (opts && opts.now) || (() => new Date());

  async function handleEnqueue(request, actor) {
    const body = await readJsonBody(request);
    if (body === undefined || body === null || typeof body !== 'object') {
      return json(400, { error: 'bad_json' });
    }
    if (!KINDS.includes(body.kind)) return json(400, { error: 'bad_kind' });

    let payloadStr = '{}';
    if (body.payload !== undefined) {
      payloadStr = typeof body.payload === 'string' ? body.payload : JSON.stringify(body.payload);
      if (new TextEncoder().encode(payloadStr).length > PAYLOAD_MAX_BYTES) {
        return json(400, { error: 'payload_too_large' });
      }
    }

    const now = nowFn();
    const nowIso = now.toISOString();
    let expiresIso;
    if (body.expires_at !== undefined) {
      const parsed = Date.parse(body.expires_at);
      if (Number.isNaN(parsed)) return json(400, { error: 'bad_expiry' });
      expiresIso = new Date(parsed).toISOString();
    } else {
      expiresIso = new Date(now.getTime() + DEFAULT_TTL_MS).toISOString();
    }

    const dedupeKey = body.dedupe_key !== undefined ? String(body.dedupe_key) : null;
    if (dedupeKey !== null) {
      const existing = await db.getTaskByDedupe(dedupeKey);
      if (existing) return json(409, { error: 'duplicate', id: existing.id });
    }

    // Write-budget guard: refuse new enqueues rather than die mid-claim.
    const eventsToday = await db.countEventsSince(dayStartIso(now));
    if (eventsToday > WRITE_BUDGET_EVENTS_PER_DAY) {
      return json(503, { error: 'write_budget' });
    }

    const row = {
      id: body.id !== undefined ? String(body.id) : genId(now),
      dedupe_key: dedupeKey,
      kind: body.kind,
      role: body.role !== undefined ? String(body.role) : 'engineer',
      payload: payloadStr,
      state: 'queued',
      producer: actor.label,
      created_at: nowIso,
      expires_at: expiresIso,
      claimed_by: null,
      claimed_at: null,
      lease_until: null,
      attempts: 0,
      max_attempts: Number.isInteger(body.max_attempts) && body.max_attempts > 0 ? body.max_attempts : 3,
      receipt: null,
      finished_at: null,
    };
    try {
      await db.insertTask(row);
    } catch (err) {
      if (err && err.code === 'unique_dedupe') {
        const existing = await db.getTaskByDedupe(dedupeKey);
        return json(409, { error: 'duplicate', id: existing ? existing.id : row.id });
      }
      if (err && err.code === 'unique_id') {
        return json(409, { error: 'duplicate', id: row.id });
      }
      throw err;
    }
    await db.insertEvent({
      task_id: row.id, at: nowIso, actor: actor.label,
      from_state: null, to_state: 'queued', note: 'enqueue',
    });
    return json(201, { id: row.id, state: 'queued' });
  }

  async function handleNext(request, actor) {
    const url = new URL(request.url);
    const role = url.searchParams.get('role') || 'engineer';
    const now = nowFn();
    const nowIso = now.toISOString();
    await reap(db, actor.label, nowIso);
    const leaseIso = new Date(now.getTime() + LEASE_MS).toISOString();
    const row = await db.claimNext({ role, deviceLabel: actor.label, nowIso, leaseIso });
    if (!row) return new Response(null, { status: 204 });
    await db.insertEvent({
      task_id: row.id, at: nowIso, actor: actor.label,
      from_state: 'queued', to_state: 'claimed', note: null,
    });
    return json(200, { task: row });
  }

  async function loadClaimedTask(id, actor) {
    const row = await db.getTaskById(id);
    if (!row) return { error: json(404, { error: 'not_found' }) };
    if (row.claimed_by !== actor.label) return { error: json(403, { error: 'not_claimant' }) };
    if (row.state !== 'claimed') return { error: json(409, { error: 'not_claimed' }) };
    return { row };
  }

  async function handleReceipt(request, actor, id) {
    const body = await readJsonBody(request);
    if (body === undefined || body === null || typeof body !== 'object') {
      return json(400, { error: 'bad_json' });
    }
    const { row, error } = await loadClaimedTask(id, actor);
    if (error) return error;
    const deviceId = actor.label.slice('device:'.length);
    if (body.device_id !== deviceId) return json(403, { error: 'not_claimant' });
    if (body.task_id !== undefined && body.task_id !== id) {
      return json(400, { error: 'task_mismatch' });
    }
    if (typeof body.receipt !== 'object' || body.receipt === null ||
        typeof body.storage_free_mb !== 'number') {
      return json(400, { error: 'bad_receipt' });
    }
    const nowIso = nowFn().toISOString();
    const status = body.receipt.completion_status;
    const newState = status === 'completed' ? 'done' : 'failed';
    const applied = await db.transition(id, ['claimed'], {
      state: newState, receipt: JSON.stringify(body), finished_at: nowIso,
    }, {
      task_id: id, at: nowIso, actor: actor.label,
      from_state: 'claimed', to_state: newState, note: body.note || 'receipt',
    });
    if (!applied) return json(409, { error: 'not_claimed' });
    return json(200, { id, state: newState });
  }

  async function handleRelease(request, actor, id) {
    const body = await readJsonBody(request); // optional; may be empty
    const { row, error } = await loadClaimedTask(id, actor);
    if (error) return error;
    const nowIso = nowFn().toISOString();
    const applied = await db.transition(id, ['claimed'], {
      state: 'queued', claimed_by: null, claimed_at: null, lease_until: null,
    }, {
      task_id: id, at: nowIso, actor: actor.label,
      from_state: 'claimed', to_state: 'queued',
      note: (body && body.note) || 'release',
    });
    if (!applied) return json(409, { error: 'not_claimed' });
    return json(200, { id, state: 'queued' });
  }

  async function handleShow(actor, id) {
    const row = await db.getTaskById(id);
    if (!row) return json(404, { error: 'not_found' });
    if (actor.kind === 'device' && row.claimed_by !== actor.label) {
      return json(403, { error: 'forbidden' });
    }
    return json(200, row);
  }

  async function handleHealth() {
    const now = nowFn();
    const counts = await db.healthCounts();
    const oldestAge = counts.oldestQueuedCreatedAt
      ? Math.max(0, Math.floor((now.getTime() - Date.parse(counts.oldestQueuedCreatedAt)) / 1000))
      : null;
    return json(200, {
      ok: true,
      queued: counts.queued,
      claimed: counts.claimed,
      dead: counts.dead,
      oldest_queued_age_s: oldestAge,
      at: now.toISOString(),
    });
  }

  return async function handle(request) {
    try {
      const url = new URL(request.url);
      const parts = url.pathname.split('/').filter((p) => p.length > 0);
      const method = request.method.toUpperCase();

      if (parts.length === 1 && parts[0] === 'health' && method === 'GET') {
        return await handleHealth();
      }

      const actor = authenticate(request, tokens);
      if (!actor) return json(401, { error: 'unauthorized' });

      if (parts.length === 1 && parts[0] === 'tasks' && method === 'POST') {
        if (actor.kind !== 'producer') return json(403, { error: 'forbidden' });
        return await handleEnqueue(request, actor);
      }
      if (parts.length === 2 && parts[0] === 'tasks' && parts[1] === 'next' && method === 'GET') {
        if (actor.kind !== 'device') return json(403, { error: 'forbidden' });
        return await handleNext(request, actor);
      }
      if (parts.length === 3 && parts[0] === 'tasks' && parts[2] === 'receipt' && method === 'POST') {
        if (actor.kind !== 'device') return json(403, { error: 'forbidden' });
        return await handleReceipt(request, actor, parts[1]);
      }
      if (parts.length === 3 && parts[0] === 'tasks' && parts[2] === 'release' && method === 'POST') {
        if (actor.kind !== 'device') return json(403, { error: 'forbidden' });
        return await handleRelease(request, actor, parts[1]);
      }
      if (parts.length === 2 && parts[0] === 'tasks' && method === 'GET') {
        return await handleShow(actor, parts[1]);
      }
      return json(404, { error: 'not_found' });
    } catch (err) {
      console.error('device-queue error', err);
      return json(500, { error: 'internal' });
    }
  };
}

// --- D1 adapter (production) ------------------------------------------------

const TASK_COLUMNS = [
  'id', 'dedupe_key', 'kind', 'role', 'payload', 'state', 'producer',
  'created_at', 'expires_at', 'claimed_by', 'claimed_at', 'lease_until',
  'attempts', 'max_attempts', 'receipt', 'finished_at',
];

export class D1Adapter {
  constructor(d1) {
    this.d1 = d1;
  }

  async insertTask(row) {
    const placeholders = TASK_COLUMNS.map(() => '?').join(', ');
    try {
      await this.d1
        .prepare(`INSERT INTO tasks (${TASK_COLUMNS.join(', ')}) VALUES (${placeholders})`)
        .bind(...TASK_COLUMNS.map((c) => row[c]))
        .run();
    } catch (err) {
      const msg = String((err && err.message) || err);
      if (msg.includes('UNIQUE') && msg.includes('dedupe_key')) {
        const e = new Error('duplicate dedupe_key'); e.code = 'unique_dedupe'; throw e;
      }
      if (msg.includes('UNIQUE')) {
        const e = new Error('duplicate id'); e.code = 'unique_id'; throw e;
      }
      throw err;
    }
    return row;
  }

  async getTaskById(id) {
    return await this.d1.prepare('SELECT * FROM tasks WHERE id = ?').bind(id).first();
  }

  async getTaskByDedupe(key) {
    return await this.d1.prepare('SELECT * FROM tasks WHERE dedupe_key = ?').bind(key).first();
  }

  async listClaimsPastLease(nowIso) {
    const { results } = await this.d1
      .prepare("SELECT * FROM tasks WHERE state = 'claimed' AND lease_until < ?")
      .bind(nowIso)
      .all();
    return results || [];
  }

  async listQueuedPastExpiry(nowIso) {
    const { results } = await this.d1
      .prepare("SELECT * FROM tasks WHERE state = 'queued' AND expires_at <= ?")
      .bind(nowIso)
      .all();
    return results || [];
  }

  async transition(id, fromStates, patch, event) {
    const cols = Object.keys(patch);
    const setClause = cols.map((c) => `${c} = ?`).join(', ');
    const statePlaceholders = fromStates.map(() => '?').join(', ');
    const res = await this.d1
      .prepare(`UPDATE tasks SET ${setClause} WHERE id = ? AND state IN (${statePlaceholders})`)
      .bind(...cols.map((c) => patch[c]), id, ...fromStates)
      .run();
    const changed = res && res.meta && typeof res.meta.changes === 'number' ? res.meta.changes : 0;
    if (changed !== 1) return false;
    if (event) await this.insertEvent(event);
    return true;
  }

  // Atomic claim: one UPDATE ... WHERE id = (SELECT oldest claimable) followed
  // by a SELECT of the claimed row by (claimed_by, claimed_at, lease_until).
  // The brief's UPDATE ... RETURNING shape is equivalent on current D1; the
  // UPDATE+SELECT form is used so the identical logic runs against the
  // in-memory test shim and older SQLite runtimes.
  async claimNext({ role, deviceLabel, nowIso, leaseIso }) {
    const res = await this.d1
      .prepare(
        `UPDATE tasks
           SET state = 'claimed', claimed_by = ?, claimed_at = ?, lease_until = ?,
               attempts = attempts + 1
         WHERE id = (SELECT id FROM tasks
                      WHERE state = 'queued' AND expires_at > ?
                        AND (role = ? OR role = 'any')
                      ORDER BY created_at LIMIT 1)`)
      .bind(deviceLabel, nowIso, leaseIso, nowIso, role)
      .run();
    const changed = res && res.meta && typeof res.meta.changes === 'number' ? res.meta.changes : 0;
    if (changed !== 1) return null;
    return await this.d1
      .prepare("SELECT * FROM tasks WHERE claimed_by = ? AND claimed_at = ? AND lease_until = ? AND state = 'claimed'")
      .bind(deviceLabel, nowIso, leaseIso)
      .first();
  }

  async insertEvent(event) {
    await this.d1
      .prepare('INSERT INTO events (task_id, at, actor, from_state, to_state, note) VALUES (?, ?, ?, ?, ?, ?)')
      .bind(event.task_id, event.at, event.actor, event.from_state, event.to_state, event.note)
      .run();
  }

  async countEventsSince(isoTs) {
    const row = await this.d1
      .prepare('SELECT COUNT(*) AS n FROM events WHERE at >= ?')
      .bind(isoTs)
      .first();
    return row ? row.n : 0;
  }

  async healthCounts() {
    const row = await this.d1
      .prepare(
        `SELECT
           SUM(CASE WHEN state = 'queued' THEN 1 ELSE 0 END) AS queued,
           SUM(CASE WHEN state = 'claimed' THEN 1 ELSE 0 END) AS claimed,
           SUM(CASE WHEN state = 'dead' THEN 1 ELSE 0 END) AS dead,
           MIN(CASE WHEN state = 'queued' THEN created_at END) AS oldest
         FROM tasks`)
      .first();
    return {
      queued: (row && row.queued) || 0,
      claimed: (row && row.claimed) || 0,
      dead: (row && row.dead) || 0,
      oldestQueuedCreatedAt: row ? row.oldest : null,
    };
  }
}

export default {
  async fetch(request, env) {
    const app = createApp(new D1Adapter(env.DB), {
      tokens: tokensFromEnv(env),
      now: () => new Date(),
    });
    return app(request);
  },
};
