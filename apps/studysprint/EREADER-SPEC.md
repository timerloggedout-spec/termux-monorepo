# eReader scoping spec — the EPUB edition (issue #4457)

**Status: SCOPING — for the D1 seat's ruling. No build in this
document's item; the build files as a follow-on under the ruling.**

Owner rider 3 (2026-11-03): eReader joins the surface family,
scoped as an **EPUB edition generated from the reader sections**,
joining the export family (.apkg · Obsidian · EPUB) rather than
forking a fifth app. This spec answers the four scoping
questions from the code of record.

## 1. The decision: EPUB-as-export (recommended)

**Recommendation: export-family membership — the D1 seat's
recommendation of record, confirmed by the code shape.**

The export family today is two generators in `study_sr.py` —
`export_apkg(cards, out_path, deck_name)` and
`export_obsidian_vault(cards, vault_dir, states)` — surfaced
through the CLI and the TUI Export tab. An EPUB generator is the
same kind of object: a pure function from course state to a
file, no runtime, no session, no state of its own. It has
nothing that a version line would attach to.

What the choice implies:

- **Versioning:** no new version line. The EPUB is generated
  from a surface's state and rides that surface's version — a
  `0.1.3` TUI exports the `0.1.3` reader edition. The EPUB's
  internal metadata (`dc:identifier`, `dcterms:modified`) stamps
  the generating surface + version.
- **Parity matrix:** no new surface column. The matrix gains the
  EPUB as an export-family row — "reader edition (EPUB)" —
  bound wherever the export family is bound (core + TUI today),
  with the web cell stated as it honestly is (see §4).
