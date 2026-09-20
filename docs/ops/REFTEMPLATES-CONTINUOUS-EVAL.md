# refTemplates Continuous Evaluation — Prior Planning → Execution

**Status:** ACTIVE planning + progressive implementation (PR #688+)  
**Directive:** All `refTemplates/00_` → `∞_` slots continuously repopulated, upgraded, evaluated, submodule-integrated.  
**Style:** BIUDL · recursive ELO · evidence-led · dual-gate

---

## 1. What exists today (scoring / tagging status)

| Asset | Path | Role | Gap |
|-------|------|------|-----|
| Submodule integrity | `scripts/ci/submodule_integrity.py` | Validates 4 governed `smods/` gitlinks | Does not cover full `smods/` set or `15_*` metadata |
| Repo-dev evaluation | `scripts/ci/repository_development_evaluation.py` | PR lifecycle manifests (schema v2) | Not yet pointed at template slots |
| RECON intel discovery | `scripts/ci/recon_intel_discovery.py` | GH↔GL topology (read-only) | Not template scoring |
| Devin App reconcile | `scripts/agentic/reconcile_devin_wiki_access.py` | **Programmatic** grant of Devin GitHub App access across accessible repos | Access ≠ DeepWiki content indexed; no batch wiki scrape yet |
| Repository observatory | `scripts/github/repository_observatory.py` | Repo surface observation | Extend for slot scoring |
| Pre-GitHub scripts | (historical, pre-init) | Parsed `.md` headers → category reports | Lost in rm-not-git-rm; behavior to be rebuilt under `scripts/ci/refTemplates_*` |

**DeepWiki today:** Manual “add repo → index” in Devin UI. Operator wants **programmatic** coverage of hundreds of repos each cycle.  
**Available levers:**
1. `reconcile_devin_wiki_access.py --apply` — make all accessible repos eligible for provider indexing (already in-tree).
2. Public DeepWiki MCP (`https://mcp.deepwiki.com/mcp`) — `read_wiki_structure` / `read_wiki_contents` / `ask_question` for **public** repos (no auth).
3. No documented private DeepWiki write/index API — do not invent one; stay on documented App access + public MCP.

---

## 2. Target architecture

```text
refTemplates/
├── 00_Index/ … ∞_*/          # continuous metadata + SOURCE + score cards
├── 15_Research_Repo_Templates/
├── 16_Org_Phased/
├── 17_Papers/                # NEW — cited research + implementation sources
│   ├── README.md
│   ├── SOURCES.md            # arxiv, gitxiv, ORCID, GRID.ac, Scholar, patents, Nature, …
│   ├── citations/            # one file or JSONL per work
│   └── scanners/             # notes + hooks for arxiv/gitxiv scanners
└── smods/                    # live pins only after dual-gate + score threshold

scripts/ci/
├── refTemplates_inventory.py     # walk 00→∞, assert SOURCE.txt, emit inventory JSONL
├── refTemplates_score.py         # tier A–D + ELO fields from multi-signal input
├── refTemplates_commit_slice.py  # init→current commit-window considerations
└── refTemplates_deepwiki_batch.py  # public MCP harvest + merge with App-access report

docs/ops/generated/refTemplates/
├── inventory.jsonl
├── scores.jsonl
├── elo-pairs.jsonl
└── deepwiki-batch-summary.json
```

---

## 3. Recursive ELO-style reviews

**Not** a single top-level star count. Pairwise + multi-slice:

| Layer | Input | Output |
|-------|-------|--------|
| L0 surface | stars, forks, license, last push, topics | coarse prior |
| L1 layout | README structure, src/tests/docs presence, CI files | scaffold fitness |
| L2 agent surface | AGENTS.md, MCP, OpenCode plugin, markers | agent-ready score |
| L3 commit slice | first N commits + recent M commits + midpoint | stability / intent drift |
| L4 DeepWiki | structure + contents summary (public MCP or provider wiki) | doc density / architecture clarity |
| L5 papers link | arxiv/gitxiv/ORCID/DOI cited in README or `17_Papers` | research grounding |
| L6 Actions fit | dual-gate compatibility, secret-free, shallow-pin safe | promote eligibility |

**ELO loop:** sample pairs within tier or across B→A candidates; update ratings from L1–L6 deltas; promote when rating + dual-gate green; demote when stale or secret-heavy.

**Commit-slice evaluation surface:** for each candidate, consider *repo init → current* as the integration evaluation window — not only HEAD. Flags: history rewrite risk, license change, dependency explosion, abandoned after initial scaffold.

---

## 4. Papers section (`17_Papers`)

Purpose: research **cited and used for implementation evaluation**, not a full bibliographic database.

| Source class | Examples | Use |
|--------------|----------|-----|
| Preprint | arXiv, GitXiv | method / pipeline papers behind templates |
| Identity | ORCID, GRID.ac | author / org grounding |
| Scholar | Google Scholar | citation checks |
| Formal | Nature, patents | high-weight implementation claims |
| Seeded | operator-supplied DOIs / URLs | first-class |

Each citation record: `id`, `title`, `url`, `source_class`, `linked_slots[]`, `eval_notes`, `collected_at`.

Scanners (progressive): thin wrappers that resolve arXiv abs/pdf and gitxiv pages into citation stubs; no bulk scrape without rate limits and dual-gate.

---

## 5. DeepWiki programmatic path (hundreds of repos)

1. **Eligibility batch:** scheduled run of `reconcile_devin_wiki_access.py --apply` (operator-token lane) so all non-archived accessible repos get Devin App access → provider-managed indexing *eligible*.
2. **Public content harvest:** for public repos, `refTemplates_deepwiki_batch.py` calls DeepWiki MCP `read_wiki_structure` (+ selective `read_wiki_contents`) → JSONL under `docs/ops/generated/refTemplates/`.
3. **Merge into score:** L4 signal in `refTemplates_score.py`.
4. **Boundary (documented in reconcile script):** App access does **not** prove a public DeepWiki page exists or refreshed. Report that explicitly; never invent a private index API.

---

## 6. Execution order (Make it So)

| Phase | Work | Gate |
|-------|------|------|
| **P0** | This doc + `17_Papers/` seed + expand inventory/score contracts | PR #688 dual-gate |
| **P1** | `refTemplates_inventory.py` — walk slots, SOURCE.txt required, emit JSONL | CI path filter `refTemplates/**` |
| **P2** | Expand `submodule_integrity.py` to all `smods/` in `.gitmodules` | dual-gate |
| **P3** | `refTemplates_score.py` — tier + multi-layer fields; seed ELO pairs from current 15_* |
| **P4** | `refTemplates_deepwiki_batch.py` — public MCP batch + merge report |
| **P5** | `refTemplates_commit_slice.py` — init→current considerations |
| **P6** | Papers scanners + ORCID/GRID hooks as thin resolvers |
| **P7** | Cadence: scheduled inventory+score; promote B→A only on dual-gate |

---

## 7. Non-goals

- Browser automation against Devin private UI
- Undocumented DeepWiki index-write endpoints
- Auto-merge of submodule pins without dual-gate + score threshold
- Full recursive clone of every candidate on every CI run

---

**Agent-Identity:** Grok (Administrator) CXO  
**Show-me:** existing Devin reconcile + submodule integrity + repo-dev eval are the spine; continuous ELO + papers + DeepWiki batch are the expansion.  
