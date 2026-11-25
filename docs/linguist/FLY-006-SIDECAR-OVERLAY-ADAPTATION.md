# FLY-006 — Linguist Sidecar / Overlay Adaptation Audit

**Status:** evidence-backed research handoff; no runtime changes.
**Prepared:** 2026-11-25
**Scope:** `timerloggedout-spec/termux-monorepo`, current `master` snapshot `8f8437b8e49c67f124755c5cd0f3678b2a67fdcf`.
**Routing:** FLY-006 `cue/work-comms.jsonl` (pair work); FLY-005 remains export/backup coordination; FLY-003 remains publication receipts.

## Executive finding

The current repository has a working phase codec, a nomenclature search/add tool, and several historical content-addressed pointer/index implementations. It does **not** currently contain the proposed `archwiz/mapping_pointer_index.py`, an NSE-021 overlay loader, or a verified private encrypted mapping-sidecar implementation.

The NSE-021 design and plan exist on the unmerged branch `docs/nse-021-sidecar-comment-overlays-r2`; the related PR #5737 is closed without merge. Treat these artifacts as proposal/design evidence, not deployed runtime behavior.

## Verified current implementation

| Surface | Exact path | Current contract / evidence | Classification |
|---|---|---|---|
| Phase codec | `workspace/compression_sandbox/cedrlang/phase_codec.py` | `to_1337speak` / `from_1337speak`; initial probability 0.70; seeded RNG; canonical token variant index; exact phase-token restoration | Implemented |
| Phase codec tests | `tests/test_cedrlang_phase_codec.py` | Six tests: 70% constant, p=0 identity, p=1 reversible, seeded repeatability, protected prose/numbers/path, probability validation | Present; not executed in this audit |
| Nomenclature tool | `scripts/linguist/matrice_search.py` | stdlib `search`, `screen`, `add`, `validate`; additions forced to candidate | Implemented |
| Matrice tests | `scripts/linguist/tests/test_matrice_search.py` | Three tests for search, collision screening, add+validate | Present; PR #5299 reports 3/3 local |
| Matrice seed | `docs/proposals/active/notation-sets/nomenclature-matrix/seed.json` | Canonical concept/label/mapping seed; source registry and domain labels | Implemented data substrate |
| Matrice workflow | `.github/workflows/matrice-search.yml` | Manual `workflow_dispatch` search/validate; artifact + step summary | Implemented; read-only workflow |
| Linguist panel feed | `scripts/linguist/linguist_panel_feed.py` | Imports actual codec registries, derives live round-trip flags, records gaps | Implemented observability |
| Panel feed contract | `docs/ops/LINGUIST-PANEL-FEED.md` | Canonical source table; explicitly records missing Mapping Pointer Index and unverified encrypted hooks | Implemented documentation / gap register |
| ArchWiz pointer index | `archwiz/pointer_index.py` | Maps code hashes to local export session/manifest locations; runtime-local `~/.archwiz/pointer_index.json` | Existing export pointer index; **not** mapping sidecar |
| Synthegration index | `cli-synthegration/synthegration_index.py` | Session/message/block pointers, content hashes, taxonomy tree and wire encoding | Existing provenance index; separate data model |
| Pointer sync | `cli-synthegration/pointer_sync.py` | Computes missing blocks against a remote manifest | Existing sync helper; not overlay loading |

### Critical documentation drift

`NSE-020-MAPPING-POINTER-ROUNDTRIP.md` and `ROUNDTRIP-IMPLEMENTATION.md` describe `archwiz/mapping_pointer_index.py` as implemented. The current master panel contract and collector explicitly flag that path as absent. The current `archwiz/pointer_index.py` is a different implementation with a different purpose and data model.

**Disposition:** classify the Mapping Pointer Index as **specified / implementation missing** until a schema-backed implementation and tests land. Correct the NSE-020 implementation wording before promoting dependent work.

## NSE-021 sidecar overlay design — recovered proposal

The design and plan are present on `docs/nse-021-sidecar-comment-overlays-r2`:

- `docs/proposals/active/notation-sets/NSE-021-SIDECAR-OVERLAYS.md`
- `docs/superpowers/specs/2026-11-20-siglary-sidecar-overlays-design.md`
- `docs/superpowers/plans/2026-11-20-siglary-sidecar-overlays.md`

