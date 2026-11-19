(function (root) {
  "use strict";
  var REPOSITORY = "timerloggedout-spec/timerloggedout-spec.github.io";
  var PAGES_SOURCE_BRANCH = "main-landing-studysprint-link";
  var API_ROOT = "https://api.github.com";
  var MAX_PR_COMPARISONS = 20;
  function classifyComparison(compare) {
    if (!compare || !Number.isFinite(compare.ahead_by) || !Number.isFinite(compare.behind_by)) return "UNKNOWN";
    if (compare.ahead_by === 0 && compare.behind_by === 0) return "NO_DELTA";
    if (compare.ahead_by > 0 && compare.behind_by === 0) return "AHEAD";
    if (compare.ahead_by > 0 && compare.behind_by > 0) return "DIVERGED";
    if (compare.ahead_by === 0 && compare.behind_by > 0) return "BEHIND";
    return "UNKNOWN";
  }
  function classifyPagesSource(compare) {
    if (!compare || !Number.isFinite(compare.ahead_by) || !Number.isFinite(compare.behind_by)) return "UNKNOWN";
    if (compare.ahead_by === 0 && compare.behind_by === 0) return "ALIGNED";
    if (compare.ahead_by > 0 && compare.behind_by === 0) return "FAST_FORWARD_AVAILABLE";
    if (compare.ahead_by > 0 && compare.behind_by > 0) return "DIVERGED";
    if (compare.ahead_by === 0 && compare.behind_by > 0) return "SOURCE_AHEAD";
    return "UNKNOWN";
  }
  function buildBranchRows(branches, pulls, comparisons, auditedComparisons, defaultBranch) {
    defaultBranch = defaultBranch || "main";
    branches = Array.isArray(branches) ? branches : [];
    pulls = Array.isArray(pulls) ? pulls : [];
    comparisons = comparisons || {};
    auditedComparisons = auditedComparisons || {};
    return branches.map(function (branch) {
      var name = branch && branch.name ? branch.name : "(unknown)";
      var sha = branch && branch.commit && branch.commit.sha ? branch.commit.sha : null;
      if (name === defaultBranch) return { name:name, sha:sha, state:"DEFAULT", comparisonState:"NO_DELTA", ahead:0, behind:0, pr:null, audited:false };
      var pr = pulls.find(function (item) {
        return item && item.head && item.head.ref === name && item.head.repo && item.head.repo.full_name === REPOSITORY;
      }) || null;
      var comparison = pr ? comparisons[pr.number] : auditedComparisons[name];
      var comparisonState = classifyComparison(comparison);
      return {
        name:name, sha:sha, state:pr ? comparisonState : "UNLINKED", comparisonState:comparisonState,
        ahead:comparison && Number.isFinite(comparison.ahead_by) ? comparison.ahead_by : null,
        behind:comparison && Number.isFinite(comparison.behind_by) ? comparison.behind_by : null,
        pr:pr, audited:!pr && Object.prototype.hasOwnProperty.call(auditedComparisons,name)
      };
    }).sort(function (a,b) {
      if (a.state === "DEFAULT") return -1;
      if (b.state === "DEFAULT") return 1;
      return a.name.localeCompare(b.name);
    });
  }
  function summarize(rows, pulls, comparisons) {
    rows = Array.isArray(rows) ? rows : [];
    pulls = Array.isArray(pulls) ? pulls : [];
    comparisons = comparisons || {};
    return {
      branchCount:rows.length, openPrCount:pulls.length,
      linkedBranchCount:rows.filter(function (r) { return !!r.pr; }).length,
      unlinkedBranchCount:rows.filter(function (r) { return r.state === "UNLINKED"; }).length,
      divergedCount:Object.keys(comparisons).filter(function (key) { return classifyComparison(comparisons[key]) === "DIVERGED"; }).length,
      behindCount:rows.filter(function (r) { return r.comparisonState === "BEHIND"; }).length,
      aheadCount:rows.filter(function (r) { return r.comparisonState === "AHEAD"; }).length,
      noDeltaCount:rows.filter(function (r) { return r.comparisonState === "NO_DELTA"; }).length,
      unknownCount:rows.filter(function (r) { return r.comparisonState === "UNKNOWN"; }).length
    };
  }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
      return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[ch];
    });
  }
  function shortSha(value) { return value ? String(value).slice(0,12) : "unknown"; }
  function pill(label,tone) { return '<span class="publishing-pill' + (tone ? " "+tone : "") + '">' + escapeHtml(label) + "</span>"; }
  async function fetchJson(url) {
    var response = await root.fetch(url,{headers:{Accept:"application/vnd.github+json"},cache:"no-store"});
    if (!response.ok) {
      var message = "GitHub API HTTP " + response.status;
      if (response.status === 403) message += " (rate limit or access restriction)";
      throw new Error(message + " for " + url);
    }
    return response.json();
  }
  async function fetchOptionalJson(url) {
    try { return {data:await fetchJson(url),error:null}; }
    catch (error) { return {data:null,error:error.message}; }
  }
  function selectPublicationRuns(sourceResult,siteResult) {
    sourceResult = sourceResult || {};
    siteResult = siteResult || {};
    var sourceRuns = sourceResult.data && Array.isArray(sourceResult.data.workflow_runs) ? sourceResult.data.workflow_runs : [];
    var siteRuns = siteResult.data && Array.isArray(siteResult.data.workflow_runs) ? siteResult.data.workflow_runs : [];
    return [
      {label:"Tribute + Matrix publisher",repository:"termux-monorepo",runs:sourceRuns.slice(0,5),error:sourceResult.error || null},
      {label:"Public website Pages",repository:REPOSITORY,
        runs:siteRuns.filter(function (run) { return /pages build and deployment|deploy github pages/i.test(run.name || ""); }).slice(0,5),
        error:siteResult.error || null}
    ];
  }
  function compareUrl(baseRepo,baseRef,headRepo,headRef) {
    var headSpec = headRepo && headRepo !== baseRepo ? headRepo + ":" + headRef : headRef;
    return API_ROOT + "/repos/" + baseRepo + "/compare/" + encodeURIComponent(baseRef) + "..." + encodeURIComponent(headSpec);
  }
  async function loadSnapshot() {
    var base = API_ROOT + "/repos/" + REPOSITORY;
    var results = await Promise.all([
      fetchJson(base), fetchJson(base + "/branches?per_page=100"), fetchJson(base + "/pulls?state=open&per_page=100"),
      fetchOptionalJson(API_ROOT + "/repos/timerloggedout-spec/termux-monorepo/actions/workflows/tribute-dashboard-deploy.yml/runs?per_page=5"),
      fetchOptionalJson(base + "/actions/runs?per_page=30")
    ]);
    var repository = results[0], branches = results[1], pulls = results[2];
    var publicationRuns = selectPublicationRuns(results[3],results[4]);
    var defaultBranch = repository.default_branch || "main";
    var pagesSourceResult = await fetchOptionalJson(compareUrl(REPOSITORY,PAGES_SOURCE_BRANCH,REPOSITORY,defaultBranch));
    var pagesSourceBranch = branches.find(function (branch) { return branch.name === PAGES_SOURCE_BRANCH; });
    var defaultBranchInfo = branches.find(function (branch) { return branch.name === defaultBranch; });
    var pagesSource = {
      branch:PAGES_SOURCE_BRANCH, defaultBranch:defaultBranch,
      sourceSha:pagesSourceBranch && pagesSourceBranch.commit ? pagesSourceBranch.commit.sha : null,
      targetSha:defaultBranchInfo && defaultBranchInfo.commit ? defaultBranchInfo.commit.sha : null,
      comparison:pagesSourceResult.data || null, error:pagesSourceResult.error || null
    };
    var comparisons = {}, auditedComparisons = {}, selectedPulls = pulls.slice(0,MAX_PR_COMPARISONS);
    await Promise.all(selectedPulls.map(async function (pr) {
      var baseRepo = pr.base && pr.base.repo && pr.base.repo.full_name ? pr.base.repo.full_name : REPOSITORY;
      var headRepo = pr.head && pr.head.repo && pr.head.repo.full_name ? pr.head.repo.full_name : null;
      try { comparisons[pr.number] = await fetchJson(compareUrl(baseRepo,pr.base.ref,headRepo,pr.head.ref)); }
      catch (error) { comparisons[pr.number] = {error:error.message}; }
    }));
    var auditBranches = branches.filter(function (b) { return /ai-elves/i.test(b.name); });
    await Promise.all(auditBranches.map(async function (b) {
      try { auditedComparisons[b.name] = await fetchJson(compareUrl(REPOSITORY,defaultBranch,REPOSITORY,b.name)); }
      catch (error) { auditedComparisons[b.name] = {error:error.message}; }
    }));
    return {branches:branches,pulls:pulls,comparisons:comparisons,auditedComparisons:auditedComparisons,
      publicationRuns:publicationRuns,pagesSource:pagesSource,defaultBranch:defaultBranch,comparedPullCount:selectedPulls.length,compareLimit:MAX_PR_COMPARISONS,checkedAt:new Date().toISOString()};
  }
  function renderSnapshot(snapshot) {
    var rows = buildBranchRows(snapshot.branches,snapshot.pulls,snapshot.comparisons,snapshot.auditedComparisons,snapshot.defaultBranch);
    var summary = summarize(rows,snapshot.pulls,snapshot.comparisons);
    var summaryNode = document.getElementById("publishing-summary");
    var branchNode = document.getElementById("publishing-branches");
    var prNode = document.getElementById("publishing-prs");
    var checkedNode = document.getElementById("publishing-checked");
    summaryNode.innerHTML = [
      ["Branch refs",summary.branchCount],["Open PRs",summary.openPrCount],
      ["PR-linked branches",summary.linkedBranchCount],["Unlinked branches",summary.unlinkedBranchCount],
      ["Diverged PRs",summary.divergedCount]
    ].map(function (item) {
      return '<article class="publishing-stat"><div class="label">' + escapeHtml(item[0]) + '</div><div class="value">' + item[1] + "</div></article>";
    }).join("");
    branchNode.innerHTML = '<div class="publishing-table-wrap"><table class="publishing-table"><thead><tr><th>Branch</th><th>Head SHA</th><th>Disposition</th><th>Compare</th><th>Base</th><th>Pull request</th></tr></thead><tbody>' + rows.map(function (row) {
      var tone = row.state === "AHEAD" ? "ok" : (row.state === "DIVERGED" || row.state === "BEHIND" ? "bad" : "");
      var compareText = row.ahead === null || row.behind === null ? "not compared" : row.ahead + " ahead / " + row.behind + " behind";
      var prLink = row.pr ? '<a href="' + escapeHtml(row.pr.html_url) + '" target="_blank" rel="noopener noreferrer">#' + row.pr.number + " · " + escapeHtml(row.pr.title) + "</a>" : "—";
      var audit = row.audited ? ' <span class="muted">(targeted audit)</span>' : "";
      return "<tr><td><code>" + escapeHtml(row.name) + "</code>" + audit + "</td><td><code>" + escapeHtml(shortSha(row.sha)) + "</code></td><td>" + pill(row.state,tone) + ' <span class="muted">' + escapeHtml(row.comparisonState) + "</span></td><td>" + escapeHtml(compareText) + "</td><td>" + escapeHtml(row.pr ? row.pr.base.ref : (row.audited ? snapshot.defaultBranch : "—")) + "</td><td>" + prLink + "</td></tr>";
    }).join("") + "</tbody></table></div>";
    prNode.innerHTML = snapshot.pulls.length ? '<div class="publishing-table-wrap"><table class="publishing-table"><thead><tr><th>PR</th><th>Title</th><th>Base ref / SHA</th><th>Merge-base SHA</th><th>Head SHA</th><th>Compare</th><th>Updated</th><th>Checks</th></tr></thead><tbody>' + snapshot.pulls.map(function (pr) {
      var cmp = snapshot.comparisons[pr.number], state = classifyComparison(cmp);
      var ahead = cmp && Number.isFinite(cmp.ahead_by) ? cmp.ahead_by : "?";
      var behind = cmp && Number.isFinite(cmp.behind_by) ? cmp.behind_by : "?";
      var baseVersion = (pr.base && pr.base.ref ? pr.base.ref : "unknown") + "@" + shortSha(pr.base && pr.base.sha);
      var mergeBaseSha = cmp && cmp.merge_base_commit && cmp.merge_base_commit.sha ? shortSha(cmp.merge_base_commit.sha) : "unknown";
      return '<tr><td><a href="' + escapeHtml(pr.html_url) + '" target="_blank" rel="noopener noreferrer">#' + pr.number + "</a></td><td>" + escapeHtml(pr.title) + "</td><td><code>" + escapeHtml(baseVersion) + "</code></td><td><code>" + escapeHtml(mergeBaseSha) + "</code></td><td><code>" + escapeHtml(shortSha(pr.head && pr.head.sha)) + "</code></td><td>" + pill(state,state === "DIVERGED" || state === "BEHIND" ? "bad" : "") + ' <span class="muted">' + ahead + " ahead / " + behind + " behind</span></td><td>" + escapeHtml((pr.updated_at || "").slice(0,10)) + '</td><td><a href="' + escapeHtml(pr.html_url + "/checks") + '" target="_blank" rel="noopener noreferrer">Open checks</a></td></tr>';
    }).join("") + "</tbody></table></div>" : '<p class="empty">No open pull requests found for this repository.</p>';
    var pagesSourceNode = document.getElementById("publishing-pages-source");
    var sourceComparison = snapshot.pagesSource.comparison;
    var sourceState = classifyPagesSource(sourceComparison);
    var sourceAhead = sourceComparison && Number.isFinite(sourceComparison.ahead_by) ? sourceComparison.ahead_by : "?";
    var sourceBehind = sourceComparison && Number.isFinite(sourceComparison.behind_by) ? sourceComparison.behind_by : "?";
    var sourceTone = sourceState === "ALIGNED" || sourceState === "FAST_FORWARD_AVAILABLE" ? "ok" : (sourceState === "DIVERGED" || sourceState === "SOURCE_AHEAD" ? "bad" : "");
    var sourceDetail = snapshot.pagesSource.error
      ? "Comparison unavailable: " + snapshot.pagesSource.error
      : (sourceState === "FAST_FORWARD_AVAILABLE"
        ? snapshot.pagesSource.defaultBranch + " is " + sourceAhead + " commits ahead / " + sourceBehind + " behind; a fast-forward is available."
        : (sourceState === "ALIGNED" ? "The Pages source branch matches the default branch." : "Comparison: " + sourceAhead + " ahead / " + sourceBehind + " behind."));
    pagesSourceNode.innerHTML = '<p>' + pill(sourceState,sourceTone) + ' <strong>' + escapeHtml(snapshot.pagesSource.branch) + "</strong> → <strong>" + escapeHtml(snapshot.pagesSource.defaultBranch) + "</strong></p><p>" + escapeHtml(sourceDetail) + '</p><p class="muted">Source SHA <code>' + escapeHtml(shortSha(snapshot.pagesSource.sourceSha)) + '</code> · Target SHA <code>' + escapeHtml(shortSha(snapshot.pagesSource.targetSha)) + '</code> · <a href="https://github.com/' + REPOSITORY + '/compare/' + encodeURIComponent(snapshot.pagesSource.branch) + '...' + encodeURIComponent(snapshot.pagesSource.defaultBranch) + '" target="_blank" rel="noopener noreferrer">Open exact comparison</a></p>';
    var deploymentNode = document.getElementById("publishing-deployments");
    deploymentNode.innerHTML = snapshot.publicationRuns.map(function (group) {
      var heading = "<h3>" + escapeHtml(group.label) + "</h3>";
      if (group.error) return heading + '<p class="muted">Workflow evidence unavailable: ' + escapeHtml(group.error) + "</p>";
      if (!group.runs.length) return heading + '<p class="muted">No matching workflow runs found in the inspected window.</p>';
      return heading + '<div class="publishing-table-wrap"><table class="publishing-table"><thead><tr><th>Run</th><th>Status</th><th>Source SHA</th><th>Event</th><th>Updated</th></tr></thead><tbody>' + group.runs.map(function (run) {
        var status = run.status === "completed" ? (run.conclusion || "completed") : (run.status || "unknown");
        var tone = status === "success" ? "ok" : (status === "failure" || status === "cancelled" ? "bad" : "");
        return '<tr><td><a href="' + escapeHtml(run.html_url || "#") + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(run.name || "Workflow run") + " #" + escapeHtml(run.run_number || run.id) + "</a></td><td>" + pill(status,tone) + "</td><td><code>" + escapeHtml(shortSha(run.head_sha)) + "</code></td><td>" + escapeHtml(run.event || "—") + "</td><td>" + escapeHtml((run.updated_at || run.created_at || "").replace("T"," ").slice(0,16)) + "</td></tr>";
      }).join("") + "</tbody></table></div>";
    }).join("");
    checkedNode.textContent = "Last checked " + new Date(snapshot.checkedAt).toLocaleString() + ". Public API snapshot; no merge or deployment action.";
    var warnings = [snapshot.pulls.length > snapshot.comparedPullCount
      ? "Compared " + snapshot.comparedPullCount + " of " + snapshot.pulls.length + " open PR heads to stay within the public API request budget."
      : "Compared all open PR heads. Unlinked branches are listed without full history comparison, except targeted AI ELVES audit branches."];
    if (snapshot.branches.length === 100) warnings.push("Branch listing reached the 100-ref API page limit; inspect the repository branch list for further refs.");
    if (snapshot.pulls.length === 100) warnings.push("Open PR listing reached the 100-item API page limit.");
    document.getElementById("publishing-warning").textContent = warnings.join(" ");
  }
  async function refresh() {
    var status = document.getElementById("publishing-status");
    var button = document.getElementById("publishing-refresh");
    button.disabled = true;
    status.textContent = "Reading public branch and PR metadata…";
    try {
      renderSnapshot(await loadSnapshot());
      status.textContent = "GitHub API snapshot loaded. Deployment remains a separate proof.";
    } catch (error) {
      status.textContent = "Unable to refresh public GitHub evidence: " + error.message;
    } finally { button.disabled = false; }
  }
  var api = {classifyComparison:classifyComparison,classifyPagesSource:classifyPagesSource,buildBranchRows:buildBranchRows,summarize:summarize,selectPublicationRuns:selectPublicationRuns};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.PublishingReconciliation = api;
  if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded",function () {
    var button = document.getElementById("publishing-refresh");
    if (button) button.addEventListener("click",refresh);
    refresh();
  });
})(typeof window !== "undefined" ? window : null);
