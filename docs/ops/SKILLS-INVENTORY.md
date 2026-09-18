# Skills Inventory (termux-monorepo)

**Version:** 2026-09-18 · **Last refreshed SHA:** `c082f533`
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` + `ml-pipelines` | `review-loop` + `pr-minesweeper` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate |

## Active ops skills

| Skill | Path |
|-------|------|
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |
| ml-pipelines | `.agents/skills/ml-pipelines/SKILL.md` |
| issue-175-matrix | `.agents/skills/issue-175-matrix/SKILL.md` |
| pr-minesweeper | `.agents/skills/pr-minesweeper/SKILL.md` |

## Cycle snapshot (2026-09-18T16:15Z)

- Master HEAD `c082f533` (`chore(docs): refresh DOCS-BRANCH-INDEX`).
- Dual-gate last terminal SUCCESS on `eefc068`: smoke **35301928043** + repo-gate **35301928066**. Later skill-record chain #590–#595 landed through `6af1e12`.
- Catalog extra-red: Historical Evaluation Correlation run **35356132030** FAIL on `automation_docs.py --check` after truncated `9aa6475` + regen `e24f08d` + docs-index `c082f533`. Not a dual-gate. This extract regenerates the catalog with `ml-pipelines.yml`.
- Dirty HOLD: #549 (superseded by this extract) / #432 ML init. Do **not** wholesale-merge.
- HOLD mega: #523 #527 #545 #543 #455 #485 #483 #481 #474 #471 #466 #500.
- Observe small-green: #596 skills-record (unstable), #597 Sentinel symlink, #598 Bolt regex, #599 catalog (dirty, superseded here).
- Extra-red ≠ gate: `validate-pull-request`, Vercel rate-limit, merge-promotion-queue inventory, comment-storm-skip.
- MoneyBall scores remain decision-support. Dual gates dominate.

BIUDL. Agent-Identity: Grok (Administrator)
