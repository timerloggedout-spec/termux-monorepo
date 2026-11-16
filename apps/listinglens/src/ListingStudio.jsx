// ListingLens — React surface: view / edit / act on the agent's work.
// Brief requirement (BUILD-BRIEF.md): users get "an interface to view,
// edit, and act on its work". Every agent-produced field is editable;
// edits route back through the reviseListing action (here: the onRevise
// callback injected by the host, wired to actions.reviseListing).
import React, { useState } from "react";

const money = (cents) =>
  `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

export function ListingStudio({ photo, initialPackage, onRegenerate, onRevise }) {
  const [pkg, setPkg] = useState(initialPackage);
  const [draft, setDraft] = useState({});
  const dirty = Object.keys(draft).length > 0;

  const field = (key, value) => (
    <input
      value={draft[key] ?? value}
      onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
      style={{ width: "100%" }}
    />
  );

  const applyEdits = () => {
    const patch = {};
    if (draft.title) patch.title = draft.title;
    if (draft.description) patch.description = draft.description;
    if (draft.priceDollars) {
      patch.suggestedPriceCents = Math.round(
        Number.parseFloat(draft.priceDollars) * 100,
      );
    }
    if (draft.template) patch.template = draft.template;
    if (draft.accentColor) patch.accentColor = draft.accentColor;
    const revised = onRevise(pkg, patch);
    setPkg(revised);
    setDraft({});
  };

  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 880, margin: "0 auto" }}>
      <h1>ListingLens — seller studio</h1>
      <section style={{ display: "flex", gap: 16 }}>
        <img
          src={photo.imageSrc}
          alt={photo.fileName}
          style={{ width: 320, borderRadius: 8 }}
        />
        <div>
          <p>
            Photo <code>{photo.fileName}</code> · {photo.widthPx}×
            {photo.heightPx} · condition {photo.condition}
          </p>
          <button onClick={() => setPkg(onRegenerate(photo))}>
            ↻ Regenerate listing (agent)
          </button>
          <p>
            Revision {pkg.provenance.revision} · model {pkg.provenance.model}
          </p>
        </div>
      </section>

      <section
        style={{
          borderTop: `6px solid ${pkg.layout.accentColor}`,
          paddingTop: 12,
        }}
      >
        <h2>Listing copy (editable)</h2>
        {field("title", pkg.copy.title)}
        <textarea
          rows={4}
          style={{ width: "100%" }}
          value={draft.description ?? pkg.copy.description}
          onChange={(e) =>
            setDraft((d) => ({ ...d, description: e.target.value }))
          }
        />
        <ul>
          {pkg.copy.bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>

        <h2>Pricing (agent suggestion, editable)</h2>
        <p>
          Suggested <strong>{money(pkg.price.suggestedCents)}</strong> · range{" "}
          {money(pkg.price.rangeLowCents)}–{money(pkg.price.rangeHighCents)} ·{" "}
          basis {pkg.price.basis}
        </p>
        <p>
          <em>{pkg.price.rationale}</em>
        </p>
        {field("priceDollars", (pkg.price.suggestedCents / 100).toFixed(2))}

        <h2>Storefront layout (editable)</h2>
        <label>
          Template{" "}
          <select
            value={draft.template ?? pkg.layout.template}
            onChange={(e) =>
              setDraft((d) => ({ ...d, template: e.target.value }))
            }
          >
            <option value="hero-spotlight">hero-spotlight</option>
            <option value="gallery-grid">gallery-grid</option>
            <option value="story-first">story-first</option>
          </select>
        </label>{" "}
        <label>
          Accent {field("accentColor", pkg.layout.accentColor)}
        </label>
        {pkg.layout.sections.map((s) => (
          <article key={s.kind}>
            <h3>{s.heading}</h3>
            <p>{s.body}</p>
          </article>
        ))}

        <button disabled={!dirty} onClick={applyEdits}>
          ✓ Apply edits (act via reviseListing)
        </button>
      </section>
    </main>
  );
}

export default ListingStudio;
