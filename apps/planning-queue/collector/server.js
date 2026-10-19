'use strict';
/**
 * Planning Queue - Collector
 * Subscribes to planning-tasks, INSERT ... ON CONFLICT (id) DO NOTHING into ops_queue (Neon).
 * Gateway routes:
 *   GET  /api/queue            -> GET /           (?status=queued&repo=o/r&kind=x&limit=100)
 *   POST /api/queue/claim      -> POST /claim     {worker, kind?, repo?}  atomically claims oldest queued
 *   POST /api/queue/:id/done   -> POST /:id/done  {worker, ok?: true, result?: {}}
 * Adapted from shoal-platform/message-queue-demo order-collector.
 */
const fs = require('node:fs');
const path = require('node:path');
const express = require('express');
const { PubSub } = require('@google-cloud/pubsub');
const { Pool } = require('pg');

const SERVICE = 'planning-collector';
function requireEnv(n) { const v = process.env[n]; if (!v) { console.error(`[${SERVICE}] missing required env: ${n}`); process.exit(1); } return v; }

const PORT = Number(process.env.PORT || 8080);
const DATABASE_URL = requireEnv('DATABASE_URL');
const SUBSCRIPTION_ID = requireEnv('TASKS_SUBSCRIPTION_ID');
const WORKER_TOKEN = process.env.WORKER_TOKEN || ''; // optional bearer for claim/done

const pool = new Pool({ connectionString: DATABASE_URL, max: 10, idleTimeoutMillis: 30_000, connectionTimeoutMillis: 5_000 });
pool.on('error', e => console.error(`[${SERVICE}] idle client error:`, e));

async function initDb() {
  const local = path.join(__dirname, 'schema.sql');
  const sql = fs.existsSync(local) ? fs.readFileSync(local, 'utf8') : fs.readFileSync(path.join(__dirname, '..', 'sql', '001_ops_queue.sql'), 'utf8');
  await pool.query(sql);
}

async function saveTask(t) {
  await pool.query(
    `INSERT INTO ops_queue (id, source, repo, kind, payload, status, created_at)
     VALUES ($1,$2,$3,$4,$5::jsonb,'queued',$6) ON CONFLICT (id) DO NOTHING`,
    [t.id, t.source, t.repo || null, t.kind, JSON.stringify(t.payload || {}), t.createdAt || new Date().toISOString()]
  );
}

const COLS = `id, source, repo, kind, payload, status, created_at AS "createdAt", claimed_by AS "claimedBy", claimed_at AS "claimedAt", done_at AS "doneAt"`;

const pubsub = new PubSub({ projectId: process.env.GCP_PROJECT_ID });
const subscription = pubsub.subscription(SUBSCRIPTION_ID);

function parse(msg) {
  try { const t = JSON.parse(msg.data.toString('utf8')); return t && typeof t.id === 'string' && t.id && typeof t.kind === 'string' && typeof t.source === 'string' ? t : null; }
  catch { return null; }
}
function startSubscriber() {
  subscription.on('message', async msg => {
    const t = parse(msg);
    if (!t) { console.warn(`[${SERVICE}] discarding unreadable message ${msg.id}`); msg.ack(); return; }
    try { await saveTask(t); msg.ack(); } catch (e) { console.error(`[${SERVICE}] persist failed ${t.id}:`, e); msg.nack(); }
  });
  subscription.on('error', e => console.error(`[${SERVICE}] subscription error:`, e));
  console.log(`[${SERVICE}] subscribed to ${SUBSCRIPTION_ID}`);
}

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '256kb' }));
const auth = (req, res, next) => (!WORKER_TOKEN || req.get('authorization') === `Bearer ${WORKER_TOKEN}`) ? next() : res.status(401).json({ error: 'unauthorized' });

app.get('/health', async (_q, res) => {
  try { await pool.query('SELECT 1'); res.json({ ok: true, service: SERVICE, sha: process.env.GIT_SHA || null }); }
  catch { res.status(503).json({ ok: false, service: SERVICE }); }
});

app.get('/', async (req, res) => {
  const where = []; const args = [];
  for (const k of ['status', 'repo', 'kind', 'source']) if (req.query[k]) { args.push(String(req.query[k])); where.push(`${k} = $${args.length}`); }
  const limit = Math.min(Math.max(Number(req.query.limit) || 100, 1), 500); args.push(limit);
  try {
    const r = await pool.query(`SELECT ${COLS} FROM ops_queue ${where.length ? 'WHERE ' + where.join(' AND ') : ''} ORDER BY created_at DESC LIMIT $${args.length}`, args);
    res.json({ tasks: r.rows });
  } catch (e) { console.error(`[${SERVICE}] list failed:`, e); res.status(500).json({ error: 'Queue could not be loaded' }); }
});

app.post('/claim', auth, async (req, res) => {
  const worker = String(req.body?.worker || '').trim();
  if (!worker || worker.length > 64) return res.status(400).json({ error: 'worker is required (<=64 chars)' });
  const args = [worker]; const f = [];
  if (req.body?.kind) { args.push(String(req.body.kind)); f.push(`kind = $${args.length}`); }
  if (req.body?.repo) { args.push(String(req.body.repo)); f.push(`repo = $${args.length}`); }
  try {
    const r = await pool.query(
      `UPDATE ops_queue SET status='claimed', claimed_by=$1, claimed_at=now()
       WHERE id = (SELECT id FROM ops_queue WHERE status='queued' ${f.length ? 'AND ' + f.join(' AND ') : ''}
                   ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1)
       RETURNING ${COLS}`, args);
    if (!r.rowCount) return res.status(204).end();
    res.json({ task: r.rows[0] });
  } catch (e) { console.error(`[${SERVICE}] claim failed:`, e); res.status(500).json({ error: 'claim failed' }); }
});

app.post('/:id/done', auth, async (req, res) => {
  const ok = req.body?.ok !== false;
  try {
    const r = await pool.query(
      `UPDATE ops_queue SET status=$2, done_at=now(),
              payload = CASE WHEN $3::jsonb IS NULL THEN payload ELSE payload || jsonb_build_object('result', $3::jsonb) END
       WHERE id=$1 AND status IN ('claimed','stale') AND ($4::text IS NULL OR claimed_by=$4) RETURNING ${COLS}`,
      [req.params.id, ok ? 'done' : 'failed', req.body?.result ? JSON.stringify(req.body.result) : null, req.body?.worker || null]);
    if (!r.rowCount) return res.status(409).json({ error: 'task not claimed (or claimed by another worker)' });
    res.json({ task: r.rows[0] });
  } catch (e) { console.error(`[${SERVICE}] done failed:`, e); res.status(500).json({ error: 'done failed' }); }
});

app.use((_q, r) => r.status(404).json({ error: 'Not found' }));
// eslint-disable-next-line no-unused-vars
app.use((err, _q, res, next) => { console.error(`[${SERVICE}] error:`, err); res.status(500).json({ error: 'Internal server error' }); });

async function main() {
  await initDb();
  startSubscriber();
  const server = app.listen(PORT, () => console.log(`[${SERVICE}] listening on ${PORT}`));
  for (const s of ['SIGTERM', 'SIGINT']) process.on(s, async () => {
    setTimeout(() => process.exit(1), 10_000).unref();
    await Promise.allSettled([new Promise(r => server.close(r)), subscription.close(), pool.end()]);
    process.exit(0);
  });
}
main().catch(e => { console.error(`[${SERVICE}] start-up failed:`, e); process.exit(1); });
