// ListingLens — replaceable model interface.
//
// The pipeline never calls a model directly; it calls this interface.
// Default = deterministic local fallback (∅ API keys, ∅ network, ∅ secrets),
// so the demo + tests run offline end-to-end. A hosted vision/LLM model
// plugs in by returning the same shapes — swap point = createModel().
//   claims ↦ task brief §4: "any model call sits behind a replaceable
//   interface with a deterministic local fallback".

export function createLocalModel() {
  return {
    name: "listinglens-local/1 (deterministic fallback)",
    // Photo metadata ⇒ observations the copy step writes from. The local
    // fallback trusts the detector output carried in the photo metadata;
    // a hosted vision model would produce these from pixels instead.
    observe(photo) {
      const hero = [...photo.detectedItems].sort(
        (a, b) => b.confidence - a.confidence,
      )[0];
      return {
        heroLabel: hero.label,
        category: hero.category,
        confidence: hero.confidence,
        attributes: hero.attributes ?? [],
        condition: photo.condition,
        palette: photo.dominantColors,
        sellerNotes: photo.sellerNotes ?? "",
      };
    },
  };
}

// Extension point: createHostedModel({ provider, ... }) => same interface.
// Deliberately unimplemented in this checkpoint — no keys are read anywhere
// in this app, and the local fallback covers the demo path.
export function createModel() {
  return createLocalModel();
}
