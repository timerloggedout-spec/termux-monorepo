(function (root) {
  "use strict";
  const DAY = 24 * 60 * 60 * 1000;
  const WEEK = 7 * DAY;

  function latest(items, key) {
    const values = (items || []).map(item => item && item[key]).filter(Boolean);
    return values.sort((a, b) => Date.parse(a) - Date.parse(b)).pop() || null;
  }

  function ageLabel(asOf, now) {
    const at = Date.parse(asOf || "");
    if (!Number.isFinite(at)) return "unknown";
    const delta = now - at;
    if (delta < 0) return "future timestamp";
    const minutes = Math.floor(delta / 60000);
    if (minutes < 60) return minutes + "m";
    const hours = Math.floor(minutes / 60);
    if (hours < 48) return hours + "h";
    return Math.floor(hours / 24) + "d " + (hours % 24) + "h";
  }

  function makeRow(id, label, asOf, evidence, detail, threshold, now, options) {
    const at = Date.parse(asOf || "");
    let status = "UNKNOWN";
    if (Number.isFinite(at)) {
      const old = now - at > threshold;
      status = options && options.event
        ? (old ? "NO RECENT EVENT" : "RECENT EVENT")
        : (old ? "STALE" : "FRESH");
    }
    return {
      id, label, as_of: asOf || null, evidence: evidence || "unknown",
      detail: detail || "", generated_at: options && options.generated_at || null,
      status, age: ageLabel(asOf, now)
    };
  }

  function rows(pack, now) {
    const current = Number.isFinite(now) ? now : Date.now();
    const s1 = (pack || {}).series1_api_core || {};
    const s2 = (pack || {}).series2_snapshots || {};
    const s3 = (pack || {}).series3_actions || {};
    const s4 = (pack || {}).series4_rate_limit_events || {};
    const s5 = (pack || {}).series5_vultr || {};
    const s6 = (pack || {}).series6_self_counts || {};
    const point = (s1.points || []).slice().sort((a, b) => Date.parse(a.at) - Date.parse(b.at)).pop();
    const snapshot = (s2.snapshots || []).slice().sort((a, b) => Date.parse(a.at) - Date.parse(b.at)).pop();
    const day = (s3.days || []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date))).pop();
    const event = (s4.events || []).slice().sort((a, b) => Date.parse(a.at) - Date.parse(b.at)).pop();
    const selfEvents = Object.values(s6.providers || {}).map(p => p && p.last_at).filter(Boolean);
    const selfLast = selfEvents.sort((a, b) => Date.parse(a) - Date.parse(b)).pop() || null;
    const plans = s5.plans || {};
    return [
      makeRow("api-core", "GitHub API core remaining", point && point.at,
        point && point.kind || "observed point",
        point ? ("remaining " + point.remaining + " / " + s1.limit + " " + (s1.unit || "") + " · " + (point.provenance || "")) : "",
        DAY, current),
      makeRow("quota-snapshots", "Quota service status snapshots", snapshot && snapshot.at,
        "status snapshot",
        snapshot ? (snapshot.rows + " rows · " + (snapshot.provenance || "")) : "",
        DAY, current),
      makeRow("actions-reconstructed", "Actions volume corpus", day && day.date,
        "reconstructed corpus",
        day ? ("+" + day.runs_delta + " runs · +" + day.jobs_delta + " jobs · corpus growth, not fleet volume") : "",
        DAY, current),
      makeRow("rate-limit-events", "Rate-limit incident register", event && event.at,
        event && event.class || "incident event",
        event ? ("HTTP " + (event.http == null ? "—" : event.http) + " · " + (event.surface || "")) : "",
        WEEK, current, {event: true}),
      makeRow("vultr-plan-rates", "Vultr plan-rate catalog", plans.pulled_at || s5.generated_at,
        "catalog pull",
        "Plan-rate catalog only; account usage legs remain explicit gaps.",
        WEEK, current, {generated_at: s5.generated_at}),
      makeRow("self-counts", "Fleet self-count events", selfLast,
        "self-counted records",
        "Tally generated " + (s6.generated_at || "unknown") + "; self-counts are not provider readings.",
        DAY, current, {generated_at: s6.generated_at})
    ];
  }

  const api = { rows, ageLabel };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.QuotaFreshness = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
