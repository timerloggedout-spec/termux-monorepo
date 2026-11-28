"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const Desk = require("../apps/tribute-dashboard/hackathon.js");

const HOUR = 60 * 60 * 1000;
const stamp = (ms) => new Date(ms).toISOString();

test("normalizes fresh opportunity records with source and freshness", () => {
  const now = Date.parse("2026-11-28T12:00:00Z");
  const result = Desk.normalizeOpportunityFeed({
    schema: "que.opportunity-priority/v1",
    generated_at: stamp(now - HOUR),
    stale_after_hours: 24,
    source: "ops/que/feeds/opportunity-priority.json",
    opportunities: [{ id: "C13", name: "RFP", rank: 1, tier: 3, score: 120, state: "candidate" }],
    terminal_opportunities: [{ id: "D1", name: "Submitted", rank: null, state: "complete" }],
  }, now);

  assert.equal(result.status, "fresh");
  assert.equal(result.source, "ops/que/feeds/opportunity-priority.json");
  assert.equal(result.records.length, 2);
  assert.equal(result.records[0].id, "C13");
  assert.equal(result.records[0].rank, 1);
  assert.equal(result.records[1].active, false);
});

test("keeps stale opportunities visible with stale status", () => {
  const now = Date.parse("2026-11-28T12:00:00Z");
  const result = Desk.normalizeOpportunityFeed({
    schema: "que.opportunity-priority/v1",
    generated_at: stamp(now - 48 * HOUR),
    stale_after_hours: 24,
    opportunities: [{ id: "C13", name: "RFP", rank: 1 }],
    terminal_opportunities: [],
  }, now);

  assert.equal(result.status, "stale");
  assert.equal(result.records.length, 1);
  assert.equal(result.freshness.state, "stale");
});

test("classifies missing and malformed opportunity feeds explicitly", () => {
  assert.equal(Desk.normalizeOpportunityFeed(null).status, "unavailable");
  assert.equal(Desk.normalizeOpportunityFeed({ schema: "wrong" }).status, "invalid");
  assert.equal(Desk.normalizeOpportunityFeed({
    schema: "que.opportunity-priority/v1",
    generated_at: "2026-11-28T00:00:00Z",
    opportunities: {},
  }).status, "invalid");
});

test("normalizes public challenges while retaining C11 matches and C12 dates", () => {
  const result = Desk.normalizeChallengeFeed({
    schema: "challenge-public-feed/v1",
    generated_at: "2026-11-28T12:00:00Z",
    source: "ops/challenge/coordinator.json",
    events: [
      { id: "C11", name: "AMD AI League", matches: [{ id: "M5", name: "AI-Powered Code Repository Repair" }] },
      { id: "C12", name: "UGREEN Hackathon", dates: { final_due: "2026-11-30T23:45:00-08:00" } },
    ],
  }, Date.parse("2026-11-28T12:00:00Z"));

  assert.equal(result.status, "fresh");
  assert.equal(result.records.find((event) => event.id === "C11").matches[0].id, "M5");
  assert.equal(result.records.find((event) => event.id === "C12").dates.final_due,
    "2026-11-30T23:45:00-08:00");
});

test("keeps completed countdowns and null deadlines explicit", () => {
  const now = Date.parse("2026-11-28T12:00:00Z");
  const result = Desk.normalizeCountdownFeed({
    schema: "challenge-countdowns-feed/v1.2",
    generated_at: stamp(now),
    entries: [
      { id: "D0", title: "Completed", status: "COMPLETED", opens: null, closes: null },
      { id: "D1", title: "Unscheduled", status: "ACTIVE", opens: null, closes: null },
      { id: "D2", title: "Upcoming", status: "ACTIVE", opens: stamp(now + HOUR), closes: null },
    ],
  }, now);

  assert.equal(result.records.length, 3);
  assert.equal(result.records[0].countdown.state, "CLOSED");
  assert.equal(result.records[1].opens, null);
  assert.equal(result.records[1].closes, null);
  assert.equal(result.records[1].countdown.state, "NOT_ESTABLISHED");
  assert.equal(result.records[2].countdown.state, "UPCOMING");
});

test("normalizes desk and QUE pipeline with embedded dispatch claims only", () => {
  const now = Date.parse("2026-11-28T12:00:00Z");
  const result = Desk.normalizePipelineFeed({
    desk: {
      schema: "desk-feed/v1.3",
      generated_at: stamp(now),
      traversals: [{ entry: "D0", project: "Oracle", status: "landed", stages: { spec: "done" } }],
    },
    queue: {
      schema: "que-queue-feed/v1",
      generated_at: stamp(now),
      queue: { tiers: { "1": { tier: 1, queued: 2, in_progress: 1 } } },
      dispatch_claims: {
        source_schema: "dispatch-state-feed/v1",
        source_generated_at: stamp(now - 5 * 60 * 1000),
        counts: { claimed: 1, escalated: 0, queued: 0 },
        active_claims: [{
          issue: 4277, title: "Build task", state: "claimed",
          tier: { index: 4, name: "FINAL" },
          score: 1718.301, score_components: { age: 41.108 },
          claim: { at: stamp(now - HOUR), ref: "https://github.com/timerloggedout-spec/termux-monorepo/issues/4277" },
        }],
      },
    },
  }, now);

  assert.equal(result.status, "fresh");
  assert.equal(result.traversals[0].entry, "D0");
  assert.equal(result.tiers[0].queued, 2);
  assert.equal(result.dispatch_claims[0].issue, 4277);
  assert.equal(result.dispatch_claims[0].tier.name, "FINAL");
  assert.equal("score" in result.dispatch_claims[0], false);
  assert.equal("score_components" in result.dispatch_claims[0], false);
});

test("validates safe external links and escapes rendered text", () => {
  assert.equal(Desk.safeExternalUrl("https://example.com/rules"), "https://example.com/rules");
  assert.equal(Desk.safeExternalUrl("javascript:alert(1)"), null);
  assert.equal(Desk.safeExternalUrl("http://example.com"), null);
  assert.equal(Desk.safeExternalUrl("//example.com/path"), null);
  assert.equal(Desk.safeExternalUrl("https://user:pass@example.com"), null);
  assert.equal(Desk.safeExternalUrl(""), null);
  assert.equal(Desk.escapeHtml("<script>&\"'"), "&lt;script&gt;&amp;&quot;&#39;");
});
