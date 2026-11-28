/* global module, globalThis */
(function attachHackathonDesk(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.HackathonDesk = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function createHackathonDesk() {
  "use strict";

  const SCHEMAS = Object.freeze({
    opportunity: "que.opportunity-priority/v1",
    challenge: "challenge-public-feed/v1",
    countdown: "challenge-countdowns-feed/v1.2",
    desk: "desk-feed/v1.3",
    queue: "que-queue-feed/v1",
  });
  const DATE_FIELDS = Object.freeze([
    "announced", "reg_open", "reg_close", "build_start", "build_end",
    "submissions_open", "deadline", "judging_end", "winners_at",
    "register_build", "preliminary_due", "finalists_announced", "final_due", "winners",
  ]);

  function isRecord(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function scalar(value) {
    return value === null || ["string", "number", "boolean"].includes(typeof value)
      ? value
      : undefined;
  }

  function pick(record, fields) {
    if (!isRecord(record)) return {};
    const output = {};
    fields.forEach((field) => {
      if (!Object.prototype.hasOwnProperty.call(record, field)) return;
      const value = scalar(record[field]);
      if (value !== undefined && value !== null) output[field] = value;
    });
    return output;
  }

  function nowMillis(now) {
    if (now instanceof Date) return now.getTime();
    if (typeof now === "number" && Number.isFinite(now)) return now;
    if (typeof now === "string") {
      const parsed = Date.parse(now);
      if (Number.isFinite(parsed)) return parsed;
    }
    return Date.now();
  }

  function freshness(payload, now, fallbackHours) {
    const current = nowMillis(now);
    const generated = typeof payload.generated_at === "string"
      ? Date.parse(payload.generated_at)
      : NaN;
    const configured = Number(payload.stale_after_hours);
    const staleAfter = Number.isFinite(configured) && configured > 0
      ? configured
      : fallbackHours;
    if (!Number.isFinite(generated)) {
      return {
        state: "unknown",
        age_hours: null,
        stale_after_hours: staleAfter,
        generated_at: payload.generated_at || null,
      };
    }
    const ageHours = Math.max(0, (current - generated) / 3600000);
    const freshUntil = typeof payload.fresh_until === "string"
      ? Date.parse(payload.fresh_until)
      : NaN;
    const stale = payload.stale === true
      || ageHours > staleAfter
      || (Number.isFinite(freshUntil) && current > freshUntil);
    return {
      state: stale ? "stale" : "fresh",
      age_hours: Math.round(ageHours * 100) / 100,
      stale_after_hours: staleAfter,
      generated_at: payload.generated_at,
      fresh_until: Number.isFinite(freshUntil) ? payload.fresh_until : null,
    };
  }

  function invalidEnvelope(status, source) {
    return {
      status,
      source: source || null,
      generated_at: null,
      freshness: { state: status, age_hours: null, stale_after_hours: null },
      records: [],
    };
  }

  function collectionEnvelope(payload, schema, key, now, fallbackHours) {
    if (payload === null || payload === undefined) return invalidEnvelope("unavailable");
    if (!isRecord(payload) || payload.schema !== schema || !Array.isArray(payload[key])) {
      return invalidEnvelope("invalid", isRecord(payload) ? payload.source : null);
    }
    const fresh = freshness(payload, now, fallbackHours);
    return {
      status: fresh.state === "stale" ? "stale" : fresh.state === "unknown" ? "invalid" : "fresh",
      source: payload.source || null,
      generated_at: payload.generated_at || null,
      freshness: fresh,
      records: payload[key],
    };
  }

  function normalizePriorityTimebox(value) {
    return pick(value, ["wall", "landing", "cushion", "escalation", "final", "source", "wall_source"]);
  }

  function normalizeDateValue(value) {
    if (typeof value === "string" || value === null) return value;
    return isRecord(value) ? pick(value, ["at", "tz", "source"]) : null;
  }

  function normalizeDates(value) {
    if (!isRecord(value)) return {};
    const output = {};
    DATE_FIELDS.forEach((field) => {
      if (Object.prototype.hasOwnProperty.call(value, field)) {
        output[field] = normalizeDateValue(value[field]);
      }
    });
    return output;
  }

  function normalizeOpportunityFeed(payload, now) {
    if (payload === null || payload === undefined) return invalidEnvelope("unavailable");
    if (!isRecord(payload)
      || payload.schema !== SCHEMAS.opportunity
      || !Array.isArray(payload.opportunities)
      || !Array.isArray(payload.terminal_opportunities)) {
      return invalidEnvelope("invalid", isRecord(payload) ? payload.source : null);
    }
    const fresh = freshness(payload, now, 72);
    const normalizeOpportunity = (item, active) => {
      const record = pick(item, [
        "id", "slug", "rank", "tier", "score", "name", "host", "state",
        "verdict", "prep_state", "next_gate", "days_to_gate", "source_url", "url",
      ]);
      if (isRecord(item.priority_timebox)) {
        record.priority_timebox = normalizePriorityTimebox(item.priority_timebox);
      }
      record.active = active;
      return record;
    };
    const active = payload.opportunities.map((item) => normalizeOpportunity(item, true));
    const terminal = payload.terminal_opportunities.map((item) => normalizeOpportunity(item, false));
    return {
      status: fresh.state === "stale" ? "stale" : fresh.state === "unknown" ? "invalid" : "fresh",
      source: payload.source || "ops/que/feeds/opportunity-priority.json",
      generated_at: payload.generated_at || null,
      freshness: fresh,
      records: active.concat(terminal),
    };
  }

  function normalizeChallengeFeed(payload, now) {
    const envelope = collectionEnvelope(payload, SCHEMAS.challenge, "events", now, 72);
    if (envelope.status === "invalid" || envelope.status === "unavailable") return envelope;
    const eventFields = [
      "id", "name", "host", "platform", "status", "format", "kind",
      "league_window", "rules_state", "claim_gate", "deadline", "fetched_at",
      "official_url", "source_url", "also_platforms", "constraints",
    ];
    envelope.records = envelope.records.map((event) => {
      const out = pick(event, eventFields);
      if (isRecord(event.dates)) out.dates = normalizeDates(event.dates);
      if (Array.isArray(event.also_platforms)) {
        out.also_platforms = event.also_platforms.filter((item) => typeof item === "string");
      }
      if (typeof event.constraints === "string") out.constraints = event.constraints;
      else if (Array.isArray(event.constraints)) {
        out.constraints = event.constraints.filter((item) => typeof item === "string");
      }
      if (Array.isArray(event.organizers)) {
        out.organizers = event.organizers.map((item) => pick(item, [
          "name", "role", "source", "source_url", "fetched_at",
        ]));
      }
      if (Array.isArray(event.matches)) {
        out.matches = event.matches.map((item) => {
          const match = pick(item, ["id", "name", "points", "state", "tasks", "rules", "deadline"]);
          if (Object.prototype.hasOwnProperty.call(item, "dates")) {
            match.dates = normalizeDateValue(item.dates);
          }
          return match;
        });
      }
      if (Array.isArray(event.gates)) {
        out.gates = event.gates.map((item) => pick(item, [
          "id", "label", "blocks", "status", "state", "text",
        ]));
      }
      if (isRecord(event.prizes)) {
        out.prizes = pick(event.prizes, ["status", "pool", "source", "notes"]);
        if (Array.isArray(event.prizes.tiers)) {
          out.prizes.tiers = event.prizes.tiers.map((item) => pick(item, [
            "place", "award", "source_url",
          ]));
        } else if (typeof event.prizes.tiers === "string") {
          out.prizes.tiers = event.prizes.tiers;
        }
      }
      if (isRecord(event.registration)) {
        out.registration = pick(event.registration, ["state"]);
      }
      if (isRecord(event.submission)) {
        out.submission = pick(event.submission, ["state", "at"]);
      }
      return out;
    });
    return envelope;
  }

  function countdownState(entry, now) {
    const current = nowMillis(now);
    const opens = typeof entry.opens === "string" ? Date.parse(entry.opens) : NaN;
    const closes = typeof entry.closes === "string" ? Date.parse(entry.closes) : NaN;
    const completed = typeof entry.status === "string"
      && /^(completed|closed)/i.test(entry.status.trim());
    if (completed) return { state: "CLOSED", target: null, remaining_seconds: null };
    if (Number.isFinite(opens) && current < opens) {
      return {
        state: "UPCOMING",
        target: "opens",
        remaining_seconds: Math.ceil((opens - current) / 1000),
      };
    }
    if (Number.isFinite(closes) && current <= closes) {
      return {
        state: "OPEN",
        target: "closes",
        remaining_seconds: Math.ceil((closes - current) / 1000),
      };
    }
    if (Number.isFinite(closes) && current > closes) {
      return { state: "OVERDUE", target: "closes", remaining_seconds: 0 };
    }
    if (Number.isFinite(opens) && current >= opens) {
      return { state: "OPEN", target: null, remaining_seconds: null };
    }
    return { state: "NOT_ESTABLISHED", target: null, remaining_seconds: null };
  }

  function normalizeCountdownFeed(payload, now) {
    const envelope = collectionEnvelope(payload, SCHEMAS.countdown, "entries", now, 72);
    if (envelope.status === "invalid" || envelope.status === "unavailable") return envelope;
    envelope.records = envelope.records.map((entry) => ({
      ...pick(entry, ["id", "title", "status", "prizes", "submission"]),
      opens: Object.prototype.hasOwnProperty.call(entry, "opens") ? normalizeDateValue(entry.opens) : undefined,
      closes: Object.prototype.hasOwnProperty.call(entry, "closes") ? normalizeDateValue(entry.closes) : undefined,
      countdown: countdownState(entry, now),
    }));
    return envelope;
  }

  function normalizeDeskFeed(payload, now) {
    const envelope = collectionEnvelope(payload, SCHEMAS.desk, "traversals", now, 72);
    if (envelope.status === "invalid" || envelope.status === "unavailable") return envelope;
    envelope.records = envelope.records.map((row) => ({
      ...pick(row, ["entry", "project", "artifact_repo", "status", "next"]),
      stages: pick(row.stages, ["spec", "desk", "builder", "pr", "ci", "merge", "sync"]),
    }));
    return envelope;
  }

  function normalizeQueueFeed(payload, now) {
    if (payload === null || payload === undefined) return invalidEnvelope("unavailable");
    if (!isRecord(payload) || payload.schema !== SCHEMAS.queue || !isRecord(payload.queue)) {
      return invalidEnvelope("invalid", isRecord(payload) ? payload.source : null);
    }
    const fresh = freshness(payload, now, 1);
    const tiers = isRecord(payload.queue.tiers)
      ? Object.keys(payload.queue.tiers).sort((a, b) => Number(a) - Number(b)).map((key) => {
        const tier = payload.queue.tiers[key];
        return pick(tier, ["tier", "queued", "in_progress", "oldest_queued_at"]);
      })
      : [];
    const claims = isRecord(payload.dispatch_claims)
      && Array.isArray(payload.dispatch_claims.active_claims)
      ? payload.dispatch_claims.active_claims.map((claim) => {
        const row = pick(claim, ["issue", "entry", "title", "state"]);
        if (isRecord(claim.tier)) row.tier = pick(claim.tier, ["index", "name"]);
        if (isRecord(claim.claim)) {
          row.claim = pick(claim.claim, ["at"]);
          const ref = safeExternalUrl(claim.claim.ref);
          if (ref) row.claim.ref = ref;
        }
        return row;
      })
      : [];
    return {
      status: fresh.state === "stale" ? "stale" : fresh.state === "unknown" ? "invalid" : "fresh",
      source: payload.provenance?.producer || "ops/que/feeds/que-queue-feed.json",
      generated_at: payload.generated_at || null,
      freshness: fresh,
      tiers,
      dispatch_claims: claims,
      dispatch_source_schema: payload.dispatch_claims?.source_schema || null,
      dispatch_source_generated_at: payload.dispatch_claims?.source_generated_at || null,
    };
  }

  function normalizePipelineFeed(payload, now) {
    if (!isRecord(payload)) {
      return { status: "unavailable", traversals: [], tiers: [], dispatch_claims: [], sources: {} };
    }
    const desk = normalizeDeskFeed(payload.desk, now);
    const queue = normalizeQueueFeed(payload.queue, now);
    const available = [desk, queue].filter((item) => item.status === "fresh" || item.status === "stale");
    let status = "unavailable";
    if (available.length === 2) {
      status = available.some((item) => item.status === "stale") ? "stale" : "fresh";
    } else if (available.length === 1) {
      status = "partial";
    } else if (desk.status === "invalid" || queue.status === "invalid") {
      status = "invalid";
    }
    return {
      status,
      traversals: desk.records || [],
      tiers: queue.tiers || [],
      dispatch_claims: queue.dispatch_claims || [],
      dispatch_source_schema: queue.dispatch_source_schema || null,
      dispatch_source_generated_at: queue.dispatch_source_generated_at || null,
      sources: {
        desk: { source: desk.source, generated_at: desk.generated_at, freshness: desk.freshness },
        queue: { source: queue.source, generated_at: queue.generated_at, freshness: queue.freshness },
      },
    };
  }

  function safeExternalUrl(value) {
    if (typeof value !== "string" || !value.trim()) return null;
    try {
      const parsed = new URL(value);
      if (parsed.protocol !== "https:" || !parsed.hostname || parsed.username || parsed.password) {
        return null;
      }
      return parsed.href;
    } catch (_error) {
      return null;
    }
  }

  function escapeHtml(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  return Object.freeze({
    normalizeOpportunityFeed,
    normalizeChallengeFeed,
    normalizeCountdownFeed,
    normalizePipelineFeed,
    safeExternalUrl,
    escapeHtml,
  });
});
