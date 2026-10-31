// ListingLens — pipeline: photo metadata ↦ listing package.
// Pure + deterministic (deps ∅): copy draft ∘ pricing ∘ layout, then the
// seller edit/act transform. Framework wiring lives in actions.mjs; the
// surface renders ListingPackage and patches it via applyListingPatch.

const CONDITION_FACTOR = { "like-new": 1.0, good: 0.9, fair: 0.75 };
const CONDITION_PHRASE = {
  "like-new": "like new, carefully kept",
  good: "gently used, in good working order",
  fair: "pre-loved, with honest wear",
};
// Fallback when the seller supplies ∅ comparables (cents, by category).
const CATEGORY_BASELINE_CENTS = {
  ceramics: 4200,
  textiles: 3500,
  woodwork: 6800,
  jewelry: 8500,
  art: 9000,
  default: 4000,
};

const cents = (n) => Math.max(100, Math.round(n));
// Charm pricing: round to the nearest x.99 within the dollar.
const charm = (n) => Math.max(199, Math.floor(n / 100) * 100 + 99);
const median = (xs) => {
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};
const quartile = (xs, q) => {
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.floor(q * s.length))];
};
const titleCase = (s) => s.replace(/\b\w/g, (c) => c.toUpperCase());

export function suggestPrice(photo, observations) {
  const factor = CONDITION_FACTOR[photo.condition];
  const prices = (photo.comparables ?? []).map((c) => c.soldPriceCents);
  if (prices.length >= 2) {
    const med = median(prices);
    return {
      currency: "USD",
      suggestedCents: charm(med * factor),
      rangeLowCents: cents(quartile(prices, 0.25) * factor),
      rangeHighCents: cents(quartile(prices, 0.75) * factor),
      basis: "comparables",
      rationale:
        `Median of ${prices.length} comparable sold listings, ` +
        `× ${factor} condition factor (${photo.condition}).`,
    };
  }
  const base =
    CATEGORY_BASELINE_CENTS[observations.category] ??
    CATEGORY_BASELINE_CENTS.default;
  return {
    currency: "USD",
    suggestedCents: charm(base * factor),
    rangeLowCents: cents(base * factor * 0.8),
    rangeHighCents: cents(base * factor * 1.2),
    basis: "category-baseline",
    rationale:
      `No comparables supplied — ${observations.category} category baseline ` +
      `× ${factor} condition factor (${photo.condition}). Add sold comps ` +
      `for a market-priced suggestion.`,
  };
}

export function draftCopy(photo, observations) {
  const attrs = observations.attributes;
  // Title lead = up to 2 attributes whose words aren't already in the label
  // (avoids "Stoneware Stoneware Vase").
  const labelWords = new Set(observations.heroLabel.toLowerCase().split(/\s+/));
  const fresh = attrs.filter((a) =>
    a.toLowerCase().split(/\s+/).some((w) => !labelWords.has(w)),
  );
  const lead = fresh.length ? `${fresh.slice(0, 2).join(" ")} ` : "";
  const title = titleCase(
    `${lead}${observations.heroLabel}`.trim().slice(0, 140),
  );
  const conditionPhrase = CONDITION_PHRASE[photo.condition];
  const notes = observations.sellerNotes
    ? ` Seller notes: ${observations.sellerNotes}`
    : "";
  const description =
    `${title} — a one-of-a-kind piece from an independent maker. ` +
    `Condition: ${conditionPhrase}. Photographed as-is; what you see is ` +
    `the exact item that ships.${notes}`;
  const bullets = [
    `Condition: ${conditionPhrase}`,
    ...attrs.map((a) => titleCase(a)),
    `Palette: ${observations.palette.join(", ")}`,
    "Ships from the maker's studio, packed by hand",
  ];
  const tags = [
    observations.category,
    observations.heroLabel.split(" ")[0].toLowerCase(),
    "handmade",
    "indie-seller",
  ];
  return { title, description, bullets, tags };
}

export function chooseLayout(photo, observations) {
  const template =
    observations.confidence >= 0.8
      ? "hero-spotlight"
      : photo.detectedItems.length > 1
        ? "gallery-grid"
        : "story-first";
  const sections = [
    {
      kind: "hero",
      heading: observations.heroLabel,
      body: "Lead with the strongest photo; price + buy action stay pinned.",
    },
    {
      kind: "story",
      heading: "From the maker's bench",
      body:
        observations.sellerNotes ||
        "How this piece was made, in the seller's words.",
    },
    {
      kind: "details",
      heading: "Details & condition",
      body: `Condition: ${photo.condition}. Attributes: ${
        observations.attributes.join(", ") || "see photos"
      }.`,
    },
    {
      kind: "shipping",
      heading: "Shipping & returns",
      body: "Packed by hand; tracked shipping; 14-day returns.",
    },
  ];
  return { template, accentColor: photo.dominantColors[0], sections };
}

// photo metadata ↦ listing package (the agent's job, end-to-end).
export function generateListing(photo, model) {
  const observations = model.observe(photo);
  return {
    photoId: photo.photoId,
    copy: draftCopy(photo, observations),
    price: suggestPrice(photo, observations),
    layout: chooseLayout(photo, observations),
    provenance: {
      model: model.name,
      generatedFrom: "photo-metadata",
      revision: 1,
    },
  };
}

// Seller edit/act: patch ↦ new revision. Price edits keep the suggestion's
// range + basis visible so the seller sees what they overrode.
export function applyListingPatch(listing, patch) {
  const next = structuredClone(listing);
  if (patch.title !== undefined) next.copy.title = patch.title;
  if (patch.description !== undefined) next.copy.description = patch.description;
  if (patch.bullets !== undefined) next.copy.bullets = patch.bullets;
  if (patch.suggestedPriceCents !== undefined) {
    next.price = {
      ...next.price,
      suggestedCents: patch.suggestedPriceCents,
      rationale: `${next.price.rationale} Seller override applied at revision ${
        listing.provenance.revision + 1
      }.`,
    };
  }
  if (patch.template !== undefined) next.layout.template = patch.template;
  if (patch.accentColor !== undefined) next.layout.accentColor = patch.accentColor;
  next.provenance = {
    ...next.provenance,
    revision: listing.provenance.revision + 1,
  };
  return next;
}
