# Research Integration Lane

**Status:** ACTIVE (feat/refTemplates-research-consolidate / PR #688 + Research Silo Delphi, validated/rebased 2026-10-27)  
**Locator term:** “Jogyo” / research-lab class = the **entire** research-reference set, not a single upstream.

---

## 1. Are the researchers wired in?

**Yes — by design on this lane.** Research patterns are not passive README shelves. They feed:

| Surface | How research templates participate |
|---------|-------------------------------------|
| **Proposals** | `docs/proposals/` + critical-proposal path — research scaffolds inform structure of new work |
| **Evidence** | evidence-led receipts; research markers (hypothesis/finding/trust) align with dual-gate culture |
| **Decisions / voting** | help-wanted claims, dual-gate green/hold, PR disposition; research quality gates (coverage, provenance, adversarial review) inform promote/hold |
| **Project direction** | `15_Research_Repo_Templates` + SOURCE-MAP are inputs to Repository-development priority; Org phase board gates Enterprise promotion |
| **Improvements** | integrity checklist + inventory jobs; pattern harvest from 489+ forks / starred set → new slots under `15_*` |
| **Siloed Delphi** | Each tier-A slot has its own Proposal → Delphi → cycle stovepipe for independent outcome comparison — see `RESEARCH-SILO-DELPHI.md` + `ops/delphi/research-silos.json` |

They do **not** auto-vote or auto-merge. They supply structure, quality criteria, and evidence shape so humans + agents decide with better signal.

---

## 2. Decision / evidence wiring (concrete)

1. **Dual-gate** — every change under `refTemplates/` and `smods/` rides the same green path.
2. **evidence-led-monorepo-ops** — inventory `00_Index/SOURCE-MAP.md` vs `.gitmodules`; research slots must keep `SOURCE.txt`.
3. **help-wanted / tribute** — research-template work is claimable; foreign research PRs can be followed with the same follow-up poll.
4. **Proposals** — new research-shaped work should cite a `15_*` slot when adopting a layout (docxology pipeline, jogyo markers, yy layout, etc.).
5. **Codespace agent lane** — preferred smoke path before any new live `smods/` pin of a research template.
6. **credential-router** — research agents use free-first routing only (no hardcoded keys in templates).
7. **Research Silo Delphi** — 12 independent stovepipes (one per tier-A slot). Baseline cycle: RFP{1st_improve_request_cycle on RFP itself} → Delphi → validated output / feature extraction / consensus comparison. Evolutionary 🧬 variants (`rnd` · `selected` · `control`) extend per silo. Config: `ops/delphi/research-silos.json`. Spec: `docs/ops/RESEARCH-SILO-DELPHI.md`.

See also: `REFTEMPLATES-WORKFLOW-HOOKS.md`, `REFTEMPLATES-CONSOLIDATION.md`, `DELPHI-ORACLE-RFP-GATE.md`.

---

## 3. Evaluation of 489+ repos + starred set

**Policy:** continuous harvest, not one-shot dump.

| Tier | Criteria | Action |
|------|----------|--------|
| **A — Integrate metadata now** | Clear research-repo / project-template / agent-research layout; public; fits Repository development | Slot under `15_Research_Repo_Templates/` (done for core set) |
| **B — Watch / score** | High stars or active fork under timerloggedout-spec; research-adjacent but not yet layout-ready | List in SOURCE-MAP “candidates”; re-score on cadence |
| **C — Pattern only** | Single idea (marker style, gate, pipeline stage) without full scaffold | Document pattern in CONSOLIDATION or ops notes; no full slot |
| **D — Out of scope** | Unrelated product, pure app, or secret-heavy | Skip |

**Already tier-A (full 12):**

- jogyo-research-lab (Yeachan-Heo/My-Jogyo) — locator exemplar
- docxology-template
- yy-project-template
- buoyancy99-research-template
- yp-edu-research-project-template
- seunghyukoh-research-template
- irudik-repo-template
- jdingel-projecttemplate
- 3rdCore-Research_Project_Template
- dicklesworthstone-agentic-flywheel (metadata-only)
- opencode-research-papers
- cactus-needle

**Next harvest (B → A):** score starred agent/research runtimes and `_fork` research-adjacent repos (pyrite, CodeWiki_fork, alphadesk-terminal, MOBIUS-Searcher, etc.) against layout + Actions fitness; promote winners into `15_*`.

---

## 4. Expected independent results (current schema)

| Layer | Count | Attribution |
|-------|-------|-------------|
| Baseline research silo RFPs | **12** | One stream per `research.<slot>` |
| Existing free-tier surfaces | 18 | Orthogonal (quota/deploy/model) |
| With evolutionary 🧬 variants | up to 48 | 12 × (1 + rnd/selected/control) |

Research silos reuse the Delphi gate/panel/flywheel; they do not share scores across silos.

---

## 5. What “all” means

Operator said **yes…all** — meaning the full research-reference class, not only one upstream. Jogyo is the **example framework / locator**, not the exclusive integration.

Tree target:

```text
refTemplates/
├── 00_Index/                 # SSOT + recovery + SOURCE-MAP
├── 01 … 14/                  # category stubs from skeleton
├── 15_Research_Repo_Templates/  # full research class (12 silos)
├── 16_Org_Phased/            # org phase gates
└── smods/                    # live custom-adapted pins only
```

---

## 6. Non-goals

- Auto-merge research pins without dual-gate
- Treating every star as mandatory clone
- Research agents overriding dual-gate or credential policy
- Full recursive submodule on every CI run
- Cross-silo score aggregation that collapses attribution

**Agent-Identity:** Grok (Administrator) CXO  
