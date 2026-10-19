'use strict';
/**
 * planning-queue queue-collector
 * - Subscribes to the tasks subscription; INSERT ... ON CONFLICT (id) DO NOTHING into ops_queue.
 * - GET  /                 recent tasks (?status=queued&limit=100)       gateway: GET /api/queue
 * - POST /claim            {worker, kinds?} -> claims oldest queued task  gateway: POST /api/queue/claim
 * - POST /complete         {id, worker, ok?} -> done|failed               gateway: POST /api/queue/complete
 * Optional QUEUE_TOKEN guards /claim and /complete (Bearer).
 */
const fs = require('node:fs');
const path = require('node:path');
const express = require('express');
const { PubSub } = require('@google-cloud/pubsub');
const { Pool } = require('pg');
const { timingSafeEqual } = require('node:crypto');

const SERVICE_NAME = 'queue-collector';

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    console.error(`[${SERVICE_NAME}] missing required environment variable: ${name}`);
    process.exit(1);
  }
  return value;
}

const PORT = Number(process.env.PORT || 8080);
const PROJECT_ID = process.env.GCP_PROJECT_ID;
const DATABASE_URL = requireEnv('DATABASE_URL');
const TASKS_SUBSCRIPTION_ID = requireEnv('TASKS_SUBSCRIPTION_ID');
const QUEUE_TOKEN = process.env.QUEUE_TOKEN || '';
const STATUSES = new Set(['queued', 'claimed', 'done', 'failed', 'stale']);

const pool = new Pool({ connectionString: DATABASE_URL, max: 10, idleTimeoutMillis: 30_000, connectionTimeoutMillis: 5_000 });
pool.on('error', e => console.error(`[${SERVICE_NAME}] idle client error:`, e));

const SCHEMA = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');

async function saveTask(t) {
  await pool.query(
    `INSERT INTO ops_queue (id, source, repo, kind, payload, status, created_at)
     VALUES ($1, $2, $3, $4, $5::jsonb, 'queued', $6)
     ON CONFLICT (id) DO NOTHING`,
    [t.id, t.source, t.repo ?? null, t.kind, JSON.stringify(t.payload ?? {}), t.createdAt ?? new Date().toISOString()]
  );
}

function authorized(req) {
  if (!QUEUE_TOKEN) return true;
  const got = Buffer.from(String(req.get('authorization') || ''));
  const want = Buffer.from(`Bearer ${QUEUE_TOKEN}`);
  return got.length === want.length && timingSafeEqual(got, want);
}

const pubsub = new PubSub({ projectId: PROJECT_ID });
const subscription = pubsub.subscription(TASKS_SUBSCRIPTION_ID);

function startSubscriber() {
  subscription.on('message', async m => {
    let t = null;
    try { t = JSON.parse(m.data.toString('utf8')); } catch {}
    if (!t || typeof t.id !== 'string' || !t.id || typeof t.kind !== 'string' || typeof t.source !== 'string') {
      console.warn(`[${SERVICE_NAME}] discarding unreadable message ${m.id}`);
      return m.ack();
    }
    try { await saveTask(t); m.ack(); }
    catch (e) { console.error(`[${SERVICE_NAME}] persist failed ${t.id}:`, e); m.nack(); }
  });
  subscription.on('error', e => console.error(`[${SERVICE_NAME}] subscription error:`, e));
  console.log(`[${SERVICE_NAME}] subscribed to ${TASKS_SUBSCRIPTION_ID}`);
}

const COLS = `id, source, repo, kind, payload, status, created_at AS "createdAt",
              claimed_by AS "claimedBy", claimed_at AS "claimedAt", done_at AS "doneAt"`;

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '100kb' }));

app.get('/health', async (_req, res) => {
  try { await pool.query('SELECT 1'); res.json({ ok: true, service: SERVICE_NAME }); }
  catch { res.status(503).json({ ok: false, service: SERVICE_NAME }); }
});

app.get('/', async (req, res) => {
  const limit = Math.min(Math.max(Number(req.query.limit) || 100, 1), 500);
  const status = req.query.status ? String(req.query.status) : null;
  if (status && !STATUSES.has(status)) return res.status(400).json({ error: 'unknown status' });
  try {
    const r = status
      ? await pool.query(`SELECT ${COLS} FROM ops_queue WHERE status = $1 ORDER BY created_at DESC LIMIT $2`, [status, limit])
      : await pool.query(`SELECT ${COLS} FROM ops_queue ORDER BY created_at DESC LIMIT $1`, [limit]);
    const counts = await pool.query(`SELECT status, count(*)::int AS n FROM ops_queue GROUP BY status`);
    res.json({ tasks: r.rows, counts: Object.fromEntries(counts.rows.map(x => [x.status, x.n])) });
  } catch (e) {
    console.error(`[${SERVICE_NAME}] list failed:`, e);
    res.status(500).json({ error: 'Queue could not be loaded' });
  }
});

app.post('/claim', async (req, res) => {
  if (!authorized(req)) return res.status(401).json({ error: 'Unauthorized' });
  const worker = String(req.body?.worker ?? '').trim();
  const kinds = Array.isArray(req.body?.kinds) ? req.body.kinds.map(String) : null;
  if (!worker || worker.length > 120) return res.status(400).json({ error: 'worker is required' });
  try {
    const r = await pool.query(
      `UPDATE ops_queue SET status = 'claimed', claimed_by = $1, claimed_at = now()
       WHERE id = (SELECT id FROM ops_queue WHERE status = 'queued'
                   AND ($2::text[] IS NULL OR kind = ANY($2))
                   ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1)
       RETURNING ${COLS}`, [worker, kinds]);
    res.json({ task: r.rows[0] ?? null });
  } catch (e) { console.error(`[${SERVICE_NAME}] claim failed:`, e); res.status(500).json({ error: 'claim failed' }); }
});

app.post('/complete', async (req, res) => {
  if (!authorized(req)) return res.status(401).json({ error: 'Unauthorized' });
  const id = String(req.body?.id ?? '');
  const worker = String(req.body?.worker ?? '');
  const ok = req.body?.ok !== false;
  try {
    const r = await pool.query(
      `UPDATE ops_queue SET status = $3, done_at = now()
       WHERE id = $1 AND claimed_by = $2 AND status = 'claimed' RETURNING ${COLS}`,
      [id, worker, ok ? 'done' : 'failed']);
    if (!r.rows[0]) return res.status(409).json({ error: 'not claimed by this worker' });
    res.json({ task: r.rows[0] });
  } catch (e) { console.error(`[${SERVICE_NAME}] complete failed:`, e); res.status(500).json({ error: 'complete failed' }); }
});

app.use((_req, res) => res.status(404).json({ error: 'Not found' }));
// eslint-disable-next-line no-unused-vars
app.use((error, _req, res, next) => { console.error(error); res.status(500).json({ error: 'Internal server error' }); });

async function main() {
  await pool.query(SCHEMA);
  startSubscriber();
  const server = app.listen(PORT, () => console.log(`[${SERVICE_NAME}] listening on ${PORT}`));
  for (const s of ['SIGTERM', 'SIGINT']) process.on(s, async () => {
    setTimeout(() => process.exit(1), 10_000).unref();
    await Promise.allSettled([new Promise(r => server.close(r)), subscription.close(), pool.end()]);
    process.exit(0);
  });
}
main().catch(e => { console.error(`[${SERVICE_NAME}] start-up failed:`, e); process.exit(1); });
