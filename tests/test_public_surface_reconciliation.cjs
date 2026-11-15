"use strict";
const assert = require("node:assert/strict");

let api;
try {
  api = require("../apps/tribute-dashboard/publishing.js");
} catch (error) {
  if (error && error.code === "MODULE_NOT_FOUND") {
    console.error("FAIL: publishing.js is not implemented yet");
    process.exit(1);
  }
  throw error;
}

assert.equal(api.classifyComparison({ ahead_by: 0, behind_by: 0 }), "NO_DELTA");
assert.equal(api.classifyComparison({ ahead_by: 4, behind_by: 0 }), "AHEAD");
assert.equal(api.classifyComparison({ ahead_by: 2, behind_by: 3 }), "DIVERGED");
assert.equal(api.classifyComparison({ ahead_by: 0, behind_by: 7 }), "BEHIND");
assert.equal(api.classifyComparison({}), "UNKNOWN");

const branches = [
  { name: "main", commit: { sha: "mainsha" } },
  { name: "promo/teaser-gallery", commit: { sha: "promosha" } },
  { name: "brand/ai-elves-site-identity", commit: { sha: "brandsha" } },
  { name: "legacy-unlinked", commit: { sha: "legacysha" } }
];
const pulls = [{
  number: 51,
  title: "Publish video library",
  html_url: "https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/51",
  base: { ref: "main" },
  head: {
    ref: "promo/teaser-gallery",
    sha: "promosha",
    repo: { full_name: "timerloggedout-spec/timerloggedout-spec.github.io" }
  }
}, {
  number: 52,
  title: "Fork-only branch",
  html_url: "https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/52",
  base: { ref: "main" },
  head: { ref: "fork-only", sha: "forksha", repo: { full_name: "contributor/fork" } }
}];
const comparisons = {
  51: { ahead_by: 4, behind_by: 0, status: "ahead" },
  52: { ahead_by: 2, behind_by: 3, status: "diverged" }
};
const auditedComparisons = {
  "brand/ai-elves-site-identity": { ahead_by: 0, behind_by: 2031, status: "behind" }
};
const rows = api.buildBranchRows(branches, pulls, comparisons, auditedComparisons);

assert.equal(rows.find(row => row.name === "main").state, "DEFAULT");
const promo = rows.find(row => row.name === "promo/teaser-gallery");
assert.equal(promo.state, "AHEAD");
assert.equal(promo.pr.number, 51);
assert.equal(promo.ahead, 4);
assert.equal(promo.behind, 0);

const aiElves = rows.find(row => row.name === "brand/ai-elves-site-identity");
assert.equal(aiElves.state, "UNLINKED");
assert.equal(aiElves.comparisonState, "BEHIND");
assert.equal(aiElves.ahead, 0);
assert.equal(aiElves.behind, 2031);

const legacy = rows.find(row => row.name === "legacy-unlinked");
assert.equal(legacy.state, "UNLINKED");
assert.equal(legacy.comparisonState, "UNKNOWN");

const summary = api.summarize(rows, pulls, comparisons);
assert.equal(summary.branchCount, 4);
assert.equal(summary.openPrCount, 2);
assert.equal(summary.linkedBranchCount, 1);
assert.equal(summary.unlinkedBranchCount, 2);
assert.equal(summary.divergedCount, 1);
assert.equal(summary.behindCount, 1);

console.log("public surface reconciliation contract: PASS");
