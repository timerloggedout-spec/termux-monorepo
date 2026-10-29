# Cross-Plane Graph — an additional view over the observation planes

Owner framing, 2026-10-29: "extend & optimize & properly graph matrice
the resources in their appropriately nested domains", priority =
accelerating termux-monorepo self-improvement. This lane (split from
the Repository Observatory lane, chat e3d17643) builds that layer —
**as an additional view to the existing planes, not a new plane and
never a source of truth.** Every plane keeps its own collector, its own
canonical index, and its single writer; this view is regenerated from
their committed indexes by `scripts/graph/cross_plane_link.py`
(offline, zero API calls) and can be rebuilt or deleted at any time
without losing information.

## 1. Why a view, and why now

`docs/social/X-OBSERVATORY.md` §1 already named the identifier form
(`github:repository:…`, `x:tweet:…`, `arxiv:…`) — and recon
(2026-10-29) found the planes already *emit* it: repository-index
record `id` is `github:repository:{owner}/{repo}`, x-index record `id`
is `x:tweet:{tweet_id}`, research-seed `seed_id` is
`github:research-seed:{owner}/{repo}`. What was missing was anything
that consumes those ids across planes. This view is that consumer.

## 2. Entity ids

Emitted by the planes (consumed verbatim, never reminted):
`github:repository:{owner}/{repo}`, `x:tweet:{id}`,
`github:research-seed:{owner}/{repo}`, `research-seed:{slug}`.

Minted by this view only for entities the planes name without ids:
`github:user:{login}`, `x:user:{handle}`, `topic:{slug}`,
`domain:{slug}`, and (reserved, when those indexes land)
`paper:arxiv:{id}`, `paper:doi:{doi}`, `hf:model:{id}`,
`youtube:video:{id}`, `youtube:channel:{id}`.

## 3. Edges (graph-edges/v1)

One JSON object per line in `workspace/llm_map/graph/edges.jsonl`:
`{src, dst, type, evidence:{plane, record, method, observed_at}}`
(schema: `docs/graph/graph-edges.schema.json`). Direction is
actor-first — an edge reads as a sentence. Generation is
deterministic: sorted, deduped, hash-pinned in
`workspace/llm_map/graph/graph-index.json` (`graph-index/v1`, with
per-source observed_at + snapshot_hash, so a stale source plane is
visible in the view rather than hidden by it).

v1 types, all derived from committed records (method = the field the
edge was derived from, recorded per edge):

| Type | From → To | Source |
|---|---|---|
| `owned` / `starred` / `watching` | account user → repo | repository-index `provenance` |
| `authored_by` | repo → owner user | record `owner` field (no author roll-up existed before this view) |
| `fork_of` | fork repo → parent repo | record `upstream` field; seed `local_fork` evidence |
| `about_topic` | repo → `topic:` | record `topics` |
| `in_domain` | repo / seed → `domain:` | `classification.domains` (the nesting axis) |
| `mentions_repo` | tweet / seed / intake → repo | like-excerpt GitHub URLs resolved against the index; seed `repos[]`; `issue_intake.upstream` |
| `upstream` | seed → repo | seed `canonical_upstream` |
| `liked` / `bookmarked` | X account user → tweet | x-index `signals` (emitted once the X harvest lands) |
| reserved: `follows`, `implements`, `cites`, `same_author_as` | — | land with the Following Graph / Papers indexes; `same_author_as` only on explicit evidence, never name-matching |

Honest blanks at first pass (2026-10-29 index, observed
2026-10-29T10:55Z): `fork_of` = 1 — the repository index carries
`upstream: null` on all 968 fork records, so the only fork edge is the
one a research seed evidences (Gravitee). The extractor is ready the
day the Observatory records upstreams. X edges = 0 — the X index is
`awaiting_token` with 0 records; the code path is tested and lands
edges on the first harvest. Papers edges = 0 — no papers index exists
yet (Papers Surfaces lane, chat efb9429b, proposes one with a native
HF `githubRepo` field, which becomes `implements`).

