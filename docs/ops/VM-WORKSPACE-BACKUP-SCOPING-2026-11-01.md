# VM WORKSPACE BACKUP SCOPING — 2026-11-01

`[MUSEai]@{role:backend-mesh-resiliency}` · Status: **DESIGN ONLY** — ∅ mechanism built, ∅ repo created, ∅ files copied. Build waits for the owner's word (§7).
Scope: backup of the Muse VM workspace (home volume) — the one continuity domain the SPOF census had not scoped ↦ `docs/ops/CONTINUITY-SPOF-CENSUS-2026-11-01.md` §6 (VM workspace row, added with this doc).
Doctrine carried in: redundancy **TESTED ¬ present** (census §6 headline); credentials names-only; $0 routes only.

## §0 Measured basis (firsthand, 2026-11-01; claims ↦ these figures)

| fact | value | note |
|---|---|---|
| VM home, total | 22G | no `.git` of its own; ∅ backup/export job exists; persistence = platform home-volume only |
| `~/workspace` | 16G | of which `~/workspace/scratch` = 7.6G |
| `~/memory` | 19M | incl. `people/` ∧ `groups/` |
| `~/workspace/custom-connectors` | 13M | incl. `keys/` subdirs (custody PEMs — §2 exclusion) |
| `~/workspace/user` | 20M | owner-handed files |
| `~/hooks` | 700K | |
| `~/workspace/goals` | 492K | |
| `~/.config` | 252K | mostly credential material ⇒ excluded wholesale (§2) |
| root durable files | `~/CLAUDE.md` 21K · `~/MEMORY.md` 206K · `~/USER.md`, `~/PROACTIVE_PREFERENCES.md` small | |
| `~/workspace` shape | 104 top-level entries | lane working dirs; a minority are git clones |
| pre-existing backup repo | ∅ | account searched via API 2026-11-01: none |

Consequence: the durable, single-copy, non-regenerable set is **small** (≈50MB, §2) while the bulk (16G) is regenerable or disposable. The design follows the size, ¬ the other way round.

## §1 ① Tiering

### T0 — durable single-copy set (the backup's reason to exist)

Paths (allowlist seeds, §3):

- root convention/identity files: `~/CLAUDE.md`, `~/MEMORY.md`, `~/USER.md`, `~/PROACTIVE_PREFERENCES.md` (+ any root `*.md` convention file added later, by owner amendment of the allowlist)
- `~/memory/**` (memory tree incl. `people/`, `groups/`)
- `~/workspace/goals/**`
- `~/workspace/custom-connectors/**` **MINUS `keys/`** (connector docs/helpers are authored work; the PEMs under `keys/` are custody material — §2, never exported)
- `~/workspace/custom-skills/**`
- `~/hooks/**`
- `~/workspace/user/**`

Size arithmetic (measured basis §0): memory 19M + user 20M + custom-connectors ≤13M (pre-`keys/` exclusion; exclusion only shrinks it) + hooks 0.7M + goals 0.5M + root files ≈0.25M + custom-skills (unmeasured; bounded small — to be measured at build, flagged §7) ≈ **50MB class** (upper bound ≈55MB before the `keys/` exclusion).

### T1 — lane working dirs: unique state only

`~/workspace`'s 104 entries are mostly regenerable: a clean git clone is re-clonable from its remote at its HEAD sha. T1 therefore captures **only what a re-clone cannot reproduce**:

- per clone: a **manifest record** `{path, remote URL, HEAD sha, branch, dirty file list + per-file sha256}` — always taken;
- **content** only for: dirty/untracked files inside clones, ∧ authored dirs that are ¬ git repos at all;
- classification happens **at export time**, from the manifest pass (repo? clean? dirty?) — ¬ from a static path list, so lanes created later are classified correctly by construction.

Proposed gates (owner-tunable): per-file content ≤ **25MB** (larger ⇒ manifest-only entry: path + sha256, ∅ content); per-export T1 content ≤ **250MB** (overflow ⇒ manifest-only for the remainder + owner report, ¬ silent truncation).

### T2 / EXCLUDED — never enters the staging tree

