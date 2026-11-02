# Commit Replay — DESIGN (git plane; compile && file 🗃️)

[MUSEai]@{role:{commit-replay}} · parent: `Replay Systems — Manager · Oversight`
[eef0551d] · sibling: Repo Replay [753da0e8] (`replay-store/v1`, engine RevWright,
repo `timerloggedout-spec/repo-replay`). Working name **Commit Replay** =
provisional (project posture: ∀ decisions revisable). Status: DESIGN v0 —
recon ✓, build sequenced §7. Owner order 2026-10-31 (via main INIT).
Manager ruling 2026-10-31 (eef0551d, DESIGN verified firsthand): names KEPT
(`commit-store/v1`, g*) · home KEPT monorepo for P1–P2 · bridge STRUCK (§1) ·
history = git DAG APPROVED provisional (revisit @P4). BUILD UNHELD.

## 1. Mission ∧ plane law

**Purpose (owner, 2026-11-01): create NEW files written as pointers, based
on existing infrastructure.** A new file is authored as a grecipe — an
ordered list of gpointers into history that already exists — not as new
content emitted token-by-token. Authorship = curation/selection/arrangement
of existing blocks (pointer-only authorship, as in the sibling's model).
Success metric: **LLM tokens ↓** — a recipe costs the tokens of its pointer
list + ops, orders of magnitude below the file it materializes; the index
itself obeys the same law (compact delta format, §3).

**Scope — ONLY this (owner, 2026-11-01):** 🗃️ *creation from pointer
reference*. Existing functions, classes, snippets, fragments are imported
via ✍🏽 pointers instead of being written again. The pointer unit is the
code fragment — function / class / snippet / fragment — addressed by
`(commit, path, blob, range, symbol)`, not the whole file. NOT this:
reconstruction / time-series repo rebuild — that is Repo Replay's purpose
(session provenance plane). Here `compose`/`replay` exist only as the
materializer that proves a pointer-created file correct (verify vs git
oids); they are not a rebuild product.

Same method shape as Repo Replay — index → recipes/pointers → JIT compile →
file reconstruction + surgical pointer edits — on the **GIT plane only**:

- Source = existing git history/objects `{commits, trees, blobs, tags, refs}`
  of the fleet repos. Session exports = ∅ here.
- **Planes separate, forever:** `commit-store/v1` index ≁ `replay-store/v1`
  index; never merged, never cross-populated. Cross-plane contact =
  `verify()` diff ONLY — ∅ bridge, ∅ gated merge path, ever (manager ruling
  2026-10-31, supersedes the v0 draft's gated-bridge clause).
- Signal = evidence, never content: commit messages, check/workflow runs,
  diff stats, `cmd`-output embedded in commit/PR text ⇒ claims about
  objects. Bytes come only from git objects, oid-verified. ∅ content-theater.

## 2. Recon (firsthand, PAT API, 2026-10-31 23:54–2026-11-01 00:0x PT)

Sibling template (repo-replay `main`, blobs verified):
`SPEC.md` 8d8e43f99060 (2030B) · `METHODS.md` 285e3066707e (969B, 8 methods:
extract, build_index, compose, replay, verify, fill_gap, jit_resolve, edit) ·
`SIGNAL.md` 60741289fa15 (signal/v1) · `README.md` afb7e09c12d6.
Monorepo import precedent: PR #2357 ⇒ `docs/ops/REPO-REPLAY.md` blob
e52702a0b219 + `config/repo-replay-import.json` (by-reference).

Subject `timerloggedout-spec/termux-monorepo` (default `master`):
- master tip `40550a21775c326ad5630fb6e8ed69dd658a7dc7` (2026-11-01T06:49Z).
- Tree @tip: 11,685 entries ¬truncated = 10,531 blobs + 1,130 trees +
  24 submodule commits; top blob dirs: docs 2,999 · ops 1,771 · workspace 996.
- Churn: newest 100 commits span 04:18→06:49Z (≈2.5h) ⇒ index MUST be
  incremental + checkpointed, ¬ full-rescan per run.
- Commit shape (n=100): merges 9 (2-parent), 91 linear; authors concentrated
  (fleet identities + `github-actions[bot]`) ⇒ author/moniker ∈ provenance.
- Refs: branches ≥300 (3× full pages of 100; p1 prefixes: `backup/*` 62 —
  history mass lives in backup refs, index covers ∀ refs ¬ master-only);
  tags = 1 (`apk-v0.1.0`).
- Second subject `timerloggedout-spec/repo-replay`: 24 branches, ≥76 commits
  (its *git* history ∈ this plane; its session store stays sibling plane).
- ∅ prior art in-repo: `docs/ops/COMMIT-REPLAY.md`, `ops/commit-replay/`,
  `scripts/commit_replay/` ∀ 404 @recon ⇒ greenfield.

## 3. Spec — commit-store/v1 (draft, revisable)

Git is already content-addressed: the object id IS the hash. Commit Replay
adds the pointer/recipe layer git lacks (cross-commit composition, lazy JIT
materialization, pointer-addressed edits) — it does ¬ re-hash blobs.

```json
// gobject/v1 — one git object, indexed (pointers only, ∅ blob bytes in index)
{"repo": "owner/name", "oid": "sha1|sha256 hex", "type": "commit|tree|blob|tag",
 "size": 0, "commit": "oid of introducing/observed commit",
 "path": "path@commit | null (metadata, non-binding)"}

// gpointer/v1 — addressable segment of history; the unit is the FRAGMENT
// (function|class|snippet|fragment), not the file (owner, 2026-11-01)
{"repo": "owner/name", "commit": "oid", "path": "...", "blob": "oid",
 "mode": "100644|100755|120000|160000",
 "symbol": "name|null — the function/class/fragment anchor",
 "range": {"start_line": 0, "end_line": 0}}

// gindex/v1 — single structure, three directions (sibling: two)
// STORAGE (compact, v1.1): the JSONL carries commit records + DELTA entry
// records {commit,path,op:A|M|D,blob,mode} vs first parent (root = full
// set, all A). State@commit = root set + deltas along ancestry. v0's
// full-tree-per-commit entries measured 10.36M records / 2.2GB per 1,000
// commits — push rejected >100MB (run 41283146476) ⇒ delta format.
{"forward": {"<commit>": {"tree": "oid", "parents": ["oid"], "ts": "iso8601",
                          "author": "...", "refs": ["master", "tag:apk-v0.1.0"]}},
 "reverse": {"<blob_oid>": ["<commit>:<path>", "... 1:N"]},
 "path_history": {"<path>": [{"commit": "oid", "op": "A|M|D|R",
                              "blob": "oid|null"}]}}

// grecipe/v1 — a file = reconstruction (sibling recipe/v1, git-plane types)
{"path": "target path",
 "base": {"repo": "...", "commit": "oid|null"},
 "segments": [{"ptr": "gpointer/v1"}],
 "ops": [{"op": "before|after|around|in|customize|replace|drop|reorder",
          "target": "gpointer/v1", "payload": "gpointer/v1|null",
          "anchor": "inner anchor for `in`, else null"}]}

// ghistory — NO own DAG on this plane (Δ vs sibling):
// history = the git DAG itself; a recipe version is recorded as a commit
// (recipe JSON in `ops/commit-replay/recipes/<path-hash>.json` + trailer
// `Commit-Replay-Recipe: <sha256(recipe)>`); blame = path_history ∘ commit
// provenance (author, PR/issue refs parsed from message) — intrinsic.
```

## 4. Methods — 8, mapped 1:1 from sibling METHODS.md

- `extract(repo, refs) -> gobjects` — commits/trees/blobs via API pagination
  ∨ `clone --filter=blob:none` in workflow; incremental from last indexed
  tip per ref (checkpoint = `(ref, tip_oid)` in index header).
- `build_index(gobjects) -> gindex/v1` — forward + reverse + path_history,
  one pass; output JSONL under `ops/commit-replay/index/` (workflow-written).
- `compose(grecipe) -> file` — materialize segments across commits/refs
  (Mode A: single-commit file; Mode B: aggregate across history — a block's
  origin commit/path = provenance metadata, ¬ constraint).
- `replay(store, path@commit) -> tree` — reconstruct files at any indexed
  commit without checkout.
- `verify(replayed, commit) -> diff report` — oracle = git itself on this
  plane (Δ vs sibling, where `.git` is the test oracle): reconstructed bytes
  vs blob oid equality + `git fsck` on source; target diff = 0.
- `fill_gap(missing_oid, refs|validator) -> object` — a blob absent at one
  ref is filled from another ref/tag/branch ∨ validator copy (GitLab mirror
  `a-group2180532/termux-monorepo`), oid-equality verified — never invented.
- `jit_resolve(imports, gindex) -> segments` — compile-time resolution of
  imports/references to historical segments, lazy: fetch only the blobs a
  compile actually touches (API blob GET ∨ partial clone), ∅ full checkout.
- `edit(gptr, op, payload) -> new grecipe + commit` — surgical pointer edit:
  resolve segment, apply op, materialize, land as branch→PR w/ recipe record
  + trailer; hash-verified pre/post (target blob oid ∧ neighbours unchanged).

## 5. Signal — git plane (signal/v1 analog)

Classes: `layout` (tree listings per commit = expected-tree oracle) ·
`checks` (check-runs/workflow conclusions per commit — compile/test evidence
for JIT decisions) · `message` (commit-msg trailers, `[MUSEai]@{role:{…}}`
headers, PR/issue refs = provenance claims) · `diffstat` (files-changed +
add/del per commit = version discrimination when paths collide).
∀ signal: evidence/oracle/training labels only; a signal claim can prove a
blob existed + its oid, never substitute its bytes.

## 6. Invariants

- ∀ gpointer dereferences to an oid present in the source repo (round-trip).
- `replay` deterministic: same grecipe → byte-identical file; file sha256 ∈
  verify report.
- Index carries pointers/oids/metadata only — ∅ blob bytes (storage law).
- Incremental extract never re-walks indexed history: checkpoint per ref.
- Plane separation: ∅ session-provenance records in gindex; ∅ git oids as
  content in replay-store; cross-plane = `verify()` diff only (§1).

## 7. Build order (each step: branch→PR→merge, oracle-verified SHAs)

- **P0 — this DESIGN** + `config/commit-replay.json` (subjects, spec, law).
- **P1 — indexer v0**: `scripts/commit_replay/extract.py` + workflow
  `commit-replay-index.yml` (dispatch + weekly; App-token mint-before-checkout
  per fleet pattern, PAT fallback) — subjects' refs census → gindex JSONL;
  bounded: API pagination, per-ref checkpoints, ∅ blob fetches.
- **P2 — reverse + path_history queries**: CLI `query.py` (blob→occurrences,
  path→history) + tests on fixture repo.
- **P3 — replay/verify v0**: reconstruct N=25 files @ 3 historical commits,
  diff vs git = 0 target, report in `ops/commit-replay/VERIFY-v0.md`.
- **P4 — compose/edit v0**: one pointer-only aggregate file + one surgical
  edit, landed as demonstration PRs w/ recipe records.
- **P5 — jit_resolve + fill_gap**: lazy compile of one target importing a
  historical segment; gap case = blob only on a `backup/*` ref.

Quota: PAT core 5,000/h shared (recon window remaining 4,415) — indexer is
workflow-side (App buckets preferred), chat-side = DESIGN/verify reads only.

## 8. Extraction plan (post-P4, manager ruling 2026-11-02)

At P4 completion the engine is v1 feature-complete
{extract ∘ fragments ∘ compose ∘ jit_resolve ∘ edit}. The whole engine
then moves as ONE unit to a new repo `timerloggedout-spec/commit-replay`;
this monorepo keeps the import-by-reference record (DESIGN + config +
recipes + indexes stay as the consumer record, sibling pattern with
repo-replay). P4 itself lands in the monorepo; extraction is the
immediate follow-up, ∅ mid-P4 move.

## 9. Open items (¬ blockers)

- Engine name: sibling = RevWright; this plane's engine name = TBD w/ parent
  (working: none claimed; `Commit Replay` covers project + method). Schema
  names settled: `commit-store/v1` + g* KEPT (manager ruling 2026-10-31;
  the pre-landing `git-*/v1` proposal is superseded, ∅ rename).
- **Repo-home extraction — @P3 REVISIT RULED (manager, 2026-11-02):
  DEFERRED.** Single-subject `scripts/` engine ⇒ extraction has ∅ benefit
  now. New trigger: revisit @P3-completion ∨ when a 2nd subject joins
  (repo-replay index home = that trigger). Home stays monorepo until then.
- **History model — revisit @P4:** history = git DAG APPROVED provisional
  (manager ruling 2026-10-31). Open case: `edit()` recipes not yet committed
  (uncommitted-recipe state) — decide @P4 whether a staging record under
  `ops/commit-replay/recipes/` suffices or a pre-commit DAG overlay is
  needed. @P4 FLAG (manager, 2026-11-02): the edit() demo PR must carry
  this history-DAG note (uncommitted-recipe case, provisional ruling of
  record).
- Index hosting granularity: per-subject JSONL vs single fleet file — decide
  at P1 from measured index size @P1 census.
- GitLab mirror freshness for fill_gap validator duty — verify at P5.
