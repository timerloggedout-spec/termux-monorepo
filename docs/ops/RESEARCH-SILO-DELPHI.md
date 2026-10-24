# Research Silo Delphi — Independent Outcome Stovepipes

**Status:** ACTIVE (feat/research-silo-delphi-stovepipes)  
**Machine config:** `ops/delphi/research-silos.json`  
**Parent:** `docs/ops/RESEARCH-INTEGRATION-LANE.md` · `docs/ops/DELPHI-ORACLE-RFP-GATE.md`  
**Directive:** BIUDL · YOLO · adaptive-wait · evidence-led · dual-gate

---

## 1. Goal

Fold, adapt, and wire every tier-A research template under `refTemplates/15_Research_Repo_Templates/` into its **own** Proposal → Delphi → cycle stovepipe so we can compare:

1. **Produced output results (validated)**
2. **Feature extractions**
3. **Consensus implementation**

…independently, with no cross-silo score leakage.

Baseline cycle schema:

```text
RFP{1st_improve_request_cycle on RFP itself} → Delphi (oracle + blind panel) → award → validated comparison → flywheel
```

Then extend with 🧬 evolutionary selections & mixes (`rnd` · `specifically_selected` · `control`).

---

## 2. The 12 silos (baseline)

| Silo id | Slot | Upstream role |
|---------|------|---------------|
| `research.jogyo-research-lab` | jogyo-research-lab | Primary exemplar (Gyoshu/Jogyo/Baksa) |
| `research.docxology-template` | docxology-template | Reproducible monorepo + 17-stage |
| `research.yy-project-template` | yy-project-template | Classic research layout (uv) |
| `research.buoyancy99-research-template` | buoyancy99-research-template | ML research template |
| `research.yp-edu-research-project-template` | yp-edu-research-project-template | KISS agent-ready |
| `research.seunghyukoh-research-template` | seunghyukoh-research-template | AI research batteries |
| `research.irudik-repo-template` | irudik-repo-template | Academic Make + multi-lang |
| `research.jdingel-projecttemplate` | jdingel-projecttemplate | Task-based research logbook |
| `research.3rdCore-Research_Project_Template` | 3rdCore-Research_Project_Template | Lightning + Hydra + WandB |
| `research.dicklesworthstone-agentic-flywheel` | dicklesworthstone-agentic-flywheel | Agentic flywheel stack (metadata-only) |
| `research.opencode-research-papers` | opencode-research-papers | OpenCode research papers |
| `research.cactus-needle` | cactus-needle | Needle research |

All listed in `ops/delphi/research-silos.json` with paths and upstream URLs.

---

## 3. How many independent results does the current schema expect?

| Layer | Count | Attribution |
|-------|-------|-------------|
| **Baseline silo RFPs** | **12** | One result stream per research silo (`research.<slot>`) |
| Delphi free-tier surfaces (existing) | ~18 in `surfaces.json` | Orthogonal — quota/deploy/model/partner; not research-template comparison |
| Shadow-lane mappings | 2 wired today | github.native_ledger, turso.free (empty) |
| **Evolutionary extension** | 12 × (1 + N) | N = variants (`rnd`, `selected`, `control`) → up to **48** independent streams when fully extended |

**Current schema answer:** the Delphi Oracle RFP gate scores **surfaces**. Research silos are parallel metadata + RFP lanes that **reuse** the same gate, 5-role panel, ledger, and flywheel. Each silo files its own `delphi:rfp` with `surface_id = research.<slot>`. Expected independent validated-outcome streams for the research class = **12** (baseline) before evolutionary mixes.

---

## 4. Wiring rules

1. File one RFP per silo for the baseline improve-cycle (`surface_id` must match silo.id).
2. Comparison axes live in the RFP ledger comment + `delphi:outcomes` board (no shared aggregate score).
3. Evolutionary variants append `.rnd` | `.selected` | `.control` to the silo id and file separate RFPs.
4. Dual-gate + evidence-led still govern any live pin under `refTemplates/smods/`.
5. Reuse `panel.json` roles, `scripts/delphi/gate.py`, and the existing flywheel — do **not** fork the scoring engine.
6. Metadata-first; no recursive clone or upstream installer execution (especially dicklesworthstone).

---

## 5. First cycle focus

Start with **comparing produced output results validated; feature extractions; consensus implementation** across the 12 silos under the shared improve-request cycle on the RFP schema itself. That produces the first 12 independent result streams and calibrates the panel for research-shaped work.

Then open evolutionary variant RFPs (🧬 mixes) per silo.

---

## 6. Non-goals

- Auto-merge or auto-promote research pins without dual-gate + task outcome
- Cross-silo score aggregation that collapses attribution
- Running upstream installers inside CI or the monorepo
- Treating research silos as free-tier quota surfaces (they are validation / pattern stovepipes)

---

**Agent-Identity:** Grok (Administrator) CXO  
**Style:** BIUDL · Continuous Fully Automated Agentic Development · adaptive-wait · evidence-led  
