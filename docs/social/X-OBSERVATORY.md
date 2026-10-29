# Observation Planes — Surface Map & the X Observatory

Owner question, 2026-10-29: what are we observing, on which surfaces,
with what distinctions — and how do the planes nest into one graph?
This doc is the map. Every status below was verified firsthand at
writing (live API / repo state); anything not yet built is labelled
PLANNED or NOT ESTABLISHED, never implied.

## 1. The model: planes, provenance, distinction

An **Observation Plane** is one surface's signal set, collected by one
collector into one canonical JSON index plus a generated Markdown
projection. Records carry **provenance** (which signals captured them)
and a deterministic **classification** (inference, always labelled with
its basis). Signals are research signals — never adoption orders.

Planes nest as a graph, not a tree: a record in one plane can be an
author/owner node in another (a starred repo's author is a followed
account; an X post links a GitHub repo; a paper's code lands in a
starred repo). Cross-plane edges are recorded as identifiers
(`github:repository:…`, `x:tweet:…`, `arxiv:…`), which is what makes
the whole thing a tensor/graph instead of a pile of lists.

## 2. GitHub plane — EXISTING (Repository Observatory)

Collector `scripts/github/repository_observatory.py`, workflow
`repository-observatory.yml` (daily 04:17Z + dispatch), canonical
`workspace/llm_map/repositories/repository-index.json`, projection
`docs/repositories/matrix.md`. Counts at 2026-10-29 writing: owned 692,
starred 3128+, watching 128, issue-filed 1.

| Surface | Signal | Status |
|---|---|---|
| Owned repos | `owned` (forks = role + upstream, not a separate list) | LIVE |
| Stars (by owner) | `starred` | LIVE |
| Watch / subscriptions | `watching` (token = `OPERATOR_GITHUB_TOKEN`) | LIVE |
| Research issues filed | `issue` (intake leg, observatory-intake/v1) | LIVE |
| Delta | added / removed / provenance-changed per snapshot | LIVE (v2.3) |
| Authors of starred/watched repos | owner field on each record; no author roll-up yet | PARTIAL |
| Following (accounts) → their repos/stars | — | NOT CAPTURED |
| Followers | count only, in a stale 2026-10-22 doc | NOT CAPTURED as records |
| Topics harvest | topics exist per-repo; no topic-first index or GitHub topic search harvest | PLANNED (§5) |
| Explore / trending | — | PLANNED (§5) |
| Search harvest (code/repo queries) | ad hoc via PAT only | PLANNED (§5) |
| Reverse SEO (term discovery) | — | PLANNED (§5) |

## 3. X plane — BUILT HERE (Social Observatory)

**Is X connected to Muse's connectors? No.** Verified 2026-10-29:
no X/Twitter connector exists in the Muse catalog (Threads and
Instagram are separate surfaces), no X login is saved, and no X secret
is provisioned in the repo Actions store (58 names checked). The
browser route is not programmatic and is not used.

**Programmatic route (the only one):** X API v2 with an OAuth 2.0
*user-context* token — app-only Bearer is rejected by both endpoints:

| Endpoint | Scope | Notes |
|---|---|---|
| `GET /2/users/me` | users.read | resolves the account |
| `GET /2/users/{id}/liked_tweets` | like.read | likes are public on X |
| `GET /2/users/{id}/bookmarks` | bookmark.read | **private on X; caps at 800 most recent** |

Collector `scripts/social/x_harvest.py` + workflow
`x-observatory.yml` (weekly Wed 05:23Z + dispatch) → canonical
`workspace/llm_map/social/x-index.json`, projection
`docs/social/matrix.md`. Tests: `scripts/social/test_x_harvest.py`.

**Distinction (owner requirement):** every record is classified
`plane: marketing | personal`:

- `marketing` — deterministic fleet-signal terms (`termux`, `monorepo`,
  `timerloggedout`, `4n0n`, `t3mpu`/`t3πmu`, `tempux`, `help-wanted`,
  `monorep0`) or the author is the account owner (project posts).
- `personal` — no marketing signal; recorded as inference
  (`plane_basis: default_no_marketing_signal`), never as fact.