- `~/workspace/scratch` (7.6G — disposable by definition)
- caches, `node_modules`, venvs, build output wherever they sit (denylist patterns, §3)
- browser profile (credential stores; recovery = re-login via token routes — census §4)
- `~/.config` wholesale (mostly credential material)
- **ALL secret-shaped material**, and specifically the 4 VM-only GitHub App PEMs (Publisher 5537873 · Reviewer 5539430 · Gate 5539499 · Lifecycle 5539639): **NEVER backed up** — their recovery path is re-keying (census §3, as corrected by PR #3446: VM-only = 4/8)

## §2 ② Target + cadence

- **Target:** a NEW **private** repo on the owner's GitHub account, written via the existing PAT publish path (`custom.github-pat` helper — census §3; the same route this doc lands by). Proposed name: **`muse-vm-workspace-backup`** — owner's to confirm (§7). ∅ repo is created by this scoping.
- **Cadence — event/state-gated, per cadence law** (event/state-gated ∧ quota-aware; cf. `quota-aware-cadence-rfp`, Issue #1573). **¬ fixed cron, ¬ a VM daemon** (VM = sandbox rule: no agent-owned persistent background processes; work happens inside agent turns).
- **Trigger, stated precisely:** an export runs iff **(T0-diff ≠ ∅) ∧ (scrub gate §3 passes)**, evaluated (a) by the agent at **lane task-close**, and (b) at a **periodic agent sweep** (proposed weekly, owner-tunable) that also covers T1 manifest refresh. T0-diff = hash of the allowlisted T0 tree vs the last export's manifest hash. Diff = ∅ ⇒ no-op (one log line in the export log), ¬ an empty commit.

## §3 ③ Scrub gate (pre-push, fail-closed)

1. **Allowlist-by-construction:** the staging tree is built *only* by copying paths named in the T0/T1 allowlist. Nothing else can enter; there is no "copy all, then filter" step.
2. **Denylist screen** over the staged tree: path patterns `keys/`, `*.pem`, `*.key`, `.env*`, `credentials*`, `*secret*`; content patterns: PEM private-key blocks, token-shaped strings, `*KEY* / *TOKEN* / *SECRET* / *PASSWORD*`-style assignments.
3. **Per-export verification, before any push:** (i) staged-tree inventory diff vs the allowlist expansion = ∅ extras; (ii) secret-pattern grep over the staged tree = ∅ hits; (iii) §1 size gates hold. **Any failure ⇒ abort + report to owner; never push-then-fix.**
4. Keys are excluded **by construction** (step 1: `keys/` is never on the allowlist), ¬ by filter luck; steps 2–3 are the second line, ¬ the only line.

## §4 ④ Restore + restore TEST

**Restore procedure** (target: a fresh VM home):

1. Clone the private backup repo via the PAT route.
2. Place T0 paths at their home locations (root files → `~/`, trees → their §1 paths).
3. **Re-key the 4 VM-only Apps** (Publisher/Reviewer/Gate/Lifecycle) — PEMs were never in the backup (§1); mint fresh keys, install as 0600 custody files.
4. Re-login consoles **token-first** (census §4 routes; browser-profile recovery = re-login, ¬ profile restore).
5. Re-clone lane repos from the T1 manifest (remote URL + sha), then apply T1 content bundles where they exist.
6. Verify: hash-compare restored T0 vs the export manifest = ∅ diffs before the VM is declared recovered.

**Restore TEST spec** (doctrine: redundancy TESTED ¬ present):

- Drill target = an **isolated scratch dir**, never the live home.
- Drill steps: export-format restore of T0 into the drill target → hash-compare T0 vs export manifest → restore **one** lane clone from its T1 record (clone at manifest sha + bundle apply).
- **Pass criteria:** T0 hash diff = ∅ ∧ the lane clone checks out at the manifest sha with its dirty-file hashes matching ∧ drill log written to the backup repo (`drills/`).
- **Drill cadence (event-gated):** after **each export-format change**, ∧ at a **quarterly** sweep. An untested backup is scored exactly as the census scores untested failover: **∅**.

## §5 ⑤ Size / cost

| tier | size basis | cost |
|---|---|---|
| T0 | ≈50MB full snapshot (§1 arithmetic); git deltas thereafter track churn (memory/convention edits = KBs–100s of KBs) | $0 |
| T1 | manifest-only ≈ KBs per export; content bundles gated ≤250MB/export (§1) | $0 |
| target | private repo on the existing account via the existing PAT path | $0 — ∅ new service, ∅ new credential |

Headroom: GitHub's recommended repo-size guidance is ~1GB (strongly recommended <1GB, problems >5GB). T0 ≈50MB = ~5% of the recommended ceiling *per full snapshot*, and git stores deltas, ¬ snapshots ⇒ at current churn the repo stays bounded for **decades**; the §1 T1 gates are what keep that true if lane content grows.

## §6 Risks / open questions (owner)

1. **Repo name** — `muse-vm-workspace-backup` proposed; owner's to confirm or replace.
2. **T1 content: yes/no** — recommendation: manifest-only in phase 1, bundles in phase 2 (§7). Owner may pull bundles forward.
3. **Sweep cadence** — weekly proposed for the §2(b) sweep; quarterly for the §4 drill. Owner-tunable.
4. **Same-account concentration** — the backup would live on the same GitHub account whose single PAT is itself census §3's SPOF: account loss takes primary ∧ backup together. Accepted at the $0 tier; a second-provider copy is a possible phase-3 question, ¬ scoped here.
5. **Plaintext-in-private-repo vs encrypted blobs** — this design defaults to plaintext inside the private repo, relying on the §3 scrub gate. Age-encrypted export is a build-time option at some restore complexity; owner's call if the threat model wants it.
6. **custom-skills size** — unmeasured in the §0 basis; bounded small by inspection, to be measured at build (affects only the §1 arithmetic's last decimal).

## §7 Recommendation

Build, **on the owner's word only**: (1) **T0-first** git export to the new private repo exactly as §§1–3 specify — allowlist-by-construction, event-gated at lane task-close + weekly sweep, fail-closed scrub gate; (2) **T1 manifest-only in phase 1**, content bundles in phase 2 behind the §1 gates; (3) the §4 restore drill is part of phase-1 acceptance — the backup counts as existing only once a drill has passed. Until the owner says go: **build nothing** — ∅ repo, ∅ mechanism, ∅ copies.
