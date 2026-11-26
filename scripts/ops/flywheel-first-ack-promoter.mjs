import { appendFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

export const TARGET_REPO = 'timerloggedout-spec/termux-monorepo';
export const REGISTRY_PATH = 'docs/ops/flywheel-comms/REGISTRY.json';
export const REGISTRY_REF = 'master';
export const STORE_REPO = 'timerloggedout-spec/muse-vm-workspace-backup';
export const STORE_REF = 'main';
export const CHANNEL_ID = 'FLY-006';
export const OVERDUE_AFTER_MS = 24 * 60 * 60 * 1000;

function fail(message) {
  throw new Error(message);
}

function identity(value) {
  return typeof value === 'string'
    ? value.normalize('NFKC').trim().replace(/^@/, '').toLocaleLowerCase('en-US')
    : '';
}

function aliasesFor(peer) {
  return [...new Set([peer?.name, ...(Array.isArray(peer?.aliases) ? peer.aliases : [])]
    .map(identity).filter(Boolean))];
}

function pendingStatus(peer) {
  return typeof peer?.status === 'string' && /onboarding\s+pending/i.test(peer.status);
}

function pendingName(entry) {
  if (typeof entry !== 'string') return '';
  const match = entry.trim().match(/^(.+?)\s*\(/);
  return (match ? match[1] : entry).trim();
}

export function parseJsonl(text) {
  if (typeof text !== 'string') fail('FLY-006 content was not text');
  const rows = [];
  const lines = text.split(/\r?\n/).filter(line => line.trim());
  for (let index = 0; index < lines.length; index++) {
    let row;
    try {
      row = JSON.parse(lines[index]);
    } catch {
      fail(`Malformed FLY-006 JSONL at logical line ${index + 1}`);
    }
    if (!row || typeof row !== 'object' || Array.isArray(row)) {
      fail(`Invalid FLY-006 row at logical line ${index + 1}`);
    }
    rows.push(row);
  }
  return rows;
}

function timestamp(value) {
  if (typeof value !== 'string') return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function explicitAckBody(value) {
  if (typeof value !== 'string') return false;
  let text = value.trim();
  const arrow = text.search(/(?:→|->)/u);
  if (arrow >= 0 && arrow < 180) text = text.slice(arrow + (text[arrow] === '→' ? 1 : 2)).trim();
  text = text.replace(/^[^A-Za-z0-9]+/, '');
  const ackLead = /^(?:ack(?:nowledged|nowledgement|nowledgment)?|received|noted|confirmed|roger|copy|got\s+it)\b/i.exec(text);
  if (ackLead) {
    const remainder = text.slice(ackLead[0].length).replace(/^[\s:,.!—-]+/, '');
    if (/^(?:(?:is|was|remains)\s+)?(?:still\s+)?(?:pending|owed|awaiting|requested|needed|not\b|unconfirmed\b)/i.test(remainder)) return false;
    return true;
  }
  return /^(?:i|we)\s+(?:acknowledge(?:d)?|confirm(?:ed)?|received)\b/i.test(text);
}

function firstAckRequest(rows, peerAliases) {
  let latest = null;
  for (const row of rows) {
    if (typeof row.from !== 'string' || typeof row.to !== 'string' || typeof row.body !== 'string') continue;
    if (peerAliases.includes(identity(row.from)) || !peerAliases.includes(identity(row.to))) continue;
    if (!/\bfirst[\s-]*ack(?:nowledg(?:e|ement|ment))?\b/i.test(row.body)) continue;
    const ms = timestamp(row.ts);
    if (ms === null) continue;
    if (!latest || ms > latest.ms) latest = { ms, ts: row.ts };
  }
  return latest;
}

function firstAck(rows, peerAliases, request) {
  for (const row of rows) {
    if (typeof row.from !== 'string' || !peerAliases.includes(identity(row.from)) || !explicitAckBody(row.body)) continue;
    const ms = timestamp(row.ts);
    if (request && (ms === null || ms < request.ms)) continue;
    return {
      from: row.from,
      to: typeof row.to === 'string' ? row.to : '',
      ts: typeof row.ts === 'string' ? row.ts : '',
    };
  }
  return null;
}

function expectedChannel(registry) {
  if (!registry || !Array.isArray(registry.channels)) fail('Registry has no channels array');
  const matches = registry.channels.filter(channel => channel && channel.id === CHANNEL_ID);
  if (matches.length !== 1) fail('Registry must contain exactly one FLY-006 channel');
  const channel = matches[0];
  if (!['established', 'active'].includes(String(channel.status || '').trim().toLowerCase())) {
    fail('FLY-006 is not an active, established channel');
  }
  if (channel.store_repo !== STORE_REPO) fail('FLY-006 store_repo does not match the approved private store');
  const path = typeof channel.path === 'string'
    ? channel.path.match(/^([A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*\.jsonl)\b/i)?.[1]
    : null;
  if (path !== 'cue/work-comms.jsonl') fail('FLY-006 path is not the expected JSONL stream');
  if (!Array.isArray(channel.pending_participants)) fail('FLY-006 has no pending_participants array');
  if (!Array.isArray(registry.peers)) fail('Registry has no peers array');
  return channel;
}

export function planPromotions(registry, rows, nowMs = Date.now()) {
  if (!Array.isArray(rows)) fail('FLY-006 rows must be an array');
  const channel = expectedChannel(registry);
  const peers = registry.peers;
  const pendingPeers = peers.filter(peer => peer && pendingStatus(peer) &&
    Array.isArray(peer.channels) && peer.channels.includes(CHANNEL_ID));
  const diagnostics = [];
  const promotions = [];
  const blocked = [];

  // One shared roster pass: no per-peer job, workflow, or matrix is created.
  for (const peer of pendingPeers) {
    const aliases = aliasesFor(peer);
    const request = firstAckRequest(rows, aliases);
    const ack = firstAck(rows, aliases, request);
    const ageMs = request ? Math.max(0, nowMs - request.ms) : null;
    if (!ack) {
      diagnostics.push({
        peer: peer.name,
        channel: CHANNEL_ID,
        state: request && ageMs >= OVERDUE_AFTER_MS ? 'overdue' : 'missing',
        request_ts: request?.ts ?? null,
      });
      continue;
    }

    const nameMatches = peers.filter(candidate => candidate && identity(candidate.name) === identity(peer.name) &&
      Array.isArray(candidate.channels) && candidate.channels.includes(CHANNEL_ID) && pendingStatus(candidate));
    if (nameMatches.length !== 1) {
      const item = { peer: peer.name, channel: CHANNEL_ID, state: 'blocked_registry_identity', reason: 'Exactly one pending Registry peer record is required.' };
      blocked.push(item);
      diagnostics.push(item);
      continue;
    }

    const note = typeof peer.note === 'string' ? peer.note : '';
    const collisionHold = /COLLISION FLAG/i.test(note) && /screen before any promotion/i.test(note);
    if (collisionHold) {
      const item = { peer: peer.name, channel: CHANNEL_ID, state: 'blocked_collision_screen', reason: 'Registry note requires the owner collision screen before promotion.', ack };
      blocked.push(item);
      diagnostics.push(item);
      continue;
    }

    const peerAliases = aliasesFor(peer);
    const pendingEntries = channel.pending_participants.filter(entry =>
      peerAliases.includes(identity(pendingName(entry))));
    const alreadyParticipant = (Array.isArray(channel.participants) ? channel.participants : [])
      .some(name => peerAliases.includes(identity(name)));
    const promotion = {
      peer: peer.name,
      channel: CHANNEL_ID,
      from_status: peer.status,
      to_status: 'registered',
      ack,
      request_ts: request?.ts ?? null,
      add_participant_if_absent: alreadyParticipant ? null : peer.name,
      remove_pending_participants: pendingEntries,
    };
    promotions.push(promotion);
    diagnostics.push({ peer: peer.name, channel: CHANNEL_ID, state: 'acknowledged', request_ts: request?.ts ?? null, ack });
  }

  const channelPendingNames = new Set(channel.pending_participants.map(entry => identity(pendingName(entry))).filter(Boolean));
  const peerPendingNames = new Set(pendingPeers.flatMap(peer => aliasesFor(peer)));
  const unrepresentedPending = [...channelPendingNames].filter(name => !peerPendingNames.has(name));
  for (const name of unrepresentedPending) {
    diagnostics.push({ peer: name, channel: CHANNEL_ID, state: 'blocked_registry_identity', reason: 'Pending channel identity has no matching onboarding-pending peer record.' });
  }

  return {
    channel: CHANNEL_ID,
    roster_size: pendingPeers.length,
    pending_count: pendingPeers.length,
    promotions,
    blocked,
    diagnostics,
  };
}

export function applyPromotionPlans(registry, promotions) {
  const updated = structuredClone(registry);
  const channel = expectedChannel(updated);
  const peers = updated.peers;
  for (const promotion of promotions) {
    if (promotion.channel !== CHANNEL_ID || promotion.to_status !== 'registered') fail('Refusing an invalid promotion plan');
    const matches = peers.filter(peer => peer && identity(peer.name) === identity(promotion.peer) &&
      pendingStatus(peer) && Array.isArray(peer.channels) && peer.channels.includes(CHANNEL_ID));
    if (matches.length !== 1) fail(`Registry changed or has an ambiguous peer identity for ${promotion.peer}`);
    const peer = matches[0];
    const note = typeof peer.note === 'string' ? peer.note : '';
    if (/COLLISION FLAG/i.test(note) && /screen before any promotion/i.test(note)) {
      fail(`Collision-screen hold appeared for ${promotion.peer}; refusing promotion`);
    }
    peer.status = 'registered';
    const aliases = aliasesFor(peer);
    if (!Array.isArray(channel.participants)) channel.participants = [];
    if (!channel.participants.some(name => aliases.includes(identity(name)))) channel.participants.push(peer.name);
    channel.pending_participants = channel.pending_participants.filter(entry =>
      !aliases.includes(identity(pendingName(entry))));
  }
  return updated;
}

export async function runOnce({ readRegistry, readFlywheel, writeRegistry, apply = false, nowMs = Date.now() }) {
  if (typeof readRegistry !== 'function' || typeof readFlywheel !== 'function') fail('Registry and FLY-006 readers are required');
  const readSnapshot = async () => {
    const [registryDoc, rows] = await Promise.all([readRegistry(), readFlywheel()]);
    if (!registryDoc || !registryDoc.registry || typeof registryDoc.sha !== 'string') fail('Registry reader must return registry and blob SHA');
    return { registryDoc, rows, report: planPromotions(registryDoc.registry, rows, nowMs) };
  };

  let current = await readSnapshot();
  if (!apply || current.report.promotions.length === 0) return { ...current.report, applied: [], dry_run: !apply, registry_sha: current.registryDoc.sha };
  if (typeof writeRegistry !== 'function') fail('A Registry writer is required when apply=true');

  // Re-read both sources immediately before writing to avoid acting on stale evidence.
  current = await readSnapshot();
  if (current.report.promotions.length === 0) return { ...current.report, applied: [], dry_run: false, registry_sha: current.registryDoc.sha };
  const updatedRegistry = applyPromotionPlans(current.registryDoc.registry, current.report.promotions);
  await writeRegistry({ registry: updatedRegistry, sha: current.registryDoc.sha, promotions: current.report.promotions });
  return { ...current.report, applied: current.report.promotions.map(item => item.peer), dry_run: false, registry_sha: current.registryDoc.sha };
}

function encodePath(path) {
  return path.split('/').map(segment => encodeURIComponent(segment)).join('/');
}

async function githubRequest(url, token, options = {}) {
  if (!token) fail('Required GitHub token is unavailable');
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${token}`,
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'flywheel-first-ack-promoter',
      ...(options.headers || {}),
    },
  });
  if (!response.ok) fail(`GitHub API request failed with HTTP ${response.status}`);
  return response;
}

async function getFile(repo, path, ref, token) {
  const base = process.env.GITHUB_API_URL || 'https://api.github.com';
  const url = `${base}/repos/${repo}/contents/${encodePath(path)}?ref=${encodeURIComponent(ref)}`;
  const response = await githubRequest(url, token);
  const data = await response.json();
  if (data.type !== 'file' || typeof data.content !== 'string' || typeof data.sha !== 'string') {
    fail(`GitHub API returned an invalid file object for ${repo}:${path}`);
  }
  return { sha: data.sha, text: Buffer.from(data.content.replace(/\s/g, ''), 'base64').toString('utf8') };
}

async function main() {
  const apply = process.env.APPLY_PROMOTIONS === 'true';
  const repository = process.env.GITHUB_REPOSITORY || TARGET_REPO;
  if (repository !== TARGET_REPO) fail(`Refusing to run against unexpected repository ${repository}`);
  if (apply && process.env.GITHUB_REF !== 'refs/heads/master') fail('Refusing Registry writes outside refs/heads/master');

  const registryToken = process.env.GITHUB_TOKEN;
  const privateReadToken = process.env.OPERATOR_GITHUB_TOKEN;
  const readRegistry = async () => {
    const doc = await getFile(TARGET_REPO, REGISTRY_PATH, REGISTRY_REF, registryToken);
    let registry;
    try {
      registry = JSON.parse(doc.text);
    } catch {
      fail('Registry JSON is malformed');
    }
    return { registry, sha: doc.sha };
  };
  const readFlywheel = async () => {
    const doc = await getFile(STORE_REPO, 'cue/work-comms.jsonl', STORE_REF, privateReadToken);
    return parseJsonl(doc.text);
  };
  const writeRegistry = async ({ registry, sha, promotions }) => {
    const base = process.env.GITHUB_API_URL || 'https://api.github.com';
    const url = `${base}/repos/${TARGET_REPO}/contents/${encodePath(REGISTRY_PATH)}`;
    const content = Buffer.from(`${JSON.stringify(registry, null, 2)}\n`, 'utf8').toString('base64');
    await githubRequest(url, registryToken, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `chore(flywheel): register FLY-006 first ACK${promotions.length > 1 ? 's' : ''} [skip render]`,
        content,
        sha,
        branch: REGISTRY_REF,
      }),
    });
  };

  const result = await runOnce({ readRegistry, readFlywheel, writeRegistry, apply });
  const reportCell = value => String(value ?? '—').replace(/[\r\n]/g, ' ').replace(/::/g, ': :').replace(/\|/g, '\\|');
  const summary = [
    '## FLY-006 first-ACK shared promoter',
    `Mode: ${result.dry_run ? 'dry run (no Registry write)' : 'apply-enabled'}`,
    `Pending peers checked in one roster pass: ${result.pending_count}`,
    `Qualifying promotions: ${result.promotions.length}`,
    `Registry updates applied: ${result.applied.length}`,
    '',
    '| Peer | State | Request (UTC) | ACK (UTC) |',
    '|---|---|---|---|',
    ...result.diagnostics.map(item => `| ${reportCell(item.peer)} | ${reportCell(item.state)} | ${reportCell(item.request_ts)} | ${reportCell(item.ack?.ts)} |`),
    '',
    result.blocked.length ? `Blocked promotions: ${result.blocked.map(item => `${reportCell(item.peer)} (${reportCell(item.state)})`).join(', ')}` : 'No collision or identity holds encountered among ACK candidates.',
  ].join('\n');
  console.log(summary);
  if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY, `${summary}\n`);
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) {
  main().catch(error => {
    console.error(`flywheel-first-ack-promoter: ${error.message}`);
    process.exitCode = 1;
  });
}
