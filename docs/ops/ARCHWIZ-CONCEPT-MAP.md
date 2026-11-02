# ArchWiz Concept Map — scoping record (Graph lane, 2026-11-01)

Owner direction via main: address the project profiles in Archwiz.py as a concept
map — use + improve — as the basis for building custom Projects ∧ user projects
(like challenges); some require the encryption; build method = the dispatch
build method. PLANNING PASS ONLY — ∅ built.

All repo facts firsthand PAT-API @master 2026-11-01 (this lane).

## 1. The map as it exists (proto-concept-map)

### Cockpit layer
- `archwiz/archwiz.py` (7,457B) — Termux TUI cockpit/dispatcher shell; imports
  paths from `archwiz/config.py` only. Recon verdict (2026-10-30, ae45b8c4):
  FIT as single operator/UI surface ∧ UNFIT as provider-control layer as-is;
  last real change 2026-09-30 (PR #937); provider names inside = ∅.
- `archwiz/config.py` — path constants (ARCHWIZ_DIR, WORKSPACE_DIR, …).
  **No profile loader exists in-repo** (grep: profiles ¬ referenced).

### Profile layer — `.config/llm_map/profiles/` (7 profiles, ALL scan-scopes)
Profile semantics as-is: **profile = named scope = {include[], exclude[]} path-set
over the device-workspace universe** (llm_map mapping), NOT a project/task profile.

| profile | shape | include core | notes |
|---|---|---|---|
| archwiz.json | self+workspace | deepcli, deepcli-tui, termux-multi-agent, harmony_hub, archwiz, workspace, sandbox… | the cockpit's own universe |
| mapper.json | core + strict excludes | workspace/llm_map + 5 cores | exclude list encodes secrets hygiene: `deepseek_api_key*`, `.npmrc*`, `.cache/*`, `*/.git/*` |
| full_recon.json | broad recon | mapper core + src, .hermes slices | exclude has duplicated `.cargo/*` entries (drift) |
| deepseek.json | provider slice | deepseek-cli, deepseek_harvest_work + cores | |
| truth.json | minimal core | llm_map + 4 cores, ∅ excludes | the "core-only" pattern |
| quantum.json | single-project | one path: QuanTM harvest | the single-project scope pattern |
| regulatory_matrix.json | external intake | `~/storage/downloads/` only | scope over non-repo space |

### Index family (the proto-map proper)
- `CONCEPT_INDEX.md` (5,085B) — concepts × status {Implemented · Reserved ·
  Not built} + tool table (locations outside repo: ~/workspace/llm_map etc.).
- `METHODOLOGY_INDEX.md` (6,279B) — attempt lineages (A/B/C/D per method, what stuck).
- `TOOL_INDEX.md` (3,327B) · `POINTER_INDEX.md` (1,105B) + `pointer_index.json`
  (823,370B) + `pointer_inverted.json` (756,635B) — CID-style pointer system.
- `index_registry.json` (230,275B) — a bare list of 1,237 entries, ∅ schema header.
- `DATA_FLOW_MANIFEST.md` (1.55MB) — generated flow manifest.
- `context_relationships/` — largest ACTIVE subpackage: build_index.py (21KB),
  compiler.py (20KB), query.py (19KB), source_collector.py (17KB),
  evidence_matrix.py (15KB), temporal.py + temporal_query.py,
  **github_collector.py (39.6KB) = the GitHub-side bridge**.
- `graph_tensors/` — adjacency/similarity matrices (ast_sim_matrix.csv 3.27MB,
  file_deps_adj, session_codex_inc; csv+npz pairs). ∅ edge from profiles to tensors today.

### The generalization (the concept-map move)
`profile.scope` generalizes from PATH-sets to the PROJECT UNIVERSE
{repos · issue classes · lanes · artifact stores} with the same algebra:
include/exclude · core+satellite (truth/mapper) · single-project (quantum) ·
external-intake (regulatory_matrix). Project classes bind to scope patterns:

| class | scope pattern | universe |
|---|---|---|
| custom Projects (Repo Replay, Repo-Story, fleet systems) | core+satellite | repo(s) + owning lane tree + artifact store |
| user projects — challenges (D0–D5/AMD…) | single-project per challenge | challenge repo/dir + entry artifacts + deadline record |
| user projects — certifications | core+satellite | cert KB + progress ledger + exam records |
| artifacts (deliverables) | external-intake + slice | artifact store + source project scope |

## 2. Class × encryption matrix

Pattern of record = tonight's owner-records age store (PR #3550): envelope
`index.json` = plaintext metadata (indexable) + per-record bodies as `age`
ciphertext, keys keyed BY CLASS, private halves in owner's vault only.
Rule: **encryption attaches to the record BODY class, never wholesale to a
project class; the envelope stays plaintext everywhere.**

| class | envelope | body | key class |
|---|---|---|---|
| challenges | plaintext | plaintext (submissions are public by design) — EXCEPT pre-submission strategy/credential-adjacent notes ⇒ encrypted | challenges-notes |
| certifications | plaintext | ENCRYPTED (exam content/answers — integrity) | certifications |
| custom Projects | plaintext | mixed: repo content plaintext; owner-only decisions/bets bodies ENCRYPTED (owner-records decisions class) | decisions (existing) |
| user projects (personal) | plaintext | ENCRYPTED by default (personal data) | user-projects |
| artifacts | plaintext | plaintext (deliverables + provenance stamps); embedded secrets NEVER (names-only rule) | — |

## 3. Dispatch build method — end-to-end binding

Build method = the fleet dispatch method (routed dispatch + stamps), bound:

1. **Intake** — Issue Form `project-task` (design of record 2026-10-30,
   owner-chosen; verified tonight: `.github/ISSUE_TEMPLATE/` has 11 forms,
   ∅ project-task/challenge/certification — still unbuilt). Fields: scope
   dropdown ← profile scopes (§1 project classes) · task · target repo ·
   profile · done-evidence; auto-labels by scope.
2. **Resolve** — workflow `on: issues[opened]` + form label ⇒ parse ⇒
   scope → project profile → owning lane (routing table = §1 map, machine
   form in S2 loader).
3. **Dispatch** — routed-dispatch method: stamp {task class · arm/provider ·
   model · run id · outcome} fanned out to scoring intakes
   (`scripts/dispatch/stamp_fanout.py`, stamps @ experiments/doe/routed-
   dispatch/stamps/); NO hard-select (rotation across arms; single-arm only
   when constraints bind, recorded as constrained). Constrained/legacy arms
   ride provider-command-dispatch. ArchWiz-side ancestor:
   `archwiz/dispatch_pipeline.py` (event-sourced dispatcher registry) — the
   concept ancestor, ¬ the runtime.
4. **Nested-family tracking** — parent project issue = family root; task
   issues = children (authored refs); linkage measured by graph-matrix
   census cells (I↔I one-way, P→I) — this lane's matrix is the family's
   integrity instrument; Tracking lane consumes for rollup.
5. **Done-evidence** — PR# + merge SHA oracle-verified on the parent issue;
   routing receipt comment at dispatch time (design of record).

## 4. Improvement list for the map itself

vs the 2026-10-30 recon verdicts + tonight's firsthand pass:

1. **Profiles are scan-scopes, not project scopes** — ∅ profile exists for any
   project class; scopes point at device paths (`~/storage/downloads/`) that
   repo CI cannot resolve. ⇒ NEW project-scope profile family (§1 table),
   separate directory; do NOT overload the scan profiles.
2. **∅ in-repo profile consumer** — config.py loads no profiles; consumers are
   device-side llm_map tools. ⇒ schema + resolver land with the family (S2).
3. **Index staleness** — CONCEPT/METHODOLOGY indexes are session-era
   (2026-06-14 generation stamps); index_registry = bare 1,237-list, ∅ schema;
   DATA_FLOW_MANIFEST 1.5MB hand-era. ⇒ regenerate under event-driven
   automation (graph-matrix twin pattern) ∨ explicitly mark archival.
4. **Ride context_relationships, not the TUI** — it is the largest active
   subpackage and holds the GitHub bridge (github_collector); archwiz.py is a
   179-line cockpit frozen since 2026-09-30. The map's runtime edge belongs there.
5. **Promote mapper's secret-excludes to a stated rule** — the exclude list
   already encodes scope-safety (keys, .npmrc); make it a named concept-map
   rule so project scopes inherit it.
6. **Profile↔tensor edge missing** — graph_tensors exist unlinked; in the map,
   a profile = a node subset = a tensor slice; add that edge.
7. **Vestigial/duplicate surfaces** — `providers/` vestigial (recon);
   live_view.py ≡ live_view_original.py (identical 9,670B). Freeze law:
   archive additively, never delete.
8. **full_recon exclude duplication** (`.cargo/*` ×3) — scope drift; schema
   validation in S2 catches this class.

## 5. Build plan — PR-sized steps (∅ built in this pass)

- **S1** Docs+schema PR: `docs/ops/ARCHWIZ-CONCEPT-MAP.md` (this record) +
  `ops/projects/profile.schema.json`. No code, no workflow perms.
- **S2** Project-scope profiles v0 (challenges · certifications ·
  custom-projects · user-projects · artifacts) under
  `.config/llm_map/profiles/projects/` + `scripts/projects/profile_resolve.py`
  + tests (schema validation incl. secret-exclude rule).
- **S3** Intake PR: `.github/ISSUE_TEMPLATE/project-task.yml` per design of
  record (scope dropdown ← S2 profiles; auto-labels).
- **S4** Dispatch workflow PR (PAT route, workflow-file): `issues[opened]` ⇒
  parse ⇒ resolve (S2) ⇒ stamp + routed/command dispatch ⇒ routing-receipt
  comment. Swarm-token authored.
- **S5** Family tracking: parent/child linking convention doc + graph-matrix
  census already measures the cells; Tracking-lane consumption coordinated
  via mgr (no new machinery expected).
- **S6** Encryption leg: generalize owner_records.py machinery —
  `scripts/projects/envelope.py`, class keys {certifications · user-projects ·
  challenges-notes} provisioned owner-side (public recipients only in-repo),
  bodies encrypted, envelope plaintext.

Dependencies: S1→S2→S3→S4 chain; S5 rides S3; S6 independent after S2.

## 6. Obsidian requirement (owner ruling 2026-11-01) — placement

Owner ruling via main: **Obsidian is required IN OUR SCHEMAS — separate from
D1.** "This is where project profiles are important." The D1 fold
(FEATURES.md) is a downstream consumer of this requirement, ¬ its home.

Placement (landed with this record, S1):
- **File:** `ops/projects/profile.schema.json` (`project-profile/v1`).
- **Field:** `obsidian` — a top-level profile component, sibling of `scope`.
- **Required semantics:** `obsidian` ∈ the schema's root `required[]`
  (alongside name · class · scope): a profile WITHOUT a declared Obsidian
  surface is invalid — not defaulted, not nullable. Inside the component,
  `vault` + `mode` are themselves required; `mode` ∈ {vault-root ·
  vault-folder · linked} forces every project to state HOW its knowledge
  lives in Obsidian (its own vault, a declared folder of a shared vault, or
  a linked external vault). Optional subfields: folder · canvas ·
  templates · sync {repo-mirrored · local-only · server}. Fleet surface of
  record: `bin/obsidian_server.py` (sync=server names it).
- Rationale in one line: repos/issues/lanes are where a project's WORK is;
  the vault is where its KNOWLEDGE is — a profile that scopes only work is
  half a profile.

## 7. FSRS-for-Agents placement (paired ruling, stated ¬ assumed)

The SR rulings travel with the Obsidian requirement; placement is SPLIT:
- **Declaration: YES, this schema.** `sr` is an optional component of the
  profile: the profile declares its spaced-repetition POLICY {enabled ·
  algorithm ∈ fsrs|sm-2 · corpus · retention_target}. Corpus defaults to
  `obsidian` — review items derive from the profile's declared vault (term
  banks, study notes, flagged sections), which is exactly why the pairing
  travels: no vault declaration ⇒ no SR corpus ⇒ the two requirements are
  one requirement seen from two sides.
- **Engine: NO, not per-profile.** The scheduler implementation is a shared
  service (py-fsrs agent core + ts-fsrs UX layer per owner rulings
  2026-10-30; SM-2 remains the legitimate baseline + eval comparison). A
  profile names its algorithm and corpus; it never carries scheduler code.
  Engine home = the llm_map/agent plane, consumed by D1 (FEATURES.md fold)
  as a downstream consumer — same consumer relation D1 holds to §6.
