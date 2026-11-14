'use strict';
/**
 * Planning Queue - Intake Service
 * Gateway route: POST /api/task -> POST /
 * Validates a task and publishes it to Pub/Sub. Never touches the database.
 * Adapted from shoal-platform/message-queue-demo order-service.
 */
const express = require('express');
const { PubSub } = require('@google-cloud/pubsub');
const { randomUUID } = require('node:crypto');

const SERVICE = 'planning-intake';
function requireEnv(n) { const v = process.env[n]; if (!v) { console.error(`[${SERVICE}] missing required env: ${n}`); process.exit(1); } return v; }

const PORT = Number(process.env.PORT || 8080);
const TOPIC_ID = requireEnv('TASKS_TOPIC_ID');
const INTAKE_TOKEN = process.env.INTAKE_TOKEN || ''; // optional shared bearer for writers
const KIND_RE = /^[a-z][a-z0-9_.-]{0,63}$/;
const REPO_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

function buildTask(body) {
  const p = body && typeof body === 'object' ? body : {};
  const source = String(p.source ?? '').trim();
  const kind = String(p.kind ?? '').trim();
  const repo = p.repo == null || p.repo === '' ? null : String(p.repo).trim();
  const payload = p.payload == null ? {} : p.payload;
  if (!source || source.length > 64) return { error: 'source is required (<=64 chars)' };
  if (!KIND_RE.test(kind)) return { error: 'kind is required: lowercase, [a-z0-9_.-], <=64 chars' };
  if (repo && !REPO_RE.test(repo)) return { error: 'repo must look like owner/name' };
  if (typeof payload !== 'object' || Array.isArray(payload)) return { error: 'payload must be a JSON object' };
  const id = typeof p.id === 'string' && /^[A-Za-z0-9_.:-]{1,128}$/.test(p.id) ? p.id : randomUUID();
  return { task: { id, source, repo, kind, payload, status: 'queued', createdAt: new Date().toISOString() } };
}

const pubsub = new PubSub({ projectId: process.env.GCP_PROJECT_ID });
const topic = pubsub.topic(TOPIC_ID);
const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '256kb' }));

app.get('/health', (_q, r) => r.json({ ok: true, service: SERVICE, sha: process.env.GIT_SHA || null }));

app.post('/', async (req, res) => {
  if (INTAKE_TOKEN && req.get('authorization') !== `Bearer ${INTAKE_TOKEN}`) return res.status(401).json({ error: 'unauthorized' });
  const { task, error } = buildTask(req.body);
  if (error) return res.status(400).json({ error });
  try {
    await topic.publishMessage({ json: task, attributes: { kind: task.kind, source: task.source } });
    res.status(202).json({ message: 'Task queued', task });
  } catch (e) {
    console.error(`[${SERVICE}] publish failed ${task.id}:`, e);
    res.status(503).json({ error: 'Task could not be queued; retry.' });
  }
});

app.use((_q, r) => r.status(404).json({ error: 'Not found' }));
// eslint-disable-next-line no-unused-vars
app.use((err, _q, res, next) => {
  if (err.type === 'entity.parse.failed') return res.status(400).json({ error: 'Body must be valid JSON' });
  if (err.type === 'entity.too.large') return res.status(413).json({ error: 'Body too large' });
  console.error(`[${SERVICE}] error:`, err); res.status(500).json({ error: 'Internal server error' });
});

const server = app.listen(PORT, () => console.log(`[${SERVICE}] listening on ${PORT}`));
for (const s of ['SIGTERM', 'SIGINT']) process.on(s, () => {
  setTimeout(() => process.exit(1), 10_000).unref();
  server.close(async () => { try { await pubsub.close(); } catch {} process.exit(0); });
});
module.exports = { buildTask };