- Owner overrides in `ops/social/x-plane-overrides.json` always win
  (`plane_basis: owner_override`).

**Privacy rule:** bookmark records are **metadata-only** (id, author,
URL, timestamps, public metrics, one-way text hash) — the tweet text
is never committed to this public repo. Like records (public on X)
may carry a ≤280-char excerpt. Signals merge per tweet
(`[like]`, `[bookmark]`, both), with the same snapshot-delta pattern
as the Repository Observatory.

**Status: pipeline live, harvest DEFERRED.** The collector is
fail-soft: without the token it prints DEFER and exits 0, writing
nothing. **Provisioning item (owner):** create an X developer app,
run one OAuth 2.0 PKCE authorization for the account with scopes
`bookmark.read like.read tweet.read users.read offline.access`, and
store the user token as Actions secret `X_OAUTH2_USER_TOKEN`
(names-only; values never transit chat). Token expiry/refresh is
handled by re-authorization until a refresh worker is justified.
Account handle: NOT ESTABLISHED (no signed-in or API read has named
it yet; the first successful harvest records it in the index).

## 4. Other surfaces — status

| Surface | What exists | Observation status |
|---|---|---|
| arXiv | Citation records under `refTemplates/17_Papers/`; source-class resolver in `docs/ops/RESEARCH-SOURCES.md` | Citations only; no harvest collector — PLANNED |
| PapersWithCode | 0 hits in repo; successor routes named in RESEARCH-SOURCES (HF Papers, PapersFlow, alphaXiv) | NOT ESTABLISHED — revive via successors, GitXiv deprecated |
| HuggingFace | Hub API wired for quota/availability (PR #1878, `huggingface.hub_api`); saved Muse login exists | Provider surface LIVE; papers/models observation harvest NOT BUILT |
| Nature / journals | DOI source class in RESEARCH-SOURCES | Citation route only |
| YouTube | vidIQ connector exists in Muse (channel/video research); 2MinutePapers + AI Search channels named by owner as sources | Connector present, no repo pipeline; channel-description intake = manual seed route (research issue) |
| Muse Feed | Owner-imported discussion surface (Muse-side) | Muse-side only; items enter the repo only as filed research seeds/issues |
| Google Drive (DreamBeans shares) | Owner shares land via Drive connector (Muse-side) | Muse-side only; no repo collector |
| Owner screenshots | Media uploads (Muse-side) | Evidence inputs, transcribed into repo records when acted on |
| Stack Overflow for Agents | Connected (custom connector, read) | LIVE Muse-side |
| Threads / Instagram / Facebook | Connectors exist (Muse-side) | Not yet observatory planes — same pattern as X when wanted |

## 5. PLANNED extensions (Active Extensive Search Procurement)

Staged, in priority order; each lands as its own PR with the same
collector+index+projection shape:

1. **Following graph (GitHub):** `/user/following` + per-author repos
   and stars-received — turns the flat index into the author graph
   the owner sketched (Authors → Repos / Forks / Following → Stars).
2. **Topics harvest:** topic-first inverted index from the existing
   3,577 records, then GitHub topic search for net-new repos in the
   fleet's topic set.
3. **Explore/trending watch:** weekly snapshot of GitHub Explore
   trending per fleet language set, delta vs the index.
4. **Reverse SEO / term discovery:** mine titles/descriptions/topics
   of high-signal records (starred + liked + bookmarked) for novel
   term combinations; feed them back as search queries for (2)/(3)
   and as X search seeds. Output = candidate terms list, human/owner
   promoted, never auto-adopted.
5. **arXiv harvest:** arXiv API by fleet categories (cs.AI/cs.CL/
   cs.SE …) with the same seed flow (paper → code link = cross-plane
   edge to the GitHub plane).
6. **Cross-plane link pass:** resolve URLs inside X records and paper
   records to GitHub records; emit edges into both indexes.

Prioritization rule (owner, 2026-10-29): accelerate `termux-monorepo`
self-improvement first; expansion planes land only when they feed it.
The X harvest is the current priority plane (§3) — built, awaiting
its provisioning item.
