'use strict';
/**
 * planning-queue stale-sweeper
 * Called by the platform201 scheduler node (e.g. every 10 minutes, POST /sweep).
 * Claims older than STALE_AFTER_MINUTES (default 30) become 'stale'; with REQUEUE_STALE=true
 * they go back to 'queued' instead so another worker can pick them up.
 * Also runnable once from the CLI: `node server.js --once`.
 */
const express = require('express');
const { Pool } = require('pg');

const SERVICE_NAME = 'stale-sweeper';

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    console.error(`[${SERVICE_NAME}] missing required environment variable: ${name}`);
    process.exit(1);
  }
  return value;
}

const PORT = Number(process.env.PORT || 8080);
const DATABASE_URL = requireEnv('DATABASE_URL');
const STALE_AFTER_MINUTES = Math.max(Number(process.env.STALE_AFTER_MINUTES) || 30, 1);
const REQUEUE = String(process.env.REQUEUE_STALE || '').toLowerCase() === 'true';

const pool = new Pool({ connectionString: DATABASE_URL, max: 2, connectionTimeoutMillis: 5_000 });
pool.on('error', e => console.error(`[${SERVICE_NAME}] idle client error:`, e));

async function sweep() {
  const r = REQUEUE
    ? await pool.query(
        `UPDATE ops_queue SET status = 'queued', claimed_by = NULL, claimed_at = NULL
         WHERE status = 'claimed' AND claimed_at < now() - make_interval(mins => $1) RETURNING id`, [STALE_AFTER_MINUTES])
    : await pool.query(
        `UPDATE ops_queue SET status = 'stale'
         WHERE status = 'claimed' AND claimed_at < now() - make_interval(mins => $1) RETURNING id`, [STALE_AFTER_MINUTES]);
  const result = { swept: r.rowCount, action: REQUEUE ? 'requeued' : 'marked_stale', olderThanMinutes: STALE_AFTER_MINUTES, at: new Date().toISOString() };
  console.log(`[${SERVICE_NAME}]`, JSON.stringify(result));
  return result;
}

if (process.argv.includes('--once')) {
  sweep().then(() => pool.end()).catch(e => { console.error(e); process.exit(1); });
} else {
  const app = express();
  app.disable('x-powered-by');
  app.get('/health', (_req, res) => res.json({ ok: true, service: SERVICE_NAME }));
  const handler = async (_req, res) => {
    try { res.json(await sweep()); } catch (e) { console.error(e); res.status(500).json({ error: 'sweep failed' }); }
  };
  app.post('/sweep', handler);
  app.get('/sweep', handler);
  app.post('/', handler);
  const server = app.listen(PORT, () => console.log(`[${SERVICE_NAME}] listening on ${PORT}`));
  for (const s of ['SIGTERM', 'SIGINT']) process.on(s, () => { server.close(() => pool.end().then(() => process.exit(0))); setTimeout(() => process.exit(1), 10_000).unref(); });
}
