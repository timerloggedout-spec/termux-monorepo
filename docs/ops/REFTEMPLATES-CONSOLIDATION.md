# REFTEMPLATES Consolidation — Narrow Slice + Research Lane + Actions Integration

**Date:** 2026-09-20  
**Status:** ACTIVE (feat/refTemplates-research-consolidate)  
**Directive:** BIUDL · AVOID HITL YOLO MODE YEET AUTOAPPROVE  
**Owner surface:** timerloggedout-spec/termux-monorepo  
**Directed at:** Repository development first; complementary Orgs + Enterprise phased until self-sustaining.

---

## 1. Critical fact — narrow slice

`refTemplates/*` is a **narrow slice** of the full environment reconstruction.

- During original git initialization, files under the original refTemplates tree were removed with plain `rm` instead of `git rm`.
- Recovery path = `recreate/refTemplates-skeleton` (categories 01–14 + Haven + Interpreted-Context-Methdology_fork + README_RECOVERY) + multiple restore commits (`65c9f811`, `b104890`, `8a53ffb`, …).
- Master currently holds:
  - Thin `01_Agent_Runtime/` metadata skeletons
  - Live `smods/` gitlinks (custom-adapted, shallow)
- Full recursive submodule materialization is **rare and explicit**. Default posture = depth-1 / metadata-only + selective live pins.

Do **not** treat the current master tree as the complete reconstruction inventory. The skeleton branch + this document + SOURCE maps are the SSOT for what was intended.

---

## 2. Target layout (Repository development)

```text
refTemplates/
├── 00_Index/                          # navigator + recovery + SOURCE map (new)
│   ├── README.md
│   ├── RECOVERY.md                    # rm-vs-git-rm incident + restore path
│   └── SOURCE-MAP.md
├── 01_Agent_Runtime/ … 14_…           # from skeleton (metadata-first)
├── 15_Research_Repo_Templates/        # NEW consolidated research scaffolds
│   ├── jogyo-research-lab/            # primary — Yeachan-Heo/My-Jogyo pattern
│   │   ├── README.md
│   │   └── SOURCE.txt                 # preferred: user fork first, then upstream
│   ├── docxology-template/
│   ├── yy-project-template/
│   ├── buoyancy99-research-template/
│   ├── yp-edu-research-project-template/
│   ├── seunghyukoh-research-template/
│   └── … (high-signal patterns from 489+ forks + starred set)
├── 16_Org_Phased/                     # Enterprise + complementary orgs (phase gates)
└── smods/                             # LIVE custom-adapted gitlink lane (keep)
    ├── AuditEngine_fork
    ├── batteries_fork
    ├── … (existing ICM / MCP / cost-of-remembering / …)
    └── <future research pins that need a live tree>
```

Rules:
- Metadata-first (README + SOURCE.txt + preferred fork URL).
- Live gitlinks only when a pin is required for Actions / agent runtime.
- Pin intentionally; never auto-advance without dual-gate green.

---

## 3. Primary research pattern — *jogyo*

**Upstream:** https://github.com/Yeachan-Heo/My-Jogyo  
**Name:** Gyoshu & Jogyo (Professor / Teaching Assistant research lab)

Why it is first-class for this monorepo:
- End-to-end research automation for OpenCode / agent surfaces
- Hypothesis → experiment → finding → adversarial review (Baksa) → report
- Persistent Python REPL + auto `.ipynb` + two-gate completion (Trust Gate + Goal Gate)
- Structured markers (`[OBJECTIVE]`, `[HYPOTHESIS]`, `[FINDING]`, `[STAT:…]`) that map cleanly to evidence-led + dual-gate culture
- MCP + OpenCode plugin paths already exist — natural fit for mcp-hub / termux-mcp / android-mcp cadence

Integration intent:
1. Metadata slot under `15_Research_Repo_Templates/jogyo-research-lab/`
2. Optional live pin under `smods/jogyo_fork` (or `My-Jogyo_fork`) once a user fork exists and dual-gate is ready
3. Workflow hooks: research-session evidence receipts, notebook integrity, trust-score surface (align with help-wanted / evidence-led lanes)

No forced full clone on every runner. Sparse / on-demand only.

---

## 4. Actions / Workflows cadence integration

All entries in the consolidated category must be visible to the existing cadence:

| Cadence surface | Integration |
|-----------------|-------------|
| Dual-gate | New metadata / gitlink changes ride the same green path; no special auto-merge |
| evidence-led-monorepo-ops | Inventory + integrity checks for `refTemplates/` + `smods/` |
| adaptive-wait | Submodule / sparse-checkout jobs stay behind dual gates |
| help-wanted / tribute | Research-template work can be claimed/foreign-followed like other lanes |
| credential-router + live-catalog | No hardcoded provider keys; research agents use the same free-first routing |
| ecc-tools overflow | Large template PRs still thin-track if comment volume warrants |
| Codespace agent lane | Preferred smoke path for any new research-template pin |

Concrete workflow work (to land on this feature branch or immediate follow-ups):
- Extend any existing submodule / inventory script to walk `15_Research_Repo_Templates/` and `smods/`
- Add a thin integrity job: SOURCE.txt present, preferred URL resolvable, shallow pin when gitlink
- Document recovery procedure so future agents never repeat the original `rm` trap

---

## 5. Orgs / Enterprise phase

Complementary orgs (including Research-Astute and the Enterprise one) integrate **in phases** until each is self-sustaining:

1. Metadata + SOURCE map only
2. Own dual-gate green on its primary surface
3. Own evidence lane / help-wanted receipts
4. No monorepo secret hard-dependency
5. Then promotion out of `16_Org_Phased/` into independent operation

---

## 6. Execution order (BIUDL continuous / dual-gate)

1. **This document** lands on `feat/refTemplates-research-consolidate`.
2. Create `refTemplates/00_Index/` + `15_Research_Repo_Templates/jogyo-research-lab/` metadata (SOURCE.txt → Yeachan-Heo/My-Jogyo + preferred fork note).
3. Expand remaining skeleton categories as metadata-only (no recursive bloat).
4. Wire inventory / integrity into Actions (reuse evidence-led patterns).
5. When a user fork of My-Jogyo exists and dual-gate is ready → optional `smods/` pin.
6. Org phase board in `docs/ops/`.

Promote only when dual gates green and task outcome verified. No YOLO / YEET / AUTOAPPROVE.

---

## 7. Non-goals

- Full recursive submodule update as default CI behavior
- Treating `refTemplates` as the complete historical environment (it is a narrow slice)
- Auto-merge of any pin without dual-gate
- Hard-coding model / provider keys inside research templates

---

**Agent-Identity:** Grok (Administrator) · CXO  
**Style:** BIUDL · AVOID HITL YOLO MODE YEET AUTOAPPROVE · adaptive-wait · evidence-led  
