# Review Log — agent-readability-surface-contract

## Operator authorization — 2026-11-13

**Decision:** ACCEPTED · **Authority:** repository operator, direct instruction in the active project conversation.

**Authorized scope:** repair Agent Ready findings in source-owned pages; publish through the canonical GitHub Pages workflow; add P8 regression checks; add the conditional 95+ badge mechanism; establish the repository-wide DO-statement mandate; add the requested skill assets; and document MaxC/DerpWiki capability boundaries.

**Execution conditions:** preserve proposal item IDs, run `repo-gate` and `termux-smoke`, capture the Pages workflow receipt, and re-scan the deployed public pages.

**Evidence:** original scan `bCtaa4bIB7`; latest scan `vzNCPWMl7m`; source branch `fix/agent-readability-page-sources`.


## Live scan update — 2026-11-13

- Latest scan: [pbDNloUP-H](https://agent-ready.dev/scan/pbDNloUP-H), 89/100.
- P5–P8 pass; llms.txt 100/100; accessibility 93/100.
- Remaining page checks: P11 BreadcrumbList, P13 text-to-HTML ratio, P18 Link response header, and P19 Accept-based Markdown negotiation.
- Remaining accessibility check: A11 accessible name contains visible label.
- Website PR #48 merged the conditional badge and asset extraction; website PR #49 carries the P11/P13/A11 source fixes.