First pass totals: 25,179 edges over 3,639 repos / 2,012 distinct
authors / 4,994 distinct topics — the author roll-up alone is the
priority queue the Following Graph lane (8421d0c7) caps and rotates
against.

## 4. Nesting & the tensor view

Domains nest, they do not flatten: GitHub (user ↔ repo ↔ topic/domain),
X (user ↔ tweet), papers (paper ↔ author ↔ code), seeds/intake as the
bridge records that already point across. Cross-plane paths are then
plain graph walks, e.g. `x:user --liked--> x:tweet --mentions_repo-->
github:repository --authored_by--> github:user --follows--> …`.
Per edge type, edges form one adjacency matrix (src × dst); the set of
typed matrices is the tensor view — queries pick the slices they need
instead of a merged mega-record per entity.

## 5. Privacy & rules

- X bookmark records are metadata-only in their plane; this pass never
  reads or stores tweet text. URL extraction runs only over a like
  record's public excerpt, and edges store ids, never text.
- Signals are research signals, never adoption orders (Observatory rule).
- Coordination: schema/edge-type changes are announced to the
  Observatory lane via `[MUSEai]@{role:{cross-plane-graph}}` GitHub
  comments before merge, per the lane boundary of 2026-10-28.
- Runtime: `.github/workflows/cross-plane-graph.yml` (weekly +
  dispatch + push on plane-index paths) regenerates the view on
  GitHub and commits any delta directly, like the other observatory
  workflows. The VM authors and pushes only; it hosts nothing.

## 6. Challenge plane (v2, 2026-10-29) — participant/competitor OSINT import

The Competitive Hackathons structures join the view as a *challenge
plane*, imported read-only from `ops/challenge/coordinator.json`
(events / participants / competitors / projects / judges / organizers,
per `docs/ops/CHALLENGE-SCHEMA.md` + `docs/ops/CHALLENGE-OSINT.md`).
**No migration:** the structures stay where their lanes keep them
(see §7). The link pass is shape-tolerant (the participant_event.py
precedent) and derives participant keys the same way the Neon
participant store does (first of id/handle/username/name/team_name/url,
else a sha256 of the canonical record).

Entities: `challenge:event:{id}`, `challenge:participant:{event}/{key}`,
`challenge:project:{event}/{slug}`, `challenge:judge:{slug}`,
`challenge:organizer:{slug}`.
Edges: participant `--competes_in-->` event; participant
`--entered_with-->` project `--submitted_to-->` event; project
`--hosted_at-->` `github:repository:` (from its GitHub URL — the seam
where the challenge subgraph joins the GitHub plane); judge
`--judges-->` event; organizer `--organizes-->` event; participant
`--won-->` past event (from `past_wins[]`).

Guardrails, hard-coded in the importer and covered by tests:
- `metrics_internal` is **never read** — win-probability and friends
  render only in the Admin panel, never in this public view.
- `same_author_as` is emitted only from a participant's own published
  `persona.public_links.github` (explicit evidence) — never from name
  matching. 4n0n unlinkability is untouched; our entrants carry no such
  public link by design.
- Recruitment fields are observation-only in the source and stay so
  here: the view records competition structure, not candidates.

## 7. Lane responsibility (resolved 2026-10-29)

| Structure | Responsible lane | This view |
|---|---|---|
| coordinator.json records (single writer) | challenge-entries `a33d3ca1` | read-only import |
| OSINT coverage + page snapshots (PR #2234) | assistant seat `a440bcb2` | not imported (hashes are not entities) |
| Neon participant store (schema/writer) | database-specialist `e3055a9c` | key rule mirrored, store untouched |
| Participant scoring pattern | moneyball-plane `cd195597` | not imported (metrics_internal excluded) |
| Repository / X plane indexes | Observatory `e3d17643` / X Observatory | read-only import |
| **Edges, graph schema, this doc, link pass** | **cross-plane-graph `6f7170c0`** | **owns the view only** |

Adding an observation consumer never moves a structure: producers keep
their files, consumers derive views, and every view is regenerable.