The design selects content-addressed sidecar overlays for eligible Markdown prose and syntax-aware code comments. Its key invariants are sound and should be retained:

1. Canonical source blobs remain byte-identical during treatment experiments.
2. Every overlay pins source blob SHA, source SHA-256, stable anchor, notation version, renderer version, and provenance.
3. Executable code token streams remain identical.
4. Markdown structure and protected technical spans remain identical.
5. Changed source hashes produce stale-overlay/re-anchor events.
6. Semantic recovery and human comprehension are quality gates ahead of token/latency optimization.

The design's historical root-document rule is important: root `CLAUDE.md` is the primary collaborator entry; root `CLAUDE.hum.md` is the Linguist/tooling-compatibility surface. Historical `AGENTS.md` / `AGENTS.hum.md` lineage and the blob-identical rename into `CLAUDE.hum.md` remain provenance edges. Do not infer a current root 1:1 projection without an explicit mapping record.

## Adaptation map for the current repository

### 1. Canonical notation and semantic IR

- Read/write nomenclature through `docs/proposals/active/notation-sets/nomenclature-matrix/seed.json`.
- Resolve operator/glyph/chord class and domain through the current Siglary standard and Matrice.
- Use `scripts/linguist/matrice_search.py search|screen|validate` as the terminology discovery and collision gate.
- Normalize eligible spans to a typed semantic record before rendering. The overlay layer references canonical concept IDs; it does not mint private meanings or treat display shorthand as canonical semantics.

### 2. Mapping Pointer Index — required new component

Proposed path: `archwiz/mapping_pointer_index.py` (the path already cited by NSE-020).

Required record fields:
- schema/version and immutable mapping ID;
- source path, Git blob SHA, source SHA-256;
- encoded-surface SHA-256 and mapping-payload SHA-256;
- codec, notation, renderer and layer versions;
- parent pointer(s), layer, stable anchor, provenance and lifecycle;
- payload locator and encryption/key-version metadata only (never key material).

Required behavior:
- `register(source, surface, mapping, metadata) -> pointer`;
- `resolve(pointer) -> verified mapping reference`;
- `verify(pointer, source, surface) -> structured pass/fail`;
- fail closed on missing, stale, mismatched, ambiguous or unsupported versions;
- preserve full SHA-256 identity; any short pointer is display-only and collision-checked;
- keep private mapping payloads and encryption keys outside Git, logs, Actions artifacts and public comments.

The existing `archwiz/pointer_index.py` can inform hash/session lookup and the Synthegration index can inform provenance pointer shape. Neither is a drop-in implementation.

### 3. Sidecar overlay schema and loader — required new component

Proposed bounded paths from the recovered NSE-021 plan:
- `experiments/doe/siglary-context-tournament/schema/overlay.schema.json`
- `scripts/notation/overlay_validate.py`
- `scripts/notation/overlay_extract.py`
- `scripts/notation/overlay_render.py`
- `scripts/notation/overlay_materialize.py`
- `tests/test_siglary_overlay_schema.py`
- `tests/test_siglary_overlay_anchors.py`
- `tests/test_siglary_overlay_materialize.py`
- `tests/fixtures/siglary_overlay/`

Loader contract (proposed; implementation absent):
- **Input:** canonical source root + source Git commit/blob SHA + overlay manifest + selected variant + schema/renderer/notation versions.
- **Validation:** schema; source identity; stable anchor uniqueness; allowed node kind; protected-span boundaries; notation references; mapping pointer and payload digest; lifecycle/expiry.
- **Output:** immutable in-memory overlay plan or disposable materialized tree + machine-readable validation receipt.
- **Precedence:** canonical source always wins for executable content and protected spans; overlay applies only to explicitly selected prose/comment nodes; explicit exclusions win over broad selectors.
- **Fallback:** stale or unverifiable overlay => return canonical source unchanged and emit a structured stale/fail-closed receipt.
- **Errors:** distinguish missing source, stale source hash, unknown schema/version, duplicate anchor, missing mapping pointer, digest mismatch, parser coverage gap, and protected-token mutation.
- **Consumers:** ICM Markdown, LLM-map Markdown, syntax-aware comment materializer, DoE/MVT harness, and Linguist panel feed. Start with Markdown prose and standalone/line comments; add documentation comments only after parser fixtures.

### 4. Human-readable parity

Build an explicit mapping ledger rather than filename-based assumptions. Each row records canonical path, human/compatibility path, relationship type, historical alias, source/projection blob hashes, renderer version, fixture ID and state.

