// ListingLens — zod contracts. Single source of truth for action I/O.
// claims ↦ BUILD-BRIEF.md (listinglens repo, frozen 2026-10-30): agent job =
// photo ↦ listing copy + pricing + storefront layout; user view/edit/act.
import { z } from "zod";

export const DetectedItemSchema = z.object({
  label: z.string().min(1),
  category: z.string().min(1),
  confidence: z.number().min(0).max(1),
  attributes: z.array(z.string()).default([]),
});

export const ComparableSchema = z.object({
  title: z.string().min(1),
  soldPriceCents: z.number().int().positive(),
});

// Photo-in: metadata about one seller photo. The photo bytes themselves ride
// the host's attachment channel; the pipeline reasons over this metadata so
// the whole demo runs offline + deterministically.
export const PhotoInputSchema = z.object({
  photoId: z.string().min(1),
  fileName: z.string().min(1),
  widthPx: z.number().int().positive(),
  heightPx: z.number().int().positive(),
  dominantColors: z.array(z.string().regex(/^#[0-9a-fA-F]{6}$/)).min(1),
  detectedItems: z.array(DetectedItemSchema).min(1),
  condition: z.enum(["like-new", "good", "fair"]),
  sellerNotes: z.string().default(""),
  comparables: z.array(ComparableSchema).default([]),
});

export const PriceSuggestionSchema = z.object({
  currency: z.literal("USD"),
  suggestedCents: z.number().int().positive(),
  rangeLowCents: z.number().int().positive(),
  rangeHighCents: z.number().int().positive(),
  basis: z.enum(["comparables", "category-baseline"]),
  rationale: z.string().min(1),
});

export const ListingCopySchema = z.object({
  title: z.string().min(1).max(140),
  description: z.string().min(1),
  bullets: z.array(z.string().min(1)).min(1),
  tags: z.array(z.string()).default([]),
});

export const LayoutSectionSchema = z.object({
  kind: z.enum(["hero", "story", "details", "care", "shipping"]),
  heading: z.string().min(1),
  body: z.string().default(""),
});

export const StorefrontLayoutSchema = z.object({
  template: z.enum(["hero-spotlight", "gallery-grid", "story-first"]),
  accentColor: z.string().regex(/^#[0-9a-fA-F]{6}$/),
  sections: z.array(LayoutSectionSchema).min(2),
});

// Listing-out: the full package the surface renders + the seller edits.
export const ListingPackageSchema = z.object({
  photoId: z.string().min(1),
  copy: ListingCopySchema,
  price: PriceSuggestionSchema,
  layout: StorefrontLayoutSchema,
  provenance: z.object({
    model: z.string().min(1),
    generatedFrom: z.literal("photo-metadata"),
    revision: z.number().int().min(1),
  }),
});

// Edit/act path: the seller patches any rendered field; the agent revalidates
// + returns a new revision (never mutates the prior package).
export const ListingPatchSchema = z.object({
  title: z.string().min(1).max(140).optional(),
  description: z.string().min(1).optional(),
  bullets: z.array(z.string().min(1)).optional(),
  suggestedPriceCents: z.number().int().positive().optional(),
  template: z.enum(["hero-spotlight", "gallery-grid", "story-first"]).optional(),
  accentColor: z.string().regex(/^#[0-9a-fA-F]{6}$/).optional(),
});

export const ReviseListingInputSchema = z.object({
  listing: ListingPackageSchema,
  patch: ListingPatchSchema,
});
