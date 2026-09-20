# refTemplates Continuous Evaluation — Prior Planning → Execution

**Status:** ACTIVE — P0–P5 landed on PR #688; P6–P7 progressive  
**Directive:** All `refTemplates/00_` → `∞_` slots continuously repopulated, upgraded, evaluated, submodule-integrated.  
**Style:** BIUDL · recursive ELO · evidence-led · dual-gate  
**Related:** `PAPER2AGENT.md` · `RESEARCH-INTEGRATION-LANE.md` · `17_Papers/SOURCES.md`

---

## 1. What exists (scoring / tagging status)

| Asset | Path | Role |
|-------|------|------|
| Inventory | `scripts/ci/refTemplates_inventory.py` | Walk 00→∞; SOURCE.txt contract; JSONL |
| Score | `scripts/ci/refTemplates_score.py` | Tier A–D + L0–L6 fields + seed ELO |
| DeepWiki batch | `scripts/ci/refTemplates_deepwiki_batch.py` | Public MCP harvest (dry-run default) |
| Commit slice | `scripts/ci/refTemplates_commit_slice.py` | init→current considerations schema |
| Submodule integrity | `scripts/ci/submodule_integrity.py` | Governed smods gitlinks (expand to all = P2 residual) |
| Devin App reconcile | `scripts/agentic/reconcile_devin_wiki_access.py` | Programmatic App access for indexing eligibility |
| Repo-dev evaluation | `scripts/ci/repository_development_evaluation.py` | PR lifecycle manifests |
| Paper2Agent | `docs/ops/PAPER2AGENT.md` | GLM dense-feedback → monorepo mapping |

**DeepWiki levers (no private invent):**
1. `reconcile_devin_wiki_access.py --apply` — eligibility batch  
2. Public MCP `https://mcp.deepwiki.com/mcp`  
3. Boundary: access ≠ page indexed  

---

## 2. Architecture (landed)

```text
refTemplates/
├── 00_Index/ … 14_*
├── 15_Research_Repo_Templates/   # + opencode-research-papers, cactus-needle
├── 16_Org_Phased/
├── 17_Papers/                    # SOURCES = GitXiv successors + seeded research
└── smods/

scripts/ci/
├── refTemplates_inventory.py
├── refTemplates_score.py
├── refTemplates_commit_slice.py
└── refTemplates_deepwiki_batch.py
```

---

## 3. Recursive ELO layers (L0–L6)

| Layer | Input | Status |
|-------|-------|--------|
| L0 surface | stars, forks, license | prior / future GH API |
| L1 layout | SOURCE + README | score script |
| L2 agent surface | markers, OpenCode, MCP | score heuristic |
| L3 commit slice | init→current | commit_slice script |
| L4 DeepWiki | public MCP structure | deepwiki_batch |
| L5 papers | 17_Papers links | SOURCES seeded |
| L6 Actions fit | dual-gate, secret-free | score heuristic |

---

## 4. Papers + scanners (GitXiv deprecated)

**Successors:** Hugging Face Papers, PapersFlow (+ MCP skills), alphaXiv OpenResearch, opencode-research-papers (arXiv+OpenAlex, no keys), ArXivAtlas, Connected Papers, Elicit, Consensus.

**Operator seeds (2026-09-20):** Needle 3 / cactus-compute, GLM inference infra (Paper2Agent), opencode-research-papers, OpenResearch, PapersFlow, ArXivAtlas, Laya, TypeSafe System One waitlist, operator YT seed.

See `refTemplates/17_Papers/SOURCES.md`.

---

## 5. Execution order

| Phase | Work | Status |
|-------|------|--------|
| **P0** | Policy + 17_Papers + contracts | **DONE** |
| **P1** | inventory.py | **DONE** |
| **P2** | Expand submodule_integrity to all smods | residual |
| **P3** | score.py | **DONE** |
| **P4** | deepwiki_batch.py | **DONE** (dry-run default) |
| **P5** | commit_slice.py | **DONE** (schema + optional GH API) |
| **P6** | Thin arXiv/OpenAlex resolvers into citations/ | next |
| **P7** | Scheduled inventory+score; B→A on dual-gate only | next |

---

## 6. Non-goals

- Browser automation against Devin private UI  
- Undocumented DeepWiki index-write endpoints  
- Auto-merge pins without dual-gate + score threshold  
- Full recursive clone of every candidate on every CI run  

**Agent-Identity:** Grok (Administrator) CXO  