Required classifications:
- direct projection;
- compatibility/tooling surface;
- historical rename;
- independent entry;
- pending migration;
- excluded with rationale.

Use the current README-declared `CLAUDE.md` / `CLAUDE.hum.md` roles. Record `AGENTS.md` / `AGENTS.hum.md` as historical lineage and compatibility evidence. Require exact byte round-trip only where an explicit projection contract exists.

### 5. Tests and evidence

Present, reproducible commands (run from repository root):

```sh
python3 -m pytest -q tests/test_cedrlang_phase_codec.py
python3 -m pytest -q scripts/linguist/tests/test_matrice_search.py
python3 scripts/linguist/matrice_search.py validate
python3 scripts/linguist/index_alignment.py
```

The first two are existing fixture suites. PR #5299 records 3/3 local Matrice tests and a clean seed validation (116 concepts, 170 labels, 0 problems at that revision). The phase codec test file contains six assertions/scenarios. This audit did not execute repository tests; results must be attached from a current checkout and exact commit.

New overlay acceptance fixtures:
- Markdown headings, tables, lists, nested formatting, code fences, inline code, URLs, paths, citations and quotations;
- comment-only transformations for each supported language;
- executable-token stream equality and parse validity;
- source blob immutability;
- stable anchors under line-only movement;
- stale-anchor detection after neighboring syntax changes;
- missing/incorrect mapping pointer and tampered payload rejection;
- byte-exact decode for private/exact mode;
- human comprehension and evidence/citation accuracy.

## Minimal integration sequence

1. **Reconcile docs:** correct NSE-020's false implemented claim; link the recovered NSE-021 proposal/design/plan and mark them proposed until acceptance.
2. **Land mapping pointer index:** schema + registry + resolver + verification tests; keep private payload encryption behind a separate interface.
3. **Land overlay schema/validator:** no materialization until schema and source identity checks pass.
4. **Land extractors:** Markdown AST first, then Tree-sitter comment nodes with language-specific fixtures.
5. **Land renderer/materializer:** disposable tree only; preserve source and executable tokens.
6. **Wire Matrice:** concept IDs and typed operator/glyph/chord references; use Matrice validation before overlay issuance.
7. **Wire panel feed:** expose overlay counts, stale/fail-closed counts and actual round-trip outcomes from runtime evidence; keep count-only/private data excluded.
8. **Pre-register DoE/MVT:** run four representation arms × three context placements × three surfaces using the existing experiment contract; quality floors and held-out replication precede promotion.
9. **Promotion:** comment/documentation-only patch, exact-head repo-gate and termux-smoke, dual review.

## FLY-006 handoff status

- MuseVM's first Siglary/PDDL answer is recorded in `cue/work-comms.jsonl` and points to merged PR #5299.
- Cue's follow-up asks for the overlay-loader contract and exact implementation/test evidence.
- This audit supplies the file-level answer and identifies the primary blocker: the Mapping Pointer Index is currently a documented contract with no matching master implementation.
- This report is a repository research artifact; it does not claim to be a Cue or MuseVM message, and it does not impersonate either channel participant.

## Source links

- [NSE-020 Mapping Pointer / round-trip](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/notation-sets/NSE-020-MAPPING-POINTER-ROUNDTRIP.md)
- [Round-trip implementation plan](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/proposals/active/notation-sets/ROUNDTRIP-IMPLEMENTATION.md)
- [Linguist panel feed contract and gaps](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/LINGUIST-PANEL-FEED.md)
- [Linguist panel feed collector](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/scripts/linguist/linguist_panel_feed.py)
- [Phase codec](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/workspace/compression_sandbox/cedrlang/phase_codec.py)
- [Matrice search tool](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/scripts/linguist/matrice_search.py)
- [NSE-021 design branch](https://github.com/timerloggedout-spec/termux-monorepo/tree/docs/nse-021-sidecar-comment-overlays-r2)
- [NSE-021 original PR #5737](https://github.com/timerloggedout-spec/termux-monorepo/pull/5737)
- [Merged Matrice/PDDL PR #5299](https://github.com/timerloggedout-spec/termux-monorepo/pull/5299)
- [FLY-006 protocol](https://github.com/timerloggedout-spec/muse-vm-workspace-backup/blob/main/cue/WORK-COMMS.md)
