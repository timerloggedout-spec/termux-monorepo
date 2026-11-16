// Receiver Mesh — Cloudflare Worker leg (prototype)
// Design of record: docs/ops/RECEIVER-MESH.md
// Job: verify (HMAC primary, dynamic Meta-IP secondary), dedupe (D1),
// normalize to an allowlisted envelope, hand off via repository_dispatch.
// No business logic, no durable state beyond D1 dedupe/dead-letter.
//
// Bindings (wrangler.toml): D1 `RECEIVER_D1`
// Secrets: RECEIVER_GH_WEBHOOK_SECRET, RECEIVER_DISPATCH_TOKEN
// Vars: RECEIVER_REPO (owner/name), META_CACHE_SECONDS (default 3600)

const ENVELOPE_FIELDS = ["source", "event", "delivery_id", "received_at", "repo", "action", "actor", "object_id"];

async function hmacHex(secret, body) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function ipv4ToInt(ip) {
  return ip.split(".").reduce((acc, part) => (acc << 8) + Number(part), 0) >>> 0;
}

function ipInCidr(ip, cidr) {
  const [range, bitsStr] = cidr.split("/");
  const bits = Number(bitsStr);
  if (ip.includes(":") || range.includes(":")) return false; // IPv6 handled by signature-only path
  const mask = bits === 0 ? 0 : (0xffffffff << (32 - bits)) >>> 0;
  return (ipv4ToInt(ip) & mask) === (ipv4ToInt(range) & mask);
}

async function githubHookRanges(env) {
  const cache = caches.default;
  const cacheKey = new Request("https://receiver-mesh.internal/meta-hooks");
  const hit = await cache.match(cacheKey);
  if (hit) return hit.json();
  const res = await fetch("https://api.github.com/meta", { headers: { "User-Agent": "receiver-mesh" } });
  if (!res.ok) return null; // fail-open: signature-only
  const meta = await res.json();
  const ranges = meta.hooks || [];
  const ttl = Number(env.META_CACHE_SECONDS || 3600);
  const resp = new Response(JSON.stringify(ranges), { headers: { "Cache-Control": `max-age=${ttl}` } });
  await cache.put(cacheKey, resp.clone());
  return ranges;
}

function normalize(event, deliveryId, payload) {
  const env = {
    source: "github",
    event,
    delivery_id: deliveryId,
    received_at: new Date().toISOString(),
    repo: payload?.repository?.full_name || null,
    action: payload?.action || null,
    actor: payload?.sender?.login || null,
    object_id: String(payload?.issue?.number ?? payload?.pull_request?.number ?? payload?.release?.id ?? "") || null,
  };
  return Object.fromEntries(Object.entries(env).filter(([k]) => ENVELOPE_FIELDS.includes(k)));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") return Response.json({ ok: true, leg: "cloudflare" });
    if (request.method !== "POST" || url.pathname !== "/github") return new Response("not found", { status: 404 });

    const raw = await request.text();
    const signature = request.headers.get("x-hub-signature-256") || "";
    const expected = "sha256=" + (await hmacHex(env.RECEIVER_GH_WEBHOOK_SECRET, raw));
    if (!timingSafeEqual(signature, expected)) return new Response("bad signature", { status: 401 });

    // Secondary check only: dynamic ranges from the Meta API, never hardcoded.
    const ranges = await githubHookRanges(env);
    const sourceIp = request.headers.get("cf-connecting-ip") || "";
    if (ranges && sourceIp && !ranges.some((r) => ipInCidr(sourceIp, r))) {
      return new Response("source ip not in meta hooks ranges", { status: 403 });
    }

    const deliveryId = request.headers.get("x-github-delivery");
    const event = request.headers.get("x-github-event") || "unknown";
    if (!deliveryId) return new Response("missing delivery id", { status: 400 });

    const seen = await env.RECEIVER_D1.prepare("SELECT delivery_id FROM dedupe WHERE delivery_id = ?").bind(deliveryId).first();
    if (seen) return Response.json({ ok: true, deduped: true });

    let payload;
    try { payload = JSON.parse(raw); } catch { return new Response("bad json", { status: 400 }); }
    const envelope = normalize(event, deliveryId, payload);

    const dispatch = await fetch(`https://api.github.com/repos/${env.RECEIVER_REPO}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RECEIVER_DISPATCH_TOKEN}`,
        Accept: "application/vnd.github+json",
        "User-Agent": "receiver-mesh",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ event_type: "receiver-event", client_payload: { envelope } }),
    });

    if (!dispatch.ok) {
      // Failsafe: dead-letter in D1; the reconcile sweep replays from here.
      await env.RECEIVER_D1.prepare("INSERT OR IGNORE INTO dead_letter (delivery_id, event, envelope, failed_at, status) VALUES (?, ?, ?, ?, ?)")
        .bind(deliveryId, event, JSON.stringify(envelope), envelope.received_at, dispatch.status).run();
      return Response.json({ ok: false, dead_lettered: true }, { status: 202 });
    }

    await env.RECEIVER_D1.prepare("INSERT OR IGNORE INTO dedupe (delivery_id, event, received_at) VALUES (?, ?, ?)")
      .bind(deliveryId, event, envelope.received_at).run();
    return Response.json({ ok: true, envelope });
  },
};
