# Research Silo Delphi — Independent Outcome Stovepipes

**Status:** ACTIVE — validated + rebased onto current master 2026-10-27 (validation lane; original branch feat/research-silo-delphi-stovepipes was 756 behind master, no PR)  
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

Then extend with 🧬 evolutionary selections & mixes (`rnd` · `selected` · `control`).

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
| `research.3rdcore-research-project-template` | 3rdCore-Research_Project_Template | Lightning + Hydra + WandB |
| `research.dicklesworthstone-agentic-flywheel` | dicklesworthstone-agentic-flywheel | Agentic flywheel stack (metadata-only) |
| `research.opencode-research-papers` | opencode-research-papers | OpenCode research papers |
| `research.cactus-needle` | cactus-needle | Needle research |

All listed in `ops/delphi/research-silos.json` with paths and upstream URLs.

---

## 3. How many independent results does the current schema expect?

| Layer | Count | Attribution |
|-------|-------|-------------|
| **Baseline silo RFPs** | **12** | One result stream per research silo (`research.<slot>`) |
| Delphi free-tier surfaces (existing) | 18 in `surfaces.json` (verified 2026-10-27) | Orthogonal — quota/deploy/model/partner; not research-template comparison |
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
7. **Surface-id case rule:** ids are lowercase (`gate.py` `_SURF_RE = ^[a-z0-9][a-z0-9._-]{0,63}$` silently drops uppercase ids from flywheel/tribute signals). The 3rdCore slot/path keep upstream case; its surface_id is `research.3rdcore-research-project-template`.

## 4b. Gate filing map (verified against master gate.py + delphi-rfp.yml, 2026-10-27)

Research silos are **not** in `ops/delphi/surfaces.json` (18 quota surfaces). Filing works because the gate scores unknown ids as synthetic unsourced surfaces (`surface_from_issue`: sourced=false, fit=3, headroom=3, horizon=H2) — so the gate score is an **admission rubric only**. The research comparison axes (§1) are not gate-scored; they are recorded post-hoc in the RFP ledger + `delphi:outcomes` (rules in `research-silos.json`).

Per RFP: `surface_id` = silo.id exactly · `lane` = `other` (form has no research option) · `free_quota` = "none — research template validation lane; no quota surface (evidence: slot SOURCE.txt)" · `reset_and_zone` = "none — no quota reset; parked recheck per panel award defaults" · `auth_from_actions` = "none needed" · `lock_in` = 1.

**Veto trap:** `surface_from_issue` flags `card_required` by substring search over the free_quota + failure_modes text — any occurrence of the payment-instrument word, even negated, triggers the cost_auditor money veto (score capped at 4). Keep that word out of both fields in research RFPs.

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
