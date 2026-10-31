// ListingLens — Agent-Native actions (defineAction ∘ zod ∘ pipeline).
// Brief requirement (BUILD-BRIEF.md): "Give your agent a real job and your
// users an interface to view, edit, and act on its work."
//   generateListing = the agent's job        (photo ↦ listing package)
//   reviseListing   = the user acting on it  (patch ↦ new revision)
// The Agent-Native host mounts the exported `actions` registry; the React
// surface in ListingStudio.jsx calls the same actions.
import { defineAction } from "@agent-native/core";
import {
  ListingPackageSchema,
  PhotoInputSchema,
  ReviseListingInputSchema,
} from "./schemas.mjs";
import { applyListingPatch, generateListing } from "./pipeline.mjs";
import { createModel } from "./model.mjs";

export const generateListingAction = defineAction({
  title: "Generate listing from photo",
  description:
    "Take one indie seller photo (metadata + detector output) and produce " +
    "a complete listing package: listing copy, a pricing suggestion with " +
    "rationale, and a storefront layout. Deterministic local model by " +
    "default — no external services.",
  schema: PhotoInputSchema,
  outputSchema: ListingPackageSchema,
  run: (photo) => generateListing(photo, createModel()),
});

export const reviseListingAction = defineAction({
  title: "Revise listing",
  description:
    "Apply a seller's edits (title, description, bullets, price, layout " +
    "template, accent color) to a generated listing package and return a " +
    "new revision. The agent revalidates the result against the listing " +
    "contract; the prior revision is never mutated.",
  schema: ReviseListingInputSchema,
  outputSchema: ListingPackageSchema,
  run: ({ listing, patch }) => applyListingPatch(listing, patch),
});

export const actions = {
  generateListing: generateListingAction,
  reviseListing: reviseListingAction,
};
