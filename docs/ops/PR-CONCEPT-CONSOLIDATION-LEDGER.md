# PR Concept Consolidation Ledger (FAT slice)

**Version:** 2026-09-16T22:00Z
**Master HEAD at authoring:** `ff81cb6b` (#557)
**Authority:** read-only accounting + extract guidance — **does not merge, close, or force-push**
**Complements:** `LANE_CONSOLIDATION_SSOT.md`, `MERGED-BRANCH-AUDIT-2026.md`, `pr-minesweeper`, `ISSUE-175-MATRIX.yaml`
**Policy:** **Keep everything.** Prefer FAT concept rows with optional alternate lanes and starter stubs over deletion. Cherry-pick intent onto master; never wholesale-merge dirty megas.

Agent-Identity: Grok (Administrator)

---

## 1. Disposition codes

| Code | Meaning |
|------|--------|
| **LANDED** | Intent on master (extract or full). Keep source PR as history/provenance. |
| **EXTRACT** | Thin unique delta still worth re-applying from current master. |
| **HOLD** | Valid concept; blocked (extra-red, conflict, mega, staging-only). |
| **OPTIONAL_LANE** | Concept kept as alternate implementation path / experimental lane. |
| **STUB** | Starter surface only; expand later without blocking production. |
| **SUPERSEDED** | Duplicate of a newer or landed slice; close when safe; do not re-merge. |
| **DIRTY_HOLD** | Behind/conflicted; extract recipe only. |

Dual-gate before any promote: `agentic termux smoke` + `hygiene + portability gate`.
Extra-red (`validate-pull-request` / `validate-registry`) → HOLD wholesale even if dual-gate green.

---

## 2. Recently landed (master production spine)

| PR | Concept | SHA lineage |
|----|---------|-------------|
| #553 | colab-cli path-traversal + symlink-hijack guards | → #554/#555/#556/#557 chain |
| #554 | lag-index keyword tuple hoist | |
| #555 #556 #557 | evidence-led / adaptive-wait skill anchors + merge-queue jq fix | `ff81cb6b` |
| #542 | Linguist CedrLang short-circuit + fence guard | |
| #541 | lane consolidation / production improvements (RL-19 slice) | |
| #524 | Palette telemetry status badge | |
| #530 #531 | codespace agent lane | |
| #488 #534 … | AGENTS → CLAUDE fold | CLAUDE.md primary |
| #546 | reviewer-noise taxonomy anchors | |

Closed superseded this cycle: **#550**, **#551** (intent in #553/#554).

---

## 3. Concept map — open inventory (keep-all)

Grouped by **concept**, not PR number. Multiple PRs may share a concept; only one production extract should land per unique delta.

### 3.1 ML / MoneyBall / #175 matrix — **KEEP (HOLD extract)**

| PR | Draft | Disposition | Notes |
|----|-------|-------------|-------|
| **#549** | no | **HOLD** (extra-red) | Observe-mode ML rebase; dual-gate green historically; `validate-pull-request` / registry red. **Keep package intent.** |
| **#432** | no | **DIRTY_HOLD / SUPERSEDED-by-#549** | Dirty init sibling. Do not wholesale-merge. |
| Matrix YAML + skills in #549 | — | **STUB on master until extract** | `ISSUE-175-MATRIX.yaml`, `ml_pipelines/`, `pr-minesweeper` skill bodies live on the branch; cherry-pick when extra-red clears or as docs-only slice. |

**Optional lane:** MoneyBall scores remain **decision-support only** (never auto-merge).
**Starter stub:** `docs/ops/PR-MINESWEEPER.md` disposition table already on #549 branch.

### 3.2 Ops / skills / quality — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#543** | **HOLD** (stale base) | Skill definition quality lane + deployment map. Re-extract thin from `ff81cb6b`. |
| **#510** | **OPTIONAL_LANE** | Lane-consolidation audit & SSOT timing quotas (Jules). Overlaps docs already on master; keep as alternate narrative. |
| **#481** | **EXTRACT** candidate | Jules handoff observability. |
| **#483** | **EXTRACT** candidate | PR change ledger stale empty SHAs. |
| **#474** | **OPTIONAL_LANE** | Rate-limit consolidate + timing quotas. |
| **#466** | **OPTIONAL_LANE** | Lane audit SSOT + lag index. |
| **#527** | **HOLD** mega | Admission/pagination stall evidence gaps (pairs with #523). |
| **#523** | **HOLD** mega | Historical corpus continuation + agent throughput telemetry. Issue #522. |

### 3.3 Codespaces / gaps — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#545** | **HOLD** | Parallel multi-lane devcontainer per agent role. Prefer after single-lane #530/#531 stability. |
| **#500** | **OPTIONAL_LANE / STUB** | Gaps & Opportunities + codespaces-enablement proposal. Keep proposal text. |

### 3.4 ICM / RinDig / context graph — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#485** | **EXTRACT / OPTIONAL_LANE** | RinDig cost-of-remembering evidence + Content-Agent. Gitlink pins already in CLAUDE.md. |
| **#263** | **HOLD** mega | Manus context relationship graph. Partial evidence on master via Context Relationship audit workflow. |
| **#521** | **STUB** | ARO scope registry closeout (base `master-staging`). |

### 3.5 Linguist / CedrLang — **KEEP (lane duplicate → newest unique)**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#154** | **DIRTY_HOLD / likely SUPERSEDED** | Full CedrLang v2 overhaul + AGENTS.hum.md. Audit claimed #196 landed core; verify before close. |
| **#452** | **EXTRACT** candidate | Phase codec callbacks + short-circuiting. |
| **#436** | **LANE_DUPLICATE** | Unicode compression / phase codec. |
| **#425** | **LANE_DUPLICATE** | Translation callbacks. |
| **#418** | **LANE_DUPLICATE** | Fast-path backtick guard. |
| **#412** | **LANE_DUPLICATE** | Backtick pre-screening. |
| **#405** | **LANE_DUPLICATE** | Fast-path document compilation. |
| **#396** | **LANE_DUPLICATE** | Precomputed char pre-screening. |

**Rule:** ≥3 open on same theme → keep **newest unique micro-slice** as EXTRACT; leave others SUPERSEDED after extract lands. Concept (CedrLang perf) is **not** discarded.

### 3.6 Sentinel / security — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#429** | **EXTRACT** candidate | nexuscli symlink hijack on export/config. |
| **#419** | **LANE_DUPLICATE** | symlink safety + 0o600 on cmd_export. |
| **#404** | **LANE_DUPLICATE** | skip chmod when path is symlink. |
| **#402** | **LANE_DUPLICATE** | symlink hijack on os.chmod. |

**Policy:** production prefers **one** hardened path-walker pattern (already partially on master via colab-cli #553). Remaining PRs = optional hardening lanes / test vectors.

### 3.7 Bolt / performance — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#142** | **DIRTY_HOLD** | Telemetry seek/tell. Audit claimed #187; still open — verify then SUPERSEDED or re-extract. |
| **#471** | **EXTRACT / partial LANDED** | Lag index keywords (core landed #554) + hex moneyball CLI export remainder. |
| **#407** | **OPTIONAL_LANE** | Bellman-Ford arbitrage graph search. |
| **#392** | **OPTIONAL_LANE** | ast-grep availability check in central_mapper. |

### 3.8 Palette / PWA / Commingle — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#140** | **DIRTY_HOLD** | Stateful reactive PWA + vault refresh + a11y. |
| **#108** | **DIRTY_HOLD** | Commingle Swarm PWA reactivity refactor. |
| **#513** | **DRAFT / STUB** | npm+pnpm lockfile conflict fix. |

**Optional lane:** single canonical web lockfile policy (pnpm-first per lane SSOT); drafts stay until dual-gate.

### 3.9 Docs / debate / process — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#67** | **EXTRACT** candidate | PR scope discipline (CE-22) — why `src/db.py` ≠ agentic CI/CD. |
| **#69** | **OPTIONAL_LANE** | DEBATE dock TOC + Linear TER-116 (non-master base). |
| **#390** | **OPTIONAL_LANE / specimen** | Category-theoretic notation sets. Reviewer-noise taxonomy specimen. |
| **#540** | **EXTRACT** candidate | Fail-closed image asset pipeline + ATES SVG placeholder (#529). |
| **#455** | **HOLD** conflicted | Auto mmdc Mermaid render. |
| **#453** | **OPTIONAL_LANE** | Canonical issue observatory + similarity plane. |

### 3.10 Hub / connectors / OX-Alpha — **KEEP**

| PR | Disposition | Notes |
|----|-------------|-------|
| **#48** | **HOLD** (staging base) | LLM API hub + standalone server + ADE/kai9000 split. |
| **#73** | **EXTRACT** candidate | connector_manager critical bugs. |
| **#81** | **OPTIONAL_LANE** | Gemini quota-gate promote (event triggers). |
| **#386** | **DRAFT / STUB** | DeepSeek/OX Alpha evidence-first canary. |
| **#373** | **DRAFT / STUB** | Contextualize OX Alpha DeepSeek canary. |
| **#354** | **OPTIONAL_LANE** | Bound OX Alpha target context. |
| **#311** | **OPTIONAL_LANE** | GitLab reconciliation governance. |
| **#47** | **STUB** | refTemplates metadata-only skeleton recovery. |
| **#456** | **OPTIONAL_LANE** | Advisory CellCog SDK PR-review lane. |
| **#103** | **OPTIONAL_LANE** | CAVEMAN-micro seed + success matrix + Cheat_Code. |

---

## 4. Consolidated concept checklist (✅ keep)

Every row is **retained** as production, optional lane, or stub — none deleted.

| Concept | Production state | Open carriers | Next action |
|---------|------------------|---------------|-------------|
| Dual-gate spine | **LIVE** | — | Maintain |
| Evidence-led + adaptive-wait skills | **LIVE** `ff81cb6b` | — | Refresh anchors each cycle |
| Merge promotion queue (observer) | **LIVE** (jq fixed #557) | — | Confirm next schedule |
| colab-cli / path + symlink guards | **LIVE** #553 | #429 family | One more nexuscli extract optional |
| lag-index keywords | **LIVE** #554 | #471 remainder | Extract moneyball CLI only |
| ML observe-mode + #175 matrix | **HELD** | #549 #432 | Clear extra-red or docs-only extract |
| PR minesweeper dispositions | **HELD** (on #549) | — | Land with ML or standalone docs |
| Skill quality lane | **HELD** | #543 | Thin re-extract |
| Historical backfill + stall taxonomy | **HELD** mega | #523 #527 | Issue #522; no wholesale |
| Codespace multi-lane roles | **HELD** | #545 | After single-lane proven |
| Context relationship graph | **PARTIAL LIVE** (audit WF) | #263 | HOLD mega; evidence matrix on master |
| RinDig / cost-of-remembering | **PINNED** (CLAUDE gitlinks) | #485 | Optional evidence lane |
| CedrLang / Linguist perf | **PARTIAL LIVE** #542 | #154 #452 #436… | Newest unique extract only |
| Palette PWA UX | **PARTIAL** | #140 #108 | Extract a11y/vault or HOLD |
| LLM API hub | **STAGING** | #48 | Stay on master-staging until green |
| OX-Alpha / DeepSeek canary | **STUB** | #386 #373 #354 | Evidence-first drafts |
| Mermaid mmdc CI | **HELD** conflict | #455 | Rebase extract |
| Image asset / ATES placeholder | **OPEN** | #540 | Thin extract |
| Notation sets / category theory | **SPECIMEN** | #390 | Optional docs lane |
| Debate dock / CE-22 scope | **OPEN** | #69 #67 | Docs extracts OK |
| Commingle lockfile | **DRAFT** | #513 | pnpm-first stub |
| CellCog advisory review | **OPTIONAL** | #456 | Advisory only |
| GitLab recon governance | **OPTIONAL** | #311 | Non-blocking |
| refTemplates skeleton | **STUB** | #47 | Metadata-only |

---

## 5. Optional alternative lanes (explicit)

1. **MoneyBall observe-only** — scores never gate merge (`allow_write("merge")=false`).
2. **Linguist micro-extracts** — one short-circuit PR at a time vs #154 mega.
3. **Sentinel hardening suite** — keep duplicate PRs as test-vector lanes after one production pattern lands.
4. **Codespace role matrices** — multi-lane (#545) optional after single agent lane.
5. **Staging hub** (#48) — production remains Termux-first; hub is parallel surface.
6. **Hex non-AI trial** — already documented under `HEX-NON-AI-TRIAL-LANE.md`.

---

## 6. Starter stubs (do not block)

| Stub | Path / PR | Purpose |
|------|-----------|--------|
| Issue #175 matrix YAML | on #549 → target `docs/ops/ISSUE-175-MATRIX.yaml` | Fail-closed priority bind |
| ml_pipelines package | on #549 → `ml_pipelines/` | Observe DAG |
| pr-minesweeper skill | on #549 | Disposition codes |
| OX-Alpha canary drafts | #386 #373 | Evidence-first DeepSeek |
| Commingle lockfile draft | #513 | pnpm conflict resolution |
| refTemplates Option B | #47 | Metadata skeleton |
| Codespaces enablement proposal | #500 | Checklist only |

---

## 7. Extract priority queue (cherry-pick order)

When dual-gate capacity allows, prefer **FAT concept, thin file** extracts in this order:

1. **#483** ledger stale SHA fix (ops hygiene)
2. **#481** Jules handoff observability
3. **#67** PR scope discipline docs
4. **#540** image asset fail-closed + ATES placeholder
5. **#429** nexuscli symlink (if not covered by #553 pattern)
6. **#452** or newest unique Linguist micro-slice (close older duplicates after)
7. **#543** skill-quality lane rebased to `ff81cb6b`
8. **#549** ML package **only** after extra-red green or as docs/skills-only subset

Never: wholesale #523 #527 #263 #142 #154 #432 #48.

---

## 8. Maintenance

- Refresh this ledger when open PR count drifts >10% or after each mega disposition.
- Update `docs/ops/SKILLS-INVENTORY.md` cycle snapshot in the same PR when anchors change.
- Cross-link from `CLAUDE.md` quick pointers only if this becomes primary navigation (optional).

BIUDL. Keep everything. Cherry-pick the best.
