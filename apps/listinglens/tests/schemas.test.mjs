// ListingLens — schema + action contract tests (offline; needs zod +
// @agent-native/core installed per package.json — npm install once).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  ListingPackageSchema,
  PhotoInputSchema,
  ReviseListingInputSchema,
} from "../src/schemas.mjs";
import { actions } from "../src/actions.mjs";
import { generateListing } from "../src/pipeline.mjs";
import { createLocalModel } from "../src/model.mjs";

const photo = JSON.parse(
  readFileSync(new URL("../fixtures/sample-photo.json", import.meta.url)),
);

test("fixture validates against PhotoInputSchema", () => {
  const parsed = PhotoInputSchema.parse(photo);
  assert.equal(parsed.photoId, "sample-vase-001");
});

test("PhotoInputSchema rejects malformed photo metadata", () => {
  assert.equal(PhotoInputSchema.safeParse({ photoId: "x" }).success, false);
  assert.equal(
    PhotoInputSchema.safeParse({ ...photo, dominantColors: ["red"] }).success,
    false,
  );
  assert.equal(
    PhotoInputSchema.safeParse({ ...photo, condition: "minty" }).success,
    false,
  );
});

test("pipeline output validates against ListingPackageSchema", () => {
  const pkg = generateListing(photo, createLocalModel());
  assert.doesNotThrow(() => ListingPackageSchema.parse(pkg));
});

test("generateListing action runs the pipeline end-to-end", async () => {
  const out = await actions.generateListing.run(PhotoInputSchema.parse(photo));
  assert.equal(out.copy.title, "Hand-Thrown Terracotta Glaze Stoneware Vase");
  assert.equal(out.price.basis, "comparables");
  assert.equal(out.provenance.revision, 1);
});

test("reviseListing action applies a patch as a new revision", async () => {
  const pkg = await actions.generateListing.run(PhotoInputSchema.parse(photo));
  const input = ReviseListingInputSchema.parse({
    listing: pkg,
    patch: { title: "Acted Title" },
  });
  const revised = await actions.reviseListing.run(input);
  assert.equal(revised.copy.title, "Acted Title");
  assert.equal(revised.provenance.revision, 2);
});
