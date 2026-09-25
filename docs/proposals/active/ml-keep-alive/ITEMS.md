# ITEMS — ML keep-alive extract (Issue #175)

| ID | Work | Priority | Owner | Status | Evidence / Boundary |
|---|---|---|---|---|---|
| MLP-KEEP-001 | Slim `ml/pipelines/` DAG + MoneyBall + lane short-circuit onto live master. Never wholesale-merge #432/#549/#601/#682. | P0 | Grok | executing | Dual-gate on this SHA. Vercel non-gate (#772). |
| MLP-KEEP-002 | ICM-CCTV projection (`cli cctv`) for ops dashboards. No secrets. | P1 | Grok | executing | Schema `docs/schemas/icm-cctv.json`. |
| MLP-KEEP-003 | Minesweeper + supersede classifiers so Jules/Sentinel/Bolt peers are not overwritten. | P1 | Grok | executing | `lanes/minesweeper_rules.py`, `lanes/supersede_rules.py`. |
| MLP-KEEP-004 | Latest-session fixture resolver so keep-alive rebases do not restamp LANE-MATRIX policy. | P1 | Grok | executing | `lib/latest.py` + `fixtures/session_20260925.json`. |
| MLP-KEEP-005 | Align lane vocab with #836 (EXTRACT/CANDIDATE/NEED_EVIDENCE/SUPERSEDE). | P0 | Grok | executing | Invalid parking HOLD/WAIT/OBSERVE rejected in tests. |
