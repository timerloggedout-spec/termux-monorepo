import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync(new URL("../apps/tribute-dashboard/owner-records.html", import.meta.url), "utf8");
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
  .map(match => match[1]).find(source => source.includes("function validateEnvelope"));
assert.ok(script, "Owner Records inline runtime script exists");

const canonical = JSON.parse(readFileSync(new URL("../ops/owner-records/index.json", import.meta.url), "utf8"));
const manifest = JSON.parse(readFileSync(new URL("../apps/tribute-dashboard/version-manifest.json", import.meta.url), "utf8"));
manifest.source_sha = manifest.source_sha || "runtime-test-source-sha";
manifest.version = manifest.version || "1.0.1+runtime-test";
manifest.channel = manifest.channel || "preview";
const clone = value => JSON.parse(JSON.stringify(value));
const tick = () => new Promise(resolve => setTimeout(resolve, 0));

function harness(initialEnvelope = canonical) {
  const elements = new Map();
  const documentHandlers = new Map();
  let currentEnvelope = clone(initialEnvelope);
  let failFetch = false;
  const get = id => {
    if (!elements.has(id)) {
      const handlers = new Map();
      elements.set(id, {
        id, dataset: {}, innerHTML: "", textContent: "", hidden: false, value: "",
        addEventListener(type, callback) { handlers.set(type, callback); },
        dispatch(type, event = {}) { const callback = handlers.get(type); if (callback) callback(event); },
        replaceChildren() { this.innerHTML = ""; this.textContent = ""; }
      });
    }
    return elements.get(id);
  };
  const document = {
    visibilityState: "visible",
    getElementById: get,
    addEventListener(type, callback) { documentHandlers.set(type, callback); }
  };
  const window = { location: { search: "" }, setInterval() { return 1; } };
  const fetch = async url => {
    if (failFetch) return { ok: false, status: 503, json: async () => ({}) };
    if (url === "./version-manifest.json") return { ok: true, json: async () => clone(manifest) };
    if (String(url).startsWith("./owner-records.json?t=")) return { ok: true, json: async () => clone(currentEnvelope) };
    if (String(url).startsWith("https://raw.githubusercontent.com/")) return { ok: true, json: async () => clone(currentEnvelope) };
    throw new Error("Unexpected fetch URL: " + url);
  };
  vm.runInNewContext(script, {
    document, window, fetch, URLSearchParams, console,
    CK: { bars: () => "<svg></svg>", stampState: () => "fresh" }
  }, { filename: "owner-records.html" });
  return {
    get,
    async ready() { await tick(); await tick(); },
    setEnvelope(value) { currentEnvelope = clone(value); },
    setFetchFailure(value) { failFetch = value; },
    async refresh() {
      const callback = documentHandlers.get("visibilitychange");
      assert.ok(callback);
      callback();
      await tick();
      await tick();
    }
  };
}

test("loads only validated metadata and verifies build identity", async () => {
  const app = harness();
  await app.ready();
  assert.match(app.get("results-count").textContent, /Showing \d+ of \d+ records/);
  assert.equal(app.get("build-identity").dataset.state, "VERIFIED");
  assert.doesNotMatch(app.get("classes").innerHTML, /ciphertext body contents/i);
});

test("searches and combines class and state filters, then clears them", async () => {
  const app = harness();
  await app.ready();
  const cls = canonical.classes.find(item => item.records.length > 0);
  assert.ok(cls);
  const record = cls.records[0];
  app.get("record-search").value = record.id;
  app.get("record-search").dispatch("input", { target: app.get("record-search") });
  assert.match(app.get("results-count").textContent, /Showing 1 of/);
  assert.match(app.get("classes").innerHTML, new RegExp(record.id));
  app.get("class-filter").value = cls.class;
  app.get("class-filter").dispatch("change", { target: app.get("class-filter") });
  app.get("state-filter").value = record.state;
  app.get("state-filter").dispatch("change", { target: app.get("state-filter") });
  assert.match(app.get("results-count").textContent, /across 1 class/);
  app.get("clear-filters").dispatch("click");
  assert.match(app.get("results-count").textContent, /of \d+ records across 5 classes/);
});

test("rejects an invalid initial envelope without rendering unvalidated data", async () => {
  const invalid = clone(canonical);
  invalid.unrecognized = true;
  const app = harness(invalid);
  await app.ready();
  assert.equal(app.get("freshness").dataset.state, "ERROR");
  assert.equal(app.get("generated").textContent, "No unvalidated data was rendered.");
  assert.equal(app.get("classes").innerHTML, "");
  assert.equal(app.get("results-count").textContent, "Record search unavailable.");
  assert.match(app.get("load-error").textContent, /Envelope rejected/);
});

test("retains the last validated view when a refresh fails", async () => {
  const app = harness();
  await app.ready();
  const before = app.get("results-count").textContent;
  const htmlBefore = app.get("classes").innerHTML;
  app.setFetchFailure(true);
  await app.refresh();
  assert.equal(app.get("results-count").textContent, before);
  assert.equal(app.get("classes").innerHTML, htmlBefore);
  assert.match(app.get("freshness").textContent, /showing last validated envelope/i);
  assert.equal(app.get("load-error").hidden, false);
});
