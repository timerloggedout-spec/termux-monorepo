// ListingLens — offline end-to-end demo (checkpoint-quality proof).
// sample photo fixture ↦ generateListing ↦ editable package ↦ seller patch
// ↦ revision 2. Deps: ∅ (pipeline + local model only). Run: npm run demo
import { readFileSync } from "node:fs";
import { generateListing, applyListingPatch } from "../src/pipeline.mjs";
import { createModel } from "../src/model.mjs";

const photo = JSON.parse(
  readFileSync(new URL("../fixtures/sample-photo.json", import.meta.url)),
);

const pkg = generateListing(photo, createModel());
console.log("== ListingLens demo: photo ↦ listing ==");
console.log(`photo        ${photo.fileName} (${photo.photoId})`);
console.log(`title        ${pkg.copy.title}`);
console.log(`description  ${pkg.copy.description}`);
console.log(`bullets      ${pkg.copy.bullets.join(" | ")}`);
console.log(
  `price        $${(pkg.price.suggestedCents / 100).toFixed(2)} ` +
    `(range $${(pkg.price.rangeLowCents / 100).toFixed(2)}–$${(
      pkg.price.rangeHighCents / 100
    ).toFixed(2)}, basis ${pkg.price.basis})`,
);
console.log(`price why    ${pkg.price.rationale}`);
console.log(
  `layout       ${pkg.layout.template} · accent ${pkg.layout.accentColor} · ` +
    `sections ${pkg.layout.sections.map((s) => s.kind).join(" → ")}`,
);
console.log(`provenance   ${pkg.provenance.model} · rev ${pkg.provenance.revision}`);

const revised = applyListingPatch(pkg, {
  title: "Terracotta Stoneware Vase — Small Batch, Signed",
  suggestedPriceCents: 6499,
});
console.log("\n== seller edit/act ↦ revision ==");
console.log(`title        ${revised.copy.title}`);
console.log(`price        $${(revised.price.suggestedCents / 100).toFixed(2)}`);
console.log(`provenance   rev ${revised.provenance.revision}`);
console.log("\nDEMO OK — end-to-end, offline, deterministic.");
