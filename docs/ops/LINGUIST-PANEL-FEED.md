# Linguist Panel Feed — Contract + Canonical Registry

Schema: `linguist-panel-feed/v1`
Collector: `scripts/linguist/linguist_panel_feed.py`
Feed: `apps/help-wanted-dashboard/data/linguist-panel-feed.json`
Refresh: `.github/workflows/linguist-panel-feed-collect.yml` (dispatch +
weekly Tue 06:53 UTC + pushes touching a source path; refresh lands by
PR, never direct commit — same pattern as the Oracle Panel feed).
Consumer: Linguist admin panel (visualization lane; this contract is
the handoff surface).

## Honesty contract

- The panel shows only what the record holds. A value the record does
  not hold renders as absent / `null`, never synthesized.
- Mapping data is **imported or parsed from the sources of record at
  collection time**, never transcribed from prose claims.
- `round_trip_verified` is computed by running the actual codecs at
  collection time (differential discipline — 2026-10-20 codec-revert
  lesson: repo tests passing does not prove semantics unchanged).
  Lossy-by-design entries say so in `note`; they are never silently
  presented as reversible.
- Count-only families say `entries_included: false` and why.

## Canonical registry — one source of truth per family

On conflict, the **runtime code wins** over prose dictionaries, and a
structured record wins over a proposal document.

| Family id | Kind | Canonical source | Direction |
|---|---|---|---|
| `cedrlang-symbol` | symbol-map | `workspace/compression_sandbox/cedrlang/cedrlang.py` (`SYMBOL_MAP`) | bidirectional (decode lossy for duplicate symbols) |
| `cedrlang-compression` | word-map | same (`MAPPINGS`, via `compile_doc`/`decompile_doc`) | bidirectional |
| `cedrlang-stopwords` | elision-list | same (`STOPWORDS`) | encode-only, lossy |
| `phase-codec-leet-chars` | char-map | `workspace/compression_sandbox/cedrlang/phase_codec.py` (`LEET_MAP`) | encode-only |
| `phase-codec-canonical-tokens` | token-variants | same (`CANONICAL_TOKENS`, `VARIANT_INDEX`) | bidirectional |
| `grimoire-char-variants` | char-map (prose) | `harmony_hub/config/grimoire/1337_D1CT10N4RY.md` | encode-only |
| `grimoire-core-castings` | glossary | same | decode-only |
| `grimoire-protocol-terms` | glossary | same; canonical-token check vs `cedrlang.py` | bidirectional |
| `grimoire-orchestra-crosswalk` | crosswalk | `harmony_hub/config/GRIMOIRE_DICTIONARY.md`; check vs `cedrlang.py` | bidirectional |
| `cedar-pointer-commands` | hash-pointer | `workspace/compression_sandbox/cedrlang/cid.py` (`ALL_COMMANDS`, `CedarIndex`) | bidirectional (runtime registry) |
| `nomenclature-concepts` | concept-registry | `docs/proposals/active/notation-sets/nomenclature-matrix/seed.json` | definitional |
| `nomenclature-labels` | label-registry | same | definitional |
| `nomenclature-mappings` | concept-map | same | definitional |
| `routing-notation` | vocabulary | `docs/schemas/routing-notation.yaml` | definitional |
| `archwiz-pointer-index` | hash-pointer | `archwiz/pointer_index.json` | decode-only, **count-only** |

Real names found in-repo (the literal `CompressionMapping` occurs
nowhere): `SYMBOL_MAP`, `MAPPINGS`, `STOPWORDS`, `LEET_MAP`,
`CANONICAL_TOKENS`, `VARIANT_INDEX`, `CedarIndex`, plus the markdown
tables and the nomenclature `seed.json`/`schema.sql` vocabularies.

## Feed schema

```jsonc
{
  "schema": "linguist-panel-feed/v1",
  "generated_at": "RFC3339 UTC",
  "generator": "scripts/linguist/linguist_panel_feed.py",
  "contract": "docs/ops/LINGUIST-PANEL-FEED.md",
  "sources": { "<key>": "<repo path>", "...": "..." },
  "counts": {
    "families": 15,
    "entries_total": 7575,        // includes count-only families
    "entries_included": 288,      // entries actually enumerated
    "per_family": { "<family id>": 0 }
  },
  "families": [{
    "id": "cedrlang-compression",
    "name": "CedrLang compression mappings",
    "kind": "word-map",
    "source_path": "workspace/compression_sandbox/cedrlang/cedrlang.py",
    "direction": "bidirectional | encode-only | decode-only | definitional",
    "canonical_source": "<repo path that wins on conflict>",
    "entry_count": 31,
    "entries_included": true,
    "round_trip": { "verified": 31, "failed": 0, "not_applicable": 0 },
    "note": "optional"
  }],
  "entries": [{
    "id": "<family>:<slug of source>",
    "family": "<family id>",
    "source": "<source string, e.g. human phrase / letter / term>",
    "variants": ["<target forms>"],   // [] when none (elision, definitional)
    "direction": "<as family>",
    "provenance": { "path": "<source file>", "line": 66 },
                                  // line = span anchor (1-based first
                                  // defining line) for in-text threading
    "round_trip_verified": true,  // true | false | null (not applicable)
    "note": "optional — lossy reason, casing note, registry caveat",
    "...": "family extras: meaning / grimoire / orchestra / concept_id / label_type / relation / confidence / section / definition / status"
  }],
  "gaps":    [{ "id": "...", "detail": "..." }],
  "excluded": ["<surface considered and deliberately not a family>"]
}
```

### Entry semantics for the panel

- **Threading:** join an in-text occurrence to its entry by
  `family` + `source`/`variants`; jump to source via
  `provenance.path` + `provenance.line`.
- **`round_trip_verified: false`** is data, not an error: it marks
  lossy-by-design behavior (stopword elision; duplicate-symbol decode,
  where `note` names the phrase `REV_MAP` actually decodes to).
- **`null`** = round-trip does not apply (definitional/prose families,
  single characters whose ambiguity resolves only at token level).

## Verified round-trip results (at first collection, master `c1bae36`)

- `cedrlang-compression`: 31/31 via `compile_doc`/`decompile_doc`
  (case-insensitive; the word mappings do **not** live in
  `compress()`/`expand()`).
- `cedrlang-symbol`: 25/32 exact; 7 lossy — 6 phrases share a symbol
  with a later phrase (`→`, `⇒`, `vs`, `?`, `⚠`; `REV_MAP` last-wins
  decodes to the later phrase) and `set` (`:=`) is corrupted on decode
  by the `=` (`answer`) pair firing inside it.
- `phase-codec-canonical-tokens`: 31/31 at p=1.0, case-insensitive
  (61 indexed variant forms, 30 non-canonical).
- `cedar-pointer-commands`: 45/45 register→expand against a throwaway
  index; the live registry is runtime-local (`~/.cedar/`), not in-repo.
- `grimoire-orchestra-crosswalk`: 15/16 rows match a cedrlang
  canonical pair; `l00p`'s Grimoire cell carries an emoji suffix.

## Gaps (also in the feed's `gaps`)

- `archwiz/mapping_pointer_index.py` is cited as the
  `mapping-pointer-index/v1` contract by four documents but **does not
  exist on master** — not established as implemented.
- `REV_GRIMOIRE_MAP` is named in the recovery doc; only the derived
  `REV_MAP` exists in code.
- `linguist-machine-parity` (LMP-01) is a posted placeholder: zero
  mapping entries, no family emitted.
- PR #154's encrypted pointer store / Actions obfuscation hooks remain
  proposed, not verified deployed.
