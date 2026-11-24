"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const app = "apps/tribute-dashboard";
const viewFeed = JSON.parse(fs.readFileSync(app + "/data/experiment-view-feed.json", "utf8"));
const doeFeed = JSON.parse(fs.readFileSync(app + "/data/doe-feed.json", "utf8"));
viewFeed.methods = [viewFeed.methods.find(x => x.id === "RFP-V13"), ...viewFeed.methods.filter(x => x.id !== "RFP-V13")];
viewFeed.campaigns = [
  {campaign_id:"apk-1-parallel-versioning",method_id:"RFP-V13",state:"blocked"},
  {campaign_id:"synthetic-v1",method_id:"RFP-V1",state:"queued",runs:1}
];
viewFeed.workstreams = [
  {id:"valid-stream",method_id:"RFP-V13",state:"executing",start:"2026-11-20",end:"2026-11-22"},
  {id:"reversed-stream",method_id:"RFP-V13",state:"executing",start:"2026-11-23",end:"2026-11-21"}
];

class Element {
  constructor() { this.innerHTML = ""; this.textContent = ""; this.value = ""; this.listeners = {}; this.attributes = {}; this.children = []; }
  replaceChildren(...children) { this.children = children; this.value = children[0]?.value || ""; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
  change(value) { this.value = value; this.listeners.change({target:this}); }
}
const ids = ["rv-release","rv-method","rv-view","rv-method-summary","rv-output"];
const elements = Object.fromEntries(ids.map(id => [id,new Element()]));
const context = {
  document: {getElementById:id => elements[id], createElement:() => new Element()},
  fetch: async url => ({ok:true,json:async () => url.includes("doe-feed.json") ? doeFeed : viewFeed}),
  console, Map, Date, Math, Number, String, Array, Object, Promise
};
vm.runInNewContext(fs.readFileSync(app + "/experiment-views.js","utf8"), context);
(async () => {
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(elements["rv-method"].value,"RFP-V1","initial control follows state.method even when catalogue order differs");
  assert.match(elements["rv-method-summary"].innerHTML,/RFP baseline/);

  elements["rv-method"].change("RFP-V13");
  elements["rv-view"].change("kanban");
  assert.match(elements["rv-output"].innerHTML,/apk-1-parallel-versioning/,"view-feed campaign survives the DoE merge");
  assert.match(elements["rv-output"].innerHTML,/4 recorded runs/,"DoE evidence fills fields absent from the view-feed record");

  elements["rv-view"].change("adaptive");
  assert.match(elements["rv-output"].innerHTML,/blocked: <b>1<\/b>/);
  assert.doesNotMatch(elements["rv-output"].innerHTML,/queued: <b>1<\/b>/,"adaptive counts apply the selected method filter");

  elements["rv-view"].change("gantt");
  assert.match(elements["rv-output"].innerHTML,/Excluded 1 workstream interval/);
  assert.match(elements["rv-output"].innerHTML,/valid-stream/);
  assert.doesNotMatch(elements["rv-output"].innerHTML,/reversed-stream/);

  elements["rv-method"].change("RFP-V1");
  elements["rv-view"].change("adaptive");
  assert.match(elements["rv-output"].innerHTML,/queued: <b>1<\/b>/);
  assert.doesNotMatch(elements["rv-output"].innerHTML,/blocked: <b>1<\/b>/);
  process.stdout.write("Published-view interaction tests passed.\n");
})().catch(error => { console.error(error); process.exitCode = 1; });