- **Release set:** one new asset, stable-named
  `studysprint-reader.epub` (the APK's stable-name convention),
  attached to the **TUI release** of the same version — the TUI
  is the export family's home surface. The release-cut workflow
  (#4455 seam ③) gains the EPUB as a second asset in its `tui`
  cut; that extension is part of the follow-on build, not this
  spec.

The rejected alternative — a fifth surface with its own line —
would version a file format as if it were an app: its own
releases, its own parity column, and a sync surface in two
repos, for an artifact that is regenerated from state on every
export. Nothing in the reader pipeline needs it.

## 2. Generation path: sections → chapters

**Source structures (of record):**

- `study_reader.Section` — `{section_id, title, content,
  chapter, tokens}`. The EPUB's unit of content is the Section;
  `content` is the authored reading text (per-topic readings,
  #4230) plus any appended check-yourself material the state
  builder already composed.
- Surface state already carries the sections in reading order:
  core `build_state()["sections"]`, web
  `state["reader"]["sections"]` (`web/build_data.py`). The
  generator consumes the same list every surface renders — no
  new content path.

**Mapping:**

- Sections group by `Section.chapter` ("Week N") preserving
  state order → **one XHTML document per chapter**, sections as
  `<h2 id="{section_id}">` inside it. One file per chapter (not
  per section) keeps individual documents small — e-ink
  readers paginate and load per-document, and chapter-sized
  files are the kind granularity.
- Spine order = chapter order = state order. Front matter: a
  title page (course title, generating surface + version, the
  sample-course disclosure where the state carries it). Back
  matter: the Terms & index chapter (§3).
- Package: EPUB 3 container (stdlib `zipfile` — **no new
  dependency**; the export family today adds only genanki, for
  .apkg) with `mimetype` stored-first, `container.xml`, the
  OPF manifest/spine, an EPUB 3 nav document **and** an NCX
  (older e-ink readers still navigate by NCX; shipping both is
  the compatibility-maximal choice and costs one generated
  file).

**Generator home:** `study_sr.py`, beside the other two exports
— `export_epub(sections, out_path, *, title, surface_version)`.
Family cohesion wins over source-module adjacency: a reader of
the export family finds all three generators in one place, and
the signature states its different input (sections, not cards)
plainly.

## 3. Term-bank cross-refs — the honest answer

The term bank (`study_pipeline.py`, the reader's lookup hook)
resolves a term to `{term, definition, index_refs, card_ready}`
where **`index_refs` are page numbers in the source document**
(they arrive as `index_pages` from the ingested text's index).

**Do they survive into the EPUB? As data, yes. As links, no —
and the spec says so rather than faking targets.**

A reflowable EPUB has no pages. An `index_refs` entry pointing
at "page 42" of the source has no anchor in the edition, and
inventing one (a guessed section) would fabricate provenance —
the family's standing sin. The design:

- **Body text:** terms render as plain text. No dead links, no
  fake anchors.
- **Terms & index chapter (back matter):** every banked term,
  alphabetized, with its definition and its source pages cited
  as text — "source pp. 42, 57". Provenance survives verbatim;
  a reader holding the source text can use it exactly as a
  print index is used.
- **Stated extension (not in the build):** in-edition links from
  a term's first occurrence in each chapter to its Terms entry
  are reflow-safe (EPUB-internal hrefs) and can land later
  without changing the edition's structure. The build ships
  without them; the spec records the option so the follow-on
  ruling can take it or leave it explicitly.

## 4. Export-family wiring (entry points)

- **Core / CLI:** `export_epub` joins the export calls the CLI
  already makes; `demo.py`'s export leg gains the EPUB beside
  the .apkg so the demo run produces the full family.
- **TUI:** the Export tab (today: "Export Anki .apkg" ·
  "Export Obsidian vault", `tui.py`) gains **"Export EPUB
  reader edition"** — same receipt pattern (path + counts: chapters,
  sections, terms indexed).
- **Web / APK:** stated honestly — **not in the build.** The
  existing exports are TUI-only in the parity matrix today (SR
  exports never crossed to the web bundle), and the EPUB
  follows the family: core + TUI bound, web cell marked absent
  in the matrix until a later iteration crosses exports over.
  Scoping it in now would smuggle a second build (client-side
  EPUB generation in the bundle) inside this one.

## 5. E-ink constraints check

- **Reflowable:** no fixed-layout metadata anywhere; XHTML
  flows at the reader's font and size. ✓
- **∅ JS dependency:** no script elements, no scripted
  navigation; nav + NCX are declarative. (EPUB 3 permits
  scripting; this edition ships none.) ✓
- **Styling:** one small embedded stylesheet — serif default,
  no embedded fonts, no color-dependent meaning, no fixed-pixel
  containers, no floats. Renders identically on grayscale
  e-ink. ✓
- **Media:** no images in this edition (sections are text);
  nothing to downscale or posterize. ✓
- **Weight:** the bundled course's edition is tens of KB —
  trivially within e-ink storage/transfer norms. ✓

## 6. Evidence a build ships (defined now, owed then)

1. **A generated EPUB** from the bundled course, in-tree under
   `evidence/` beside the other surfaces' evidence.
2. **EpubCheck validation output** — the edition passes the
   canonical EPUB checker with zero errors (the checker runs
   in Actions, where a JDK is already provisioned for the APK
   build; the report ships with the evidence).
3. **A rendered capture** — one chapter rendered by a desktop
   EPUB renderer (calibre's headless viewer in the same Actions
   job), proving the XHTML/CSS renders as a book page, not
   merely validates as a zip.
4. **Suite pins** — tests asserting the container shape
   (mimetype first + stored), the OPF spine order against the
   section order, the chapter grouping, the Terms chapter's
   presence with source-page citations, and the absence of any
   `<script` in the package.

## Ruling requested

D1 rules: (a) EPUB-as-export as recommended, or the fifth-line
alternative against this spec's account of its costs; (b) the
Terms-chapter treatment (data-yes/links-no, extension noted);
(c) the release placement (second asset on the TUI release).
The build then files as a follow-on item under the ruling,
claim-at-pickup as usual.
