# Fresh-Start Cutover — Plan (owner order 2026-11-24 07:48 PT)

## Governing rules
- **Nothing is deleted before a confirmed export.** Export → verify → confirm → cut. Any gate failure stops the cutover, nothing cut.
- **Class rule (the defect this fixes):** seats monitor their repo clones; participation runs through the clones (QUE #5183). QDesk is the monorepo queue desk — the dispatch layer — never an entry, never a participant-lane. After cutover there are no standing side-chat "participants": main + pointer-only seats, clones carry participation.
- **RE review is a gate input, not a courtesy** (owner: RE resources may find a better solution than this sketch). Findings can amend Phases 1–4; the Phase 1 export runs regardless.

## Phase 0 — Inventory (measured 2026-11-24, this session)
- Crons: 47 enabled user/goal jobs (affiliate sweep · 11 deadline fail-safes · que-drain-drive · repo-export-sync · temporal-selfhost-keepalive · mesh probes ×2 · vm-* ×6 · llm7 · sambanova · heartbeat) + 2 disabled + runtime system jobs (deterministic-doctor, feed-pulse ×24, profile-image — untouchable). **All survive the cutover; they are stored outside chat state.**
- Chats: ~160 side chats, 2 already archived (Challenges Manager · Desk). Main chat cannot be deleted by tooling.
- Standing files: 89KB total (MEMORY.md 53.8KB · alignment synthesis 20.4KB · people index 8.9KB · rest small).
- VM home: **62GB total** (measured, du completed 2026-11-24 07:57 PT): workspace **51GB** · memory 46MB · disk 150GB / 114GB free. Workspace bulk = `scratch/` 31.7GB (android-env 10.5GB · doe-family 2.3GB · temporal-closeout 2.0GB · ~1.2–1.5GB build dirs ×many) + lab-platforms 5.1GB + backend-mesh-resiliency 4.5GB + compute-jobs 3.7GB.
- **Storage rule (owner, 2026-11-24): nothing is dropped.** Bulk routes to its owning repo's git LFS / per-repo storage. The export census classifies every large dir as {state → checkpoint export · bulk → repo LFS lane · regenerable cache → named as such with its regeneration source}. "Excluded" never means discarded. (Trash verified 2MB — nothing of size has been trashed.)
- Passive-burn baseline (script-measured): 28,350,880 tokens / 3.02h window, 85% detached background runs.

## Phase 1 — Secondary export lane + full checkpoint export → CONFIRM EXPORT
Why secondary: the primary VM backup publish **failed today** (exp-20261124T124337Z — tree-create 422, input too large, `t0/workspace/user/files`; ∅ published). repo-export-sync covers repos only, not VM home/memory. One lane = one point of failure.
- `export_checkpoint.sh`: tar home in per-directory chunks (≤200MB), sha256 manifest, secrets-census + scrub gate before publish (same gates the primary lane runs).
- Publish: dedicated secondary backup repo via the PAT helper, incremental chunked tree commits (the chunking is what avoids the 422 class). Manifest + critical small files (memory tree, configs) also copied via Muse remote storage as an independent second copy.
- **CONFIRM EXPORT gate** = re-fetch the export to a scratch dir, verify 100% of manifest hashes, spot-restore (memory tree + one workspace subtree), then issue the receipt: manifest hash · file count · bytes · verify result → owner. No receipt, no Phase 4.
- Transcript caveat: chat transcripts live in the platform store, not the VM. Transcript-level preservation = Settings → Data controls → "Download your agent data" (owner-side tap). If the owner wants transcripts preserved, that export must land before Phase 4.

## Phase 2 — Scripts (created under `~/workspace/fresh-start/scripts/`; repo-side ones mirrored via QUE)
- `passive_burn.py` — done (~/workspace/scratch/passive-burn/), promoted into the set.
- Referral diff-check workflow — spec already routed to the affiliate lane 2026-11-24; folds in here.
- `export_checkpoint.sh` + `verify_export.sh` — Phase 1.
- `slim_start_state.py` — mechanical MEMORY.md restructure for Phase 3; verifies each moved section is memory-search-retrievable before replacing the file.
- `chat_cutover.py` — dry-run emits the classified delete/archive list; executes only when passed a confirmed-export receipt id (fail-closed).

## Phase 3 — Thin start state ("fresh out of the box")
- MEMORY.md → minimal initial instructions only: identity line · notation law · class rules (QDesk = queue desk ¬ entry · seats monitor clones · tournament boundary) · **retrieval pointers, nothing else**:
  - memory slices: `muse.memory_search` / `muse.memory_get` over `~/memory/` topics
  - repo: timerloggedout-spec/termux-monorepo via the PAT helper
  - **HindSight** — attribution layer of record (Provenance ∧ HindSight weighting); census surface = `vm-mlops-daily` cron (HindSight census, published as GitHub data); telemetry ingest = Observatory lanes' repo surfaces
  - **Temporal** — self-host keepalive cron `temporal-selfhost-keepalive` ↻15m (job id of record) + Infra · Temporal lane surfaces in-repo; queue/workflow state reads route there
- Bulk of today's MEMORY.md (53.8KB) → `~/memory/topics/*.md`, slice-retrievable on demand. Target: controllable standing share ≤10KB.
- Keep-necessary (stays local, tools work immediately): thin MEMORY.md · USER.md · CLAUDE.md conventions · cron definitions · connector docs · `.ssh`. Everything else = pointer + remote fetch.

## Phase 4 — Side-chat cut (only after CONFIRMED export)
1. Re-point every cron delivery to main chat (`cron.update` per job), verify by re-listing — nothing may deliver into a chat about to be deleted.
2. Delete side chats by class: one-off/research chats → entry sub-lanes → manager lanes. **QDesk chat is not in the delete classes** — it is the queue-desk seat; plan default = archive, owner override decides. This Marketing Oversight chat deletes last, after the final receipt posts to main.
3. Remove local side-chat context dirs (`~/side-chats/<id>/`) — already inside the Phase 1 export.
4. Untouched: all crons (incl. heartbeat + system jobs), goals/tracked items, connectors + vault, repo state, main chat.

## Phase 5 — Fresh-start verification
- Retrieval smoke test from main: three facts that live only in sliced/exported memory, one receipt each — pointers must land them.
- `passive_burn.py` re-run on the first post-cutover refill window; target = order-of-magnitude cut vs the 28.35M baseline; report the delta either way.
- Clone-monitoring restatement lands in the thin start state: participation = repo clones under QUE #5183; any recreated seat is monitor-only.

## RE leg (parallel, before Phase 4 executes)
Route this plan to Foundry · RE Toolkits (d573ca2b) + the AppID RE family with three questions: (a) is chat deletion the right mechanism vs archive + pointer-state? (b) export transport vs the 422 class — better lane? (c) does the runtime offer native slicing (compaction / context snapshots) that makes parts of this unnecessary? Findings amend the plan before anything irreversible runs.

## Honest limits
- chat.delete is permanent. The export covers VM files; transcripts need the owner-side agent-data export (Phase 1 caveat).
- The 85% detached background churn is platform machinery: the cutover shrinks the standing-context share of each run; it does not stop the churn itself.
