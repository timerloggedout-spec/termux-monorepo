/* Method-aware views over one versioned campaign feed. */
(function () {
  "use strict";
  const $ = id => document.getElementById(id);
  const esc = value => String(value == null ? "" : value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const state = { feed: null, method: "RFP-V1", view: "overview" };
  const empty = message => '<div class="rv-empty">' + esc(message) + '</div>';
  const list = value => Array.isArray(value) ? value : [];
  function statusPill(value) { return '<span class="rv-pill rv-state">' + esc(value || "unknown") + '</span>'; }
  function selectedMethod() { return list(state.feed.methods).find(x => x.id === state.method) || list(state.feed.methods)[0]; }
  function filtered(items) { return list(items).filter(x => !x.method_id || x.method_id === state.method); }
  function mergeCampaigns(viewCampaigns, doeCampaigns) {
    const merged = new Map();
    list(doeCampaigns).forEach(c => {
      const id = c.campaign_id || c.id;
      if (!id) return;
      merged.set(String(id), Object.assign({method_id:null,source_surface:"doe"}, c, {campaign_id:c.campaign_id || String(id)}));
    });
    list(viewCampaigns).forEach(c => {
      const id = c.campaign_id || c.id;
      if (!id) return;
      const prior = merged.get(String(id)) || {};
      merged.set(String(id), Object.assign({}, prior, c, {
        campaign_id:c.campaign_id || String(id),
        source_surface:c.source_surface || prior.source_surface || "view-feed"
      }));
    });
    return Array.from(merged.values());
  }
  function methodSummary() {
    const m = selectedMethod();
    $("rv-method-summary").innerHTML = m ? '<div class="rv-meta">' + statusPill(m.status) + '<span class="rv-pill">' + esc(m.kind) + '</span><span class="rv-pill">' + esc(m.id) + '</span></div><h2>' + esc(m.name) + '</h2><p>' + esc(m.description) + '</p><p class="rv-muted">Native design: ' + esc(m.design) + '</p><p class="rv-muted">DoE campaigns without an explicit method_id remain shared family evidence; the view does not infer pipeline attribution.</p>' : empty("No method catalogue is available.");
  }
  function overview() {
    const campaigns = filtered(state.feed.campaigns), streams = filtered(state.feed.workstreams);
    const recordedRuns = campaigns.reduce((sum,c) => sum + Number(c.runs || 0), 0);
    const withResults = campaigns.filter(c => c.results && typeof c.results === "object").length;
    return '<div class="rv-grid">' +
      [['DoE campaigns',campaigns.length],['Recorded runs (campaign totals)',recordedRuns],['Campaign result summaries',withResults],['Scheduled workstreams',streams.length]].map(([k,v]) => '<article class="rv-card"><div class="rv-muted">' + k + '</div><h2>' + v + '</h2></article>').join("") +
      '</div><div class="rv-card" style="margin-top:.8rem"><h3>Method catalogue</h3><div class="rv-scroll"><table class="rv-table"><thead><tr><th>Version</th><th>Type</th><th>Design</th><th>Admission</th></tr></thead><tbody>' +
      list(state.feed.methods).map(m => '<tr><th>' + esc(m.id) + '<br>' + esc(m.name) + '</th><td>' + esc(m.kind) + '</td><td>' + esc(m.design) + '</td><td>' + statusPill(m.status) + '</td></tr>').join("") +
      '</tbody></table></div></div>' +
      (list(state.feed.doe_snapshot && state.feed.doe_snapshot.gaps).length ? '<div class="rv-card" style="margin-top:.8rem"><h3>Source-reported gaps</h3><ul>' + list(state.feed.doe_snapshot.gaps).map(g => '<li>' + esc(g) + '</li>').join("") + '</ul></div>' : '');
  }
  function gantt() {
    const source = filtered(state.feed.workstreams).filter(x => x.start && x.end);
    const streams = source.map(x => ({record:x,startMs:Date.parse(x.start),endMs:Date.parse(x.end)}));
    const valid = streams.filter(x => Number.isFinite(x.startMs) && Number.isFinite(x.endMs) && x.endMs >= x.startMs);
    const invalidCount = streams.length - valid.length;
    if (!valid.length) {
      const message = source.length ? "Schedule intervals require parseable start/end values with end at or after start." : "Gantt projection awaits method-linked workstream dates. The current DoE campaign snapshot carries campaign states and run totals, not start/end schedule fields. Add authoritative start/end dates to workstream records; phase order alone does not create calendar dates.";
      return empty(message);
    }
    const min = Math.min.apply(null, valid.map(x => x.startMs));
    const max = Math.max.apply(null, valid.map(x => x.endMs));
    const span = Math.max(1, max-min);
    return (invalidCount ? '<p class="rv-muted" role="status">Excluded ' + invalidCount + ' workstream interval(s) with invalid or reversed dates.</p>' : '') +
      '<div class="rv-card"><h3>Workstream schedule</h3>' + valid.map(item => {
        const x = item.record;
        const left = Math.max(0,(item.startMs-min)/span*100), width = Math.max(1,(item.endMs-item.startMs)/span*100);
        return '<div style="display:grid;grid-template-columns:minmax(130px,1fr) 3fr;gap:.8rem;align-items:center;padding:.6rem 0;border-bottom:1px solid var(--line)"><div><b>' + esc(x.title || x.id) + '</b><small class="rv-muted" style="display:block">' + esc(x.start) + ' → ' + esc(x.end) + '</small></div><div style="background:#0b1118;border-radius:8px;padding:4px"><div class="rv-bar" style="margin-left:' + left + '%;width:' + width + '%"></div></div></div>';
      }).join("") + '</div>';
  }
  function dependencies() {
    const streams = filtered(state.feed.workstreams);
    if (!streams.length) return '<div class="rv-graph">' + list(state.feed.phases).map((p,i) => '<div class="rv-node"><b>' + esc(p.id) + ' · ' + esc(p.name) + '</b><small>' + esc(p.theme) + (i < 12 ? ' → next governance phase' : ' · evolution / close') + '</small></div>').join("") + '</div><p class="rv-muted">This is the canonical phase sequence. Runtime dependency edges appear when workstream records provide dependencies.</p>';
    return '<div class="rv-graph">' + streams.map(x => '<div class="rv-node"><b>' + esc(x.title || x.id) + '</b><small>Depends on: ' + esc(list(x.dependencies).join(", ") || "none declared") + ' · ' + esc(x.state || "unclassified") + '</small></div>').join("") + '</div>';
  }
  function kanban() {
    const campaigns = filtered(state.feed.campaigns), methods = list(state.feed.methods);
    const stages = ["discovered","classified","triage_pending","eligible_for_design","pre_registered","admitted_design_only","executing","executed","validated","promoted","retained","culled","deferred","blocked","superseded","historical"];
    return '<div class="rv-kanban">' + stages.map(stage => {
      const items = campaigns.filter(x => x.state === stage);
      return '<section class="rv-lane"><b>' + esc(stage.replaceAll("_"," ")) + '</b><span class="rv-muted"> · ' + items.length + '</span>' + items.map(x => '<div class="rv-item">' + esc(x.campaign_id) + '<small class="rv-muted" style="display:block">' + esc(x.design_type || x.design_record || "design metadata unavailable") + '</small><small class="rv-muted" style="display:block">' + Number(x.runs || 0) + ' recorded runs</small></div>').join("") + '</section>';
    }).join("") + '</div>' + (campaigns.length ? "" : empty("The DoE source feed contains no campaign records. The method catalogue currently contains " + methods.length + " versioned options."));
  }
  function design() {
    const designs = list(state.feed.design_classes);
    return '<div class="rv-card"><h3>Design-class availability</h3><div class="rv-scroll"><table class="rv-table"><thead><tr><th>Design</th><th>Purpose</th><th>Repository status</th><th>Generator</th></tr></thead><tbody>' +
      designs.map(d => '<tr><th>' + esc(d.name) + '</th><td>' + esc(d.purpose) + '</td><td>' + statusPill(d.status) + '</td><td><code>' + esc(d.generator || "not implemented") + '</code></td></tr>').join("") +
      '</tbody></table></div></div><p class="rv-muted">Design availability follows the repository DoE taxonomy. Vocabulary-only and candidate designs remain visibly distinct from implemented generators.</p>';
  }
  function results() {
    const campaigns = filtered(state.feed.campaigns);
    const withResults = campaigns.filter(c => c.results && typeof c.results === "object");
    if (!withResults.length) return empty("The source feed has no campaign result payloads for this method. Campaign run totals remain separate from per-run experiment records.");
    return withResults.map(c => {
      const arms = c.results.arms && typeof c.results.arms === "object" ? Object.entries(c.results.arms) : [];
      return '<article class="rv-card" style="margin-bottom:.8rem"><h3>' + esc(c.campaign_id) + '</h3><p>' + esc(c.design_type || "Design details unavailable") + '</p><p>Campaign state: ' + statusPill(c.state) + ' · source run count: ' + Number(c.runs || 0) + '</p><p class="rv-muted">Attribution: ' + esc(c.method_id || "shared DoE family evidence; no RFP method mapping") + '</p>' +
        (c.results.verdict ? '<p>Verdict: <b>' + esc(c.results.verdict) + '</b></p>' : '') +
        (arms.length ? '<div class="rv-scroll"><table class="rv-table"><thead><tr><th>Arm</th><th>Runs</th><th>Mean accuracy</th><th>Mean input tokens</th><th>Rework</th></tr></thead><tbody>' +
          arms.map(([name,a]) => '<tr><th>' + esc(name) + '</th><td>' + Number(a.runs || 0) + '</td><td>' + (a.mean_accuracy == null ? '—' : esc(a.mean_accuracy)) + '</td><td>' + (a.mean_input_tokens == null ? '—' : esc(a.mean_input_tokens)) + '</td><td>' + (a.total_rework == null ? '—' : esc(a.total_rework)) + '</td></tr>').join("") +
          '</tbody></table></div>' : empty("Result payload is present without arm summaries.")) + '</article>';
    }).join("");
  }
  function adaptive() {
    const counts = {};
    filtered(state.feed.campaigns).forEach(x => { counts[x.state || "unclassified"] = (counts[x.state || "unclassified"] || 0) + 1; });
    const stages = ["discover","screen","expand","replicate","validate","promote / cull"];
    return '<div class="rv-flow">' + stages.map((s,i) => '<span><b>' + (i+1) + '. ' + esc(s) + '</b></span>' + (i < stages.length-1 ? '<span aria-hidden="true">→</span>' : '')).join("") + '</div><div class="rv-card" style="margin-top:.8rem"><h3>Current lifecycle counts</h3>' +
      (Object.keys(counts).length ? Object.keys(counts).sort().map(k => '<p>' + esc(k) + ': <b>' + counts[k] + '</b></p>').join("") : empty("Adaptive allocation awaits admitted workstream and run evidence.")) +
      '</div><p class="rv-muted">Adaptive follow-up must retain its pre-registered stopping rule and decision history.</p>';
  }
  function phases() {
    return '<div class="rv-track">' + list(state.feed.phases).map(p => '<article class="rv-phase"><b>' + esc(p.id) + ' · ' + p.order + '</b><strong>' + esc(p.name) + '</strong><small class="rv-muted" style="display:block">' + esc(p.theme) + '</small></article>').join("") + '</div><p class="rv-muted">Governance order remains stable; asynchronous workstreams may overlap when their dependencies, readiness, capacity and authorization allow.</p>';
  }
  const renderers = {overview,gantt,dependencies,kanban,design,results,adaptive,phases};
  function render() {
    methodSummary();
    $("rv-output").innerHTML = (renderers[state.view] || overview)();
    $("rv-output").setAttribute("aria-busy","false");
  }
  function init(payload) {
    const feed = payload.viewFeed, doe = payload.doeFeed;
    if (!feed || feed.schema_version !== "rfp-published-views/v1" || !Array.isArray(feed.methods) || !Array.isArray(feed.phases)) throw new Error("Unsupported or incomplete view feed.");
    if (!doe || doe.schema !== "dashboard-surface-feed/v1" || doe.surface !== "doe" || !doe.data) throw new Error("The DoE source feed is unavailable or has an unsupported schema.");
    feed.campaigns = mergeCampaigns(feed.campaigns, doe.data.campaigns);
    feed.doe_snapshot = {generated_at:doe.generated_at || null, gaps:list(doe.gaps), sources:list(doe.sources), honesty_rules:list(doe.honesty_rules)};
    state.feed = feed;
    const methodControl = $("rv-method");
    methodControl.replaceChildren(...list(feed.methods).map(m => {
      const option = document.createElement("option");
      option.value = m.id;
      option.textContent = m.id + " · " + m.name;
      return option;
    }));
    if (!list(feed.methods).some(m => m.id === state.method) && list(feed.methods).length) state.method = feed.methods[0].id;
    methodControl.value = state.method;
    $("rv-method").addEventListener("change", e => {state.method=e.target.value;render();});
    $("rv-view").addEventListener("change", e => {state.view=e.target.value;render();});
    $("rv-release").innerHTML = '<span class="rv-pill">' + esc(feed.feed_status) + '</span><span class="rv-pill">view schema ' + esc(feed.schema_version) + '</span><span class="rv-pill">DoE snapshot ' + esc(feed.doe_snapshot.generated_at || "stamp unknown") + '</span>';
    render();
  }
  Promise.all([
    fetch("./data/experiment-view-feed.json",{cache:"no-store"}).then(r => {if(!r.ok) throw new Error("view feed HTTP "+r.status);return r.json();}),
    fetch("./data/doe-feed.json",{cache:"no-store"}).then(r => {if(!r.ok) throw new Error("DoE feed HTTP "+r.status);return r.json();})
  ]).then(([viewFeed,doeFeed]) => init({viewFeed,doeFeed})).catch(err => {
    $("rv-output").innerHTML = empty("Published view feed unavailable: " + err.message);
    $("rv-method-summary").textContent = "Feed unavailable.";
    $("rv-output").setAttribute("aria-busy","false");
  });
}());