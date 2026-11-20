const REPO = "timerloggedout-spec/termux-monorepo";
const ORIGIN = "https://timerloggedout-spec.github.io";
const cors = {
  "Access-Control-Allow-Origin": ORIGIN,
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Max-Age": "86400"
};

async function gh(path, token) {
  const response = await fetch("https://api.github.com" + path, {
    headers: {"Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Authorization": "Bearer " + token, "User-Agent": "admin-graph-live"}
  });
  if (!response.ok) throw new Error("GitHub verification failed: " + response.status);
  return response.json();
}
function bounded(value, max) {
  if (typeof value !== "string") return null;
  const result = value.trim();
  return result && result.length <= max ? result : null;
}
function safeRoutePayload(value) {
  const source = value || {};
  return {
    task_ref: bounded(source.task_ref, 32),
    issue_number: Number.isInteger(source.issue_number) ? source.issue_number : null,
    source_comment_id: Number.isInteger(source.source_comment_id) ? source.source_comment_id : null,
    source: bounded(source.source, 40),
    route_role: bounded(source.route_role, 120),
    provider: bounded(source.provider, 120),
    arm_id: bounded(source.arm_id, 120),
    model: bounded(source.model, 160),
    dispatch_id: bounded(source.dispatch_id, 160)
  };
}
function validEvent(event) {
  if (!event || event.repo !== REPO || !event.id || String(event.id).length > 220) return false;
  if (!Number.isSafeInteger(Number(event.run_id)) || Number(event.run_id) <= 0) return false;
  if (!Number.isSafeInteger(Number(event.run_attempt)) || Number(event.run_attempt) <= 0) return false;
  if (!bounded(event.event, 64) || !bounded(event.status, 32) || !bounded(event.workflow, 200)) return false;
  if (!event.occurred_at || !Number.isFinite(Date.parse(event.occurred_at))) return false;
  if (!["workflow", "job", "route"].includes(event.kind)) return false;
  if (event.kind === "route") {
    const route = safeRoutePayload(event.payload);
    return event.event === "task_routed" && event.status === "routed" &&
      route.issue_number > 0 && route.source_comment_id > 0 && !!route.route_role &&
      ["producer_claim", "dispatch_executor_claim"].includes(route.source);
  }
  if (event.kind === "job") return String(event.event).startsWith("job_") && !!event.job_id;
  return String(event.event).startsWith("workflow_");
}
async function verifyRouteComment(event, token) {
  const route = safeRoutePayload(event.payload);
  const comment = await gh("/repos/" + REPO + "/issues/comments/" + encodeURIComponent(route.source_comment_id), token);
  const expectedIssue = "/issues/" + route.issue_number;
  const body = String(comment.body || "");
  const hasClaimMarker = body.includes("PRODUCER CLAIM") || body.includes("DISPATCH EXECUTOR CLAIM");
  const roleMatch = body.match(/\[MUSEai\]@\{role:\{([^}]+)\}\}/);
  if (!String(comment.issue_url || "").endsWith(expectedIssue) || !hasClaimMarker ||
      !roleMatch || roleMatch[1].trim() !== route.route_role) {
    throw new Error("route comment provenance mismatch");
  }
  if (route.source === "dispatch_executor_claim") {
    const armMatch = body.match(/^\s*-\s*arm:\s*([^\s(]+)(?:\s*\(([^)]+)\))?/m);
    const dispatchMatch = body.match(/^\s*-\s*dispatch_id:\s*([^\r\n]+)/m);
    if (!armMatch || armMatch[1].trim() !== route.arm_id ||
        (route.model && (armMatch[2] || "").trim() !== route.model) ||
        (route.dispatch_id && (!dispatchMatch || dispatchMatch[1].trim() !== route.dispatch_id))) {
      throw new Error("executor route metadata mismatch");
    }
  } else if (route.provider) {
    const providerMatch = body.match(/^\s*-\s*resolved provider:\s*([^\r\n]+)/m);
    if (!providerMatch || providerMatch[1].trim() !== route.provider) {
      throw new Error("producer route metadata mismatch");
    }
  }
  if (event.actor && comment.user && comment.user.login !== event.actor) throw new Error("route actor mismatch");
  return route;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, {status: 204, headers: cors});
    if (url.pathname === "/health" && request.method === "GET") {
      const row = await env.EVENTS_DB.prepare(
        "SELECT COUNT(*) AS n, MAX(received_at) AS latest FROM runtime_events"
      ).first();
      return Response.json({ok: true, repo: REPO, ...row}, {
        headers: {...cors, "Cache-Control": "no-store"}
      });
    }
    if (url.pathname === "/ingest" && request.method === "POST") {
      const authorization = request.headers.get("Authorization") || "";
      const token = authorization.startsWith("Bearer ") ? authorization.slice(7) : "";
      if (!token) return new Response("unauthorized", {status: 401});
      let body;
      try { body = await request.json(); }
      catch { return new Response("invalid json", {status: 400}); }
      const events = Array.isArray(body.events) ? body.events : [body.event || body];
      if (events.length > 100) return new Response("invalid event batch", {status: 400});
      if (events.length === 0) return Response.json({ok: true, accepted: 0}, {
        headers: {...cors, "Cache-Control": "no-store"}
      });
      try {
        for (const event of events) {
          if (!validEvent(event)) return new Response("invalid event envelope", {status: 400});
          const run = await gh("/repos/" + REPO + "/actions/runs/" + encodeURIComponent(event.run_id), token);
          if (String(run.id) !== String(event.run_id) || run.repository?.full_name !== REPO) {
            return new Response("run does not match repository", {status: 403});
          }
          let routePayload = null;
          if (event.kind === "route") routePayload = await verifyRouteComment(event, token);
          if (event.kind === "job") {
            const job = await gh("/repos/" + REPO + "/actions/jobs/" + encodeURIComponent(event.job_id), token);
            if (String(job.run_id) !== String(event.run_id)) return new Response("job/run mismatch", {status: 403});
          }
          if (event.kind !== "route") {
            const runStatus = run.status === "completed" ? (run.conclusion || "completed") : (run.status || "unknown");
            const runAt = run.updated_at || run.run_started_at || run.created_at || new Date().toISOString();
            const runEventId = "workflow:" + run.id + ":" + (run.run_attempt || 1) + ":" + runStatus + ":" + runAt;
            await env.EVENTS_DB.prepare(
              "INSERT OR IGNORE INTO runtime_events (id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            ).bind(runEventId, "workflow", "workflow_" + runStatus, runStatus,
              run.name || event.workflow || "GitHub Actions", null, null, REPO,
              Number(run.id), Number(run.run_attempt || 1), null, run.head_sha || null,
              run.html_url || null, String(runAt), new Date().toISOString(),
              JSON.stringify({workflow_path: run.path || null, actor: bounded(event.actor, 120)})).run();
          }
          const storedPayload = event.kind === "route" ? routePayload : {actor: bounded(event.actor, 120)};
          await env.EVENTS_DB.prepare(
            "INSERT OR IGNORE INTO runtime_events (id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
          ).bind(String(event.id), String(event.kind), String(event.event), String(event.status),
            String(event.workflow), bounded(event.job, 200), bounded(event.step, 200), REPO,
            Number(event.run_id), Number(event.run_attempt), event.job_id ? Number(event.job_id) : null,
            event.head_sha || run.head_sha || null, event.url || run.html_url || null,
            String(event.occurred_at), new Date().toISOString(), JSON.stringify(storedPayload || {})).run();
        }
        return Response.json({ok: true, accepted: events.length}, {
          headers: {...cors, "Cache-Control": "no-store"}
        });
      } catch (error) {
        return Response.json({ok: false, error: "verification_or_storage_failed"}, {
          status: 502, headers: cors
        });
      }
    }
    if (url.pathname === "/events" && request.method === "GET") {
      const limit = Math.min(400, Math.max(1, Number(url.searchParams.get("limit") || 200)));
      const afterRaw = url.searchParams.get("after_seq");
      let rows;
      if (afterRaw !== null) {
        const after = Number(afterRaw);
        if (!Number.isSafeInteger(after) || after < 0) return new Response("invalid cursor", {status: 400, headers: cors});
        rows = await env.EVENTS_DB.prepare(
          "SELECT rowid AS seq,id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload FROM runtime_events WHERE rowid > ? ORDER BY rowid ASC LIMIT ?"
        ).bind(after, limit).all();
      } else {
        rows = await env.EVENTS_DB.prepare(
          "SELECT rowid AS seq,id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload FROM runtime_events ORDER BY rowid DESC LIMIT ?"
        ).bind(limit).all();
        rows.results = (rows.results || []).reverse();
      }
      const events = rows.results || [];
      const nextAfter = events.length ? Number(events[events.length - 1].seq) : Number(afterRaw || 0);
      return Response.json({
        schema: "admin-graph-live-events/v1",
        source: "QUE task-claim observer + GitHub Actions lifecycle observer + API-backed run reconciler",
        repo: REPO, generated_at: new Date().toISOString(), poll_hint_ms: 5000,
        next_after_seq: nextAfter,
        has_more: afterRaw !== null && events.length === limit,
        events
      }, {headers: {...cors, "Cache-Control": "no-store"}});
    }
    return new Response("not found", {status: 404, headers: cors});
  }
};
