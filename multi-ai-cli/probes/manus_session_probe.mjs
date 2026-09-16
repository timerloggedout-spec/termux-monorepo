#!/usr/bin/env node
/**
 * archw1z — Manus session RECON probe (Node ESM)
 * Fetches getSessionV2 + files + cascade for a share/app URL or sessionId.
 * Prints event-type histogram + first/last timestamps. Does not write ML JSONL
 * (use multi-ai-cli/harvesters/manus_computer_replay.py for the pipeline export).
 *
 *   node manus_session_probe.mjs --url 'https://manus.im/share/ID?replay=1'
 *   node manus_session_probe.mjs --session ID --type shared
 */
import { writeFileSync, mkdirSync } from 'node:fs';

const BASE = 'https://api.manus.im';
const headers = {
  accept: 'application/json',
  'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
  referer: 'https://manus.im/',
  origin: 'https://manus.im',
  'x-client-type': 'web',
  'x-client-locale': 'en',
  'x-client-timezone': 'UTC',
  'x-client-timezone-offset': '0',
};

function parseArgs(argv) {
  const o = { type: 'shared', outDir: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--session') o.session = argv[++i];
    else if (a === '--url') o.url = argv[++i];
    else if (a === '--type') o.type = argv[++i];
    else if (a === '--out-dir') o.outDir = argv[++i];
  }
  return o;
}

function sessionIdFrom(raw) {
  if (!raw) return null;
  if (!raw.startsWith('http')) return raw.trim();
  const m = raw.match(/\/(?:share|app)\/([A-Za-z0-9_-]+)/);
  if (!m) throw new Error('cannot parse sessionId from URL');
  return m[1];
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`, { headers });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json();
}

const args = parseArgs(process.argv);
const sessionId = sessionIdFrom(args.session || args.url);
if (!sessionId) {
  console.error('need --session or --url');
  process.exit(1);
}

const type = args.type;
console.error(`[probe] session=${sessionId} type=${type}`);

const session = await get(
  `/api/chat/getSessionV2?sessionId=${sessionId}&type=${type}&getFirstSegment=true`,
);
const files = await get(`/api/chat/getSessionFilesV2?sessionId=${sessionId}&type=${type}`);
let cascade = {};
try {
  cascade = await get(
    `/api/chat/listCascadeJobs?sessionId=${sessionId}&type=${type}&includeActive=true`,
  );
} catch (e) {
  console.error('[probe] cascade:', e.message);
}

const data = session.data || session;
const events = [];
for (const seg of data.segments || []) {
  for (const ev of seg.events || []) events.push(ev);
}
events.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));

const hist = {};
for (const e of events) hist[e.type] = (hist[e.type] || 0) + 1;

console.log(
  JSON.stringify(
    {
      session_id: sessionId,
      title: data.title,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      event_count: events.length,
      types: hist,
      first: events[0]
        ? { type: events[0].type, timestamp: events[0].timestamp, id: events[0].id }
        : null,
      last: events.length
        ? {
            type: events[events.length - 1].type,
            timestamp: events[events.length - 1].timestamp,
            id: events[events.length - 1].id,
          }
        : null,
    },
    null,
    2,
  ),
);

if (args.outDir) {
  mkdirSync(args.outDir, { recursive: true });
  const base = `${args.outDir}/${sessionId}`;
  writeFileSync(`${base}_session.json`, JSON.stringify(session, null, 2));
  writeFileSync(`${base}_files.json`, JSON.stringify(files, null, 2));
  writeFileSync(`${base}_cascade.json`, JSON.stringify(cascade, null, 2));
  console.error(`[probe] raw dumps → ${base}_*.json`);
}
