const test = require("node:test");
const assert = require("node:assert/strict");
const freshness = require("../apps/tribute-dashboard/quota-freshness.js");

test("quota freshness reports per-series as-of independent of pack generation", () => {
  const pack = {
    generated_at: "2026-11-13T00:00:00Z",
    series1_api_core: {
      limit: 5000, unit: "requests/hour",
      points: [{at: "2026-11-02T06:30:06Z", remaining: 3871, kind: "observed", provenance: "rate-limit read"}]
    },
    series2_snapshots: {snapshots: [{at: "2026-11-12T12:00:00Z", rows: 170, provenance: "quota status snapshot"}]},
    series3_actions: {days: [{date: "2026-11-13", runs_delta: 40, jobs_delta: 50}]},
    series4_rate_limit_events: {events: [{at: "2026-11-02T06:25:00Z", class: "secondary-403", http: 403}]},
    series5_vultr: {generated_at: "2026-11-03T20:26:58Z", plans: {pulled_at: "2026-11-03T20:26:58Z"}},
    series6_self_counts: {generated_at: "2026-11-03T19:30:52Z", providers: {sealion: {last_at: "2026-11-02T09:14:42Z"}}}
  };
  const rows = freshness.rows(pack, Date.parse("2026-11-13T00:00:00Z"));
  const byId = Object.fromEntries(rows.map(row => [row.id, row]));
  assert.equal(byId["api-core"].as_of, "2026-11-02T06:30:06Z");
  assert.equal(byId["api-core"].status, "STALE");
  assert.equal(byId["quota-snapshots"].status, "FRESH");
  assert.equal(byId["actions-reconstructed"].evidence, "reconstructed corpus");
  assert.equal(byId["rate-limit-events"].status, "NO RECENT EVENT");
  assert.equal(byId["vultr-plan-rates"].as_of, "2026-11-03T20:26:58Z");
  assert.equal(byId["self-counts"].as_of, "2026-11-02T09:14:42Z");
  assert.equal(byId["self-counts"].generated_at, "2026-11-03T19:30:52Z");
});

test("missing observations remain unknown instead of becoming zero or fresh", () => {
  const rows = freshness.rows({}, Date.parse("2026-11-13T00:00:00Z"));
  assert.ok(rows.every(row => row.status === "UNKNOWN"));
  assert.ok(rows.every(row => row.as_of === null));
});
