// ListingLens — pipeline tests (offline, deps ∅ except node:test).
// claims ↦ task brief §5: action schemas + pipeline transform under test.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  applyListingPatch,
  generateListing,
  suggestPrice,
} from "../src/pipeline.mjs";
import { createLocalModel } from "../src/model.mjs";

const photo = JSON.parse(
  readFileSync(new URL("../fixtures/sample-photo.json", import.meta.url)),
);
const model = createLocalModel();

test("photo metadata ↦ listing package, end-to-end", () => {
  const pkg = generateListing(photo, model);
  assert.equal(pkg.photoId, "sample-vase-001");
  assert.match(pkg.copy.title, /Stoneware Vase/);
  assert.ok(pkg.copy.description.includes("Seller notes"));
  assert.ok(pkg.copy.bullets.length >= 3);
  assert.equal(pkg.layout.template, "hero-spotlight"); // confidence 0.93 ≥ 0.8
  assert.equal(pkg.layout.accentColor, "#b5542d");
  assert.deepEqual(
    pkg.layout.sections.map((s) => s.kind),
    ["hero", "story", "details", "shipping"],
  );
  assert.equal(pkg.provenance.revision, 1);
  assert.equal(pkg.provenance.generatedFrom, "photo-metadata");
});

test("pricing from comparables: median × condition factor, charm-priced", () => {
  // comps 4900/5400/5800/6200 → median 5600; like-new ×1.0 → charm 5699
  const price = suggestPrice(photo, model.observe(photo));
  assert.equal(price.basis, "comparables");
  assert.equal(price.suggestedCents, 5699);
  assert.ok(price.rangeLowCents < price.suggestedCents);
  assert.ok(price.rangeHighCents > price.suggestedCents);
  assert.match(price.rationale, /Median of 4/);
});

test("pricing without comparables falls back to category baseline", () => {
  const bare = { ...photo, comparables: [] };
  const price = suggestPrice(bare, model.observe(bare));
  assert.equal(price.basis, "category-baseline");
  // ceramics baseline 4200 × 1.0 → charm 4299
  assert.equal(price.suggestedCents, 4299);
});

test("pipeline is deterministic", () => {
  assert.deepEqual(generateListing(photo, model), generateListing(photo, model));
});

test("seller patch ↦ new revision, original untouched", () => {
  const pkg = generateListing(photo, model);
  const revised = applyListingPatch(pkg, {
    title: "Seller Title",
    suggestedPriceCents: 6499,
    template: "story-first",
  });
  assert.equal(revised.copy.title, "Seller Title");
  assert.equal(revised.price.suggestedCents, 6499);
  assert.equal(revised.layout.template, "story-first");
  assert.equal(revised.provenance.revision, 2);
  assert.match(revised.price.rationale, /Seller override/);
  assert.equal(pkg.provenance.revision, 1);
  assert.notEqual(pkg.copy.title, "Seller Title");
});

test("low-confidence multi-item photo ↦ gallery-grid layout", () => {
  const multi = {
    ...photo,
    detectedItems: [
      { label: "linen scarf", category: "textiles", confidence: 0.55, attributes: [] },
      { label: "wool scarf", category: "textiles", confidence: 0.4, attributes: [] },
    ],
  };
  const pkg = generateListing(multi, model);
  assert.equal(pkg.layout.template, "gallery-grid");
});
