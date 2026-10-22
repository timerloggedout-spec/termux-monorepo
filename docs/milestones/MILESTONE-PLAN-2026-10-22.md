# termux-monorepo Milestone Plan

> Generated 2026-10-22 · 47 open PRs → 6 milestones, ordered by compounding benefit

---

## M1 — 🛡️ Security & Workflow Hardening

**Why first:** every other PR inherits whatever attack surface is open in CI.
**Closes:** Linear TER-120 (Prompt Injection), TER-67 (Pin 3rd-party Actions), TER-69 (Overly broad permissions)

| PR | Title | Status | Action |
|-----|-------|--------|--------|
| #92 | TER-69/67/120: lock permissions, pin Actions, sanitize prompt injection | 252 ECC comments, needs rebase | Rebase onto master |
| #1451 | deepagent worktree base fix | CodeRabbit approved | Auto-merge |
| #1441 | quota-triage lane | 9 CHANGES_REQUESTED | Resolve or close (superseded by #1495?) |

**Sentinel PRs (merged 2026-10-20):**
- ✅ #1269 — Session cache path traversal/symlink fix
- ✅ #1270 — Repository observatory topic extraction
- ✅ #1306 — Briefing contract validation + source curation perf
- ✅ #1246 — BIUDL procurement adoption + edge evidence contracts

**Conflict-blocked (approved, need rebase):**
- #1247 — Sentinel: provider availability probe hardening
- #1305 — Sentinel: model router cache hardening
- #1248 — Bolt: CI evaluators & scout perf (~10% faster)

---

## M2 — ⚡ Quota & Rate-limit Capacity

**Why second:** every run saved = headroom for everything else. Directly addresses #1283.
**Constraint:** AVOID limit notifications @ `n+1/n` && use exactly `n/n=to limit`, timing at full dynamic adaptive capacity with caching.

| PR | Title | Status | Action |
|-----|-------|--------|--------|
| #1495 | Full quota mappings: 27 provider families, GitHub safeguards, dashboard | Open | Review + merge (biggest capacity win) |
| #1492 | Automated provider recon refresh | Open, gated | Auto-merge |
| #1278 | Consolidate planning-lane crons (−50 runs/day) | Approved, awaiting merge | Auto-merge |
| #1496 | Tunnel Canary lag-as-notice, ATES pin fix | Already merged | ✅ |

**Remaining gaps:**
- Response caching layer (short-circuit at capacity)
- `n/n` threshold detection (suppress notification + serve cache instead of `n+1` call)
- Cadence timing tuning across quota boundaries

---

## M3 — 📋 Ops & Observability

**Why third:** makes everything auditable.

| PR | Title | Status | Action |
|-----|-------|--------|--------|
| #1493 | Lane consolidation SSOT + merged-branch audit | Jules | Auto-merge |
| #1491 | ECC audit outcomes → check runs mirror | Evidence-only, amended | Auto-merge |
| #1293 | Governed auto-review, safe auto-merge, stale-work triage | Open | Review (enables self-merging) |
| #1289 | Operations cadence audit | Open | Auto-merge |
| #1288 | GitLab reconciliation against canonical refs | Open | Auto-merge |
| #1292 | Actions matrix upgrade + capacity lag classification | Open | Auto-merge |

---

## M4 — 🔬 BIUDL Evidence Cockpit (#1241 epic)

**Why fourth:** builds on security + quota base.

| Priority | Title | Status |
|----------|-------|--------|
| P0 | Procurement adoption + edge evidence contracts | ✅ Merged (#1246) |
| P1 | Evidence ingestion + daily briefing | 🔲 No PR — CUT NEXT |
| P2 | FOSS procurement + reproducibility | Partial (validation landed, pinning pending) |
| P3 | Agent execution safety | 🔲 No PR |
| P4 | Observability + evaluation | 🔲 No PR |
| P5 | AST + supply chain gates | 🔲 No PR |
| P6 | Local/edge/ARM inference | Schema landed, benchmarks pending |

**Next deliverable:** P1 PR — deterministic normalization/dedup keyed by canonical URL + version, append-only observations, 5-item digest enforcement, machine-readable JSON/JSONL + Markdown output.

---

## M5 — 🏗️ Infrastructure & Runtime

| PR | Title | Status | Action |
|-----|-------|--------|--------|
| #1498 | Antigravity CLI: collaborative use cases, provisioning, offline readiness | DO NOT AUTO-MERGE | Commit/push only |
| #48 | llm-api-hub + ADE/kai9000 split (TER-71) | Long-lived staging | Decision: promote or archive |
| #81 | Gemini quota-gate + agent workflows promotion | Long-lived staging | Decision: promote or archive |
| #47 | refTemplates skeleton (Option B recovery) | Long-lived staging | Decision: promote or archive |
| #1301 | Telemetry equation registry + Wolfram verification | DRAFT | Continue when ready |
| #1286 | CRG-15: temporal integrity validator | 200 comments | Review |

---

## M6 — 📖 Research & Language

| PR | Title | Status | Action |
|-----|-------|--------|--------|
| #1494 | Linguist: conversational steganography cipher + notation matrices | Jules | Review (self-contained) |
| #1284 | ML: recon11 names-only connector probe | Open | Review |

---

## Execution Order

1. **Auto-merge queue** (collaborators/automated): #1451, #1278, #1492, #1493, #1491, #1289, #1288, #1292
2. **Review**: #1495 (quota mappings), #1293 (auto-merge governance)
3. **Rebase**: #92, #1247, #1305, #1248
4. **Resolve/close**: #1441 (9 changes requested)
5. **Cut next**: BIUDL P1 PR
6. **Decision**: #48, #81, #47 — promote or archive
