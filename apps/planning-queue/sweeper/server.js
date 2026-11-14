'use strict';
/**
 * Planning Queue - Stale-claim sweeper
 * The scheduler node calls POST / (e.g. every 5 minutes). Claims older than
 * STALE_AFTER_MINUTES are marked 'stale'; with REQUEUE_STALE=true they go back to 'queued'.
 * Also runnable as a one-shot job: `node server.js --once`.
 */
const express = require('express');
const { Pool } = require('pg');
const SERVICE = 'planning-sweeper';
function requireEnv(n) { const v = process.env[n]; if (!v) { console.error(`[${SERVICE}] missing required env: ${n}`); process.exit(1); } return v; }

const pool = new Pool({ connectionString: requireEnv('DATABASE_URL'), max: 2 });
pool.on('error', e => console.error(`[${SERVICE}] idle client error:`, e));
const STALE_MIN = Math.max(Number(process.env.STALE_AFTER_MINUTES || 30), 1);
const REQUEUE = process.env.REQUEUE_STALE === 'true';
const SWEEP_TOKEN = process.env.SWEEP_TOKEN || '';

async function sweep() {
  const r = REQUEUE
    ? await pool.query(`UPDATE ops_queue SET status='queued', claimed_by=NULL, claimed_at=NULL
                        WHERE status='claimed' AND claimed_at < now() - make_interval(mins => $1) RETURNING id`, [STALE_MIN])
    : await pool.query(`UPDATE ops_queue SET status='stale'
                        WHERE status='claimed' AND claimed_at < now() - make_interval(mins => $1) RETURNING id`, [STALE_MIN]);
  return { swept: r.rowCount, action: REQUEUE ? 'requeued' : 'marked_stale', staleAfterMinutes: STALE_MIN, at: new Date().toISOString() };
}

if (process.argv.includes('--once')) {
  sweep().then(r => { console.log(JSON.stringify(r)); return pool.end(); }).catch(e => { console.error(e); process.exit(1); });
} else {
  const app = express();
  app.disable('x-powered-by');
  app.get('/health', (_q, r) => r.json({ ok: true, service: SERVICE }));
  app.post('/', async (req, res) => {
    if (SWEEP_TOKEN && req.get('authorization') !== `Bearer ${SWEEP_TOKEN}`) return res.status(401).json({ error: 'unauthorized' });
    try { const r = await sweep(); console.log(`[${SERVICE}]`, JSON.stringify(r)); res.json(r); }
    catch (e) { console.error(`[${SERVICE}] sweep failed:`, e); res.status(500).json({ error: 'sweep failed' }); }
  });
  const server = app.listen(Number(process.env.PORT || 8080), () => console.log(`[${SERVICE}] listening`));
  for (const s of ['SIGTERM', 'SIGINT']) process.on(s, () => { setTimeout(() => process.exit(1), 10_000).unref(); server.close(async () => { await pool.end().catch(() => {}); process.exit(0); }); });
}
