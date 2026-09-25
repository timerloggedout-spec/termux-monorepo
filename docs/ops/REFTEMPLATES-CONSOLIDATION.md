# REFTEMPLATES Consolidation — Narrow Slice + Research Lane + Actions Integration

**Date:** 2026-09-23 (policy realign post-#784)
**Status:** ACTIVE
**Directive:** BIUDL · Continuous Fully Automated Agentic Development · Agent auto-promote on dual-gate + task outcome
**Owner surface:** timerloggedout-spec/termux-monorepo
**Directed at:** Repository development first; complementary Orgs + Enterprise phased until self-sustaining.

---

## 1. Critical fact — narrow slice

`refTemplates/*` is a **narrow slice** of the full environment reconstruction.

- During original git initialization, files under the original refTemplates tree were removed with plain `rm` instead of `git rm`.
- Recovery path = `recreate/refTemplates-skeleton` + multiple restore commits.
- Master currently holds thin `01_Agent_Runtime/` metadata skeletons + live `smods/` gitlinks (custom-adapted, shallow).
- Full recursive submodule materialization is **rare and explicit**. Default posture = depth-1 / metadata-only + selective live pins.

Do **not** treat the current master tree as the complete reconstruction inventory.

---

## 2. Target layout (Repository development)

```text
refTemplates/
├── 00_Index/                          # navigator + recovery + SOURCE map
├── 01_Agent_Runtime/ … 14_…           # metadata-first
├── 15_Research_Repo_Templates/        # consolidated research scaffolds
│   └── jogyo-research-lab/            # primary — Yeachan-Heo/My-Jogyo pattern
├── 16_Org_Phased/                     # Enterprise + complementary orgs
└── smods/                             # LIVE custom-adapted gitlink lane
```

Rules:
- Metadata-first (README + SOURCE.txt + preferred fork URL).
- Live gitlinks only when a pin is required for Actions / agent runtime.
- Pin intentionally; promote when dual-gate green and task outcome verified.

---

## 3. Primary research pattern — *jogyo*

**Upstream:** https://github.com/Yeachan-Heo/My-Jogyo

Why first-class: end-to-end research automation, hypothesis → experiment → finding → adversarial review, two-gate completion, structured markers mapping to evidence-led + dual-gate culture.

No forced full clone on every runner. Sparse / on-demand only.

---

## 4. Actions / Workflows cadence integration

| Cadence surface | Integration |
|-----------------|-------------|
| Dual-gate | New metadata / gitlink changes ride the same green path |
| evidence-led-monorepo-ops | Inventory + integrity checks |
| adaptive-wait | Submodule / sparse-checkout jobs stay behind dual gates |
| review-loop | Continuous feedback; no synchronous HITL checkpoint when authority permits |
| help-wanted / tribute | Research-template work claimable like other lanes |
| credential-router | No hardcoded provider keys |

---

## 5. Orgs / Enterprise phase

1. Metadata + SOURCE map only
2. Own dual-gate green
3. Own evidence lane
4. No monorepo secret hard-dependency
5. Then promotion out of `16_Org_Phased/`

---

## 6. Execution order

1. This document lands.
2. Create `refTemplates/00_Index/` + jogyo metadata.
3. Expand skeleton categories as metadata-only.
4. Wire inventory / integrity into Actions.
5. Optional `smods/` pin when dual-gate ready.

Promote when dual gates green and task outcome verified. Agents auto-promote under full scoped authority (#184). Sovereignty cockpit = ArchWiz + chat for build-request projects.

---

## 7. Non-goals

- Full recursive submodule update as default CI behavior
- Treating `refTemplates` as the complete historical environment
- Promoting any pin without dual-gate + task-outcome evidence
- Hard-coding model / provider keys
- Treating Copilot / human review as a synchronous promote gate when dual-gate already passes

---

**Agent-Identity:** Grok (Administrator) · CXO
**Style:** BIUDL · Continuous Fully Automated Agentic Development · adaptive-wait · evidence-led · review-loop
