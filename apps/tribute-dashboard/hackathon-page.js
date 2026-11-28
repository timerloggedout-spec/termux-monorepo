(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const api = window.HackathonDesk;
  const esc = api.escapeHtml;
  const safe = api.safeExternalUrl;
  const sources = {
    opportunities: "https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/que/feeds/opportunity-priority.json",
    challenges: "./data/challenge-public-feed.json",
    countdowns: "./data/challenge-countdowns-feed.json",
    desk: "./data/desk-feed.json",
    queue: "./data/que-queue-feed.json"
  };
  const state = { opportunities: [], challenges: [], countdowns: [], pipeline: null };
  function link(url, label) {
    const href = safe(url);
    return href ? '<a href="' + esc(href) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + ' ↗</a>' : "";
  }
  function tag(value, stale) {
    return '<span class="tag' + (stale ? ' stale' : '') + '">' + esc(value || "status unknown") + '</span>';
  }
  async function get(url) {
    try {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) throw new Error("HTTP " + response.status);
      return await response.json();
    } catch (error) {
      return null;
    }
  }
  function freshnessLabel(feed) {
    if (!feed) return "Unavailable";
    const age = feed.freshness && feed.freshness.age_hours;
    const stamp = feed.generated_at ? new Date(feed.generated_at).toLocaleString() : "timestamp unavailable";
    return (feed.status || "unknown").toUpperCase() + " · " + stamp + (age == null ? "" : " · " + age + "h old");
  }
  function renderOpportunities() {
    const q = $("opportunity-search").value.trim().toLowerCase();
    const rows = state.opportunities.filter((r) => [r.name, r.host, r.state, r.id].join(" ").toLowerCase().includes(q));
    $("opportunity-list").innerHTML = rows.length ? rows.map((r) => {
      const source = link(r.source_url || r.url, "Source");
      return '<article class="record-card"><div class="record-meta">' + tag(r.rank ? "Rank " + r.rank : "Unranked", false) + tag(r.tier || "Tier pending", false) + tag(r.state || "State pending", false) + '</div><h3>' + esc(r.name || r.id || "Opportunity") + '</h3><p>' + esc([r.host, r.next_gate].filter(Boolean).join(" · ") || "Review the source record for eligibility and next steps.") + '</p>' + source + '</article>';
    }).join("") : '<p class="empty">No opportunity records match this filter.</p>';
  }
  function renderChallenges() {
    $("challenge-list").innerHTML = state.challenges.length ? state.challenges.map((r) => {
      const url = link(r.official_url || r.source_url, "Official event source");
      const dates = r.dates && Object.entries(r.dates).filter(([,v]) => typeof v === "string" || (v && v.at)).slice(0,3).map(([k,v]) => k.replaceAll("_"," ") + ": " + (typeof v === "string" ? v : v.at)).join(" · ");
      const matches = (r.matches || []).slice(0,4).map((m) => m.id + " · " + m.name).join(" | ");
      const gates = (r.gates || []).map((g) => g.label + ": " + (g.status || g.state || "status pending")).join(" · ");
      return '<article class="record-card"><div class="record-meta">' + tag(r.id || "Event", false) + tag(r.status || r.rules_state || "Status pending", false) + tag(r.registration && r.registration.state || "Registration state pending", false) + '</div><h3>' + esc(r.name || "Challenge event") + '</h3><p>' + esc([r.host, r.platform, r.format, r.kind].filter(Boolean).join(" · ")) + '</p><p>' + esc(dates || "Dates are not recorded in this projection.") + '</p>' + (matches ? '<p><b>Matches:</b> ' + esc(matches) + '</p>' : '') + (gates ? '<p><b>Gates:</b> ' + esc(gates) + '</p>' : '') + (r.prizes && r.prizes.pool ? '<p><b>Prize pool:</b> ' + esc(r.prizes.pool) + '</p>' : '') + url + '</article>';
    }).join("") : '<p class="empty">Challenge feed unavailable or contains no event records.</p>';
  }
  function renderCountdowns() {
    $("countdown-list").innerHTML = state.countdowns.length ? state.countdowns.map((r) => {
      const target = r.countdown && r.countdown.target === "opens" ? r.opens : r.closes;
      const date = target ? new Date(target).toLocaleString() : "No deadline instant recorded";
      return '<article class="record-card"><div class="record-meta">' + tag(r.countdown && r.countdown.state || "UNKNOWN", false) + tag(r.status || "Status pending", false) + '</div><h3>' + esc(r.title || r.id || "Event") + '</h3><p>' + esc(date) + '</p><p>' + esc(r.prizes && r.prizes.pool || "Prize details are not recorded.") + '</p></article>';
    }).join("") : '<p class="empty">Countdown feed unavailable.</p>';
  }
  function renderPipeline() {
    const p = state.pipeline;
    $("queue-tiers").innerHTML = p && p.tiers.length ? p.tiers.map((t) => '<div class="stack-row"><b>Tier ' + esc(t.tier) + '</b><small>' + esc(t.queued || 0) + ' queued · ' + esc(t.in_progress || 0) + ' in progress</small></div>').join("") : '<p class="empty">Queue tier data unavailable.</p>';
    $("dispatch-claims").innerHTML = p && p.dispatch_claims.length ? p.dispatch_claims.map((c) => '<div class="stack-row"><span>' + esc(c.title || c.entry || c.issue || "Claim") + '</span><small>' + esc(c.state || "claimed") + '</small></div>').join("") : '<p class="empty">No active dispatch claims in the published projection.</p>';
    $("traversals").innerHTML = p && p.traversals.length ? p.traversals.map((t) => '<div class="stack-row"><span>' + esc(t.entry || t.project || "Traversal") + '</span><small>' + esc(t.status || "status pending") + ' · ' + esc(t.next || "next step pending") + '</small></div>').join("") : '<p class="empty">Desk traversal feed unavailable.</p>';
    $("pipeline-meta").textContent = p ? p.status.toUpperCase() : "Unavailable";
  }
  async function load() {
    $("overall-state").textContent = "Checking feeds";
    const [opRaw, chRaw, coRaw, deskRaw, queueRaw] = await Promise.all([
      get(sources.opportunities), get(sources.challenges), get(sources.countdowns), get(sources.desk), get(sources.queue)
    ]);
    const op = api.normalizeOpportunityFeed(opRaw);
    const ch = api.normalizeChallengeFeed(chRaw);
    const co = api.normalizeCountdownFeed(coRaw);
    const pipeline = api.normalizePipelineFeed({ desk: deskRaw, queue: queueRaw });
    state.opportunities = op.records || [];
    state.challenges = ch.records || [];
    state.countdowns = co.records || [];
    state.pipeline = pipeline;
    $("opportunity-meta").textContent = freshnessLabel(op);
    $("challenge-meta").textContent = freshnessLabel(ch);
    $("countdown-meta").textContent = freshnessLabel(co);
    $("metrics").innerHTML = [
      ["Opportunities", state.opportunities.length, freshnessLabel(op)],
      ["Challenge events", state.challenges.length, freshnessLabel(ch)],
      ["Pipeline traversals", pipeline.traversals.length, pipeline.status.toUpperCase()],
      ["Dispatch claims", pipeline.dispatch_claims.length, pipeline.dispatch_source_schema || "QUE queue projection"]
    ].map(([label, value, detail]) => '<article class="metric"><span>' + esc(label) + '</span><strong>' + esc(value) + '</strong><small>' + esc(detail) + '</small></article>').join("");
    const statuses = [op.status, ch.status, co.status, pipeline.status];
    const stale = statuses.includes("stale");
    const healthy = statuses.every((s) => s === "fresh");
    $("overall-state").textContent = healthy ? "All feeds current" : stale ? "Review feed freshness" : "Partial source coverage";
    $("overall-detail").textContent = statuses.map((s) => s.toUpperCase()).join(" · ");
    $("overall-state").className = stale ? "freshness-stale" : "";
    renderOpportunities(); renderChallenges(); renderCountdowns(); renderPipeline();
  }
  $("opportunity-search").addEventListener("input", renderOpportunities);
  $("refresh").addEventListener("click", load);
  load();
}());
