# ITEMS — ML keep-alive extract (Issue #175)

| ID | Work | Priority | Owner | Status | Evidence / Boundary |
|---|---|---|---|---|---|
| MLP-KEEP-001 | Slim `ml/pipelines/` DAG + MoneyBall + lane short-circuit onto live master. Never wholesale-merge #432/#549/#601/#682. | P0 | Grok | landed | Merged #850 at `8424a50c`. Dual-gate on `1f6ebb16` (repo-gate 36644277092 + termux-smoke 36644276975). Vercel non-gate (#772). |
| MLP-KEEP-002 | ICM-CCTV projection (`cli cctv`) for ops dashboards. No secrets. | P1 | Grok | landed | On master via #843/#850. Schema `docs/schemas/icm-cctv.json`. |
| MLP-KEEP-003 | Minesweeper + supersede classifiers so Jules/Sentinel/Bolt peers are not overwritten. | P1 | Grok | landed | `lanes/minesweeper_rules.py`, `peers/`, skill `minesweeper-ops`. |
| MLP-KEEP-004 | Latest-session fixture resolver so keep-alive rebases do not restamp LANE-MATRIX policy. | P1 | Grok | landed | `lib/latest.py` + `fixtures/session_20260926.json`. |
| MLP-KEEP-005 | Align lane vocab with #836 (EXTRACT/CANDIDATE/NEED_EVIDENCE/SUPERSEDE). | P0 | Grok | landed | Invalid parking HOLD/WAIT/OBSERVE rejected in tests. Command-center v0.6.0 on master. |
| MLP-KEEP-006 | Command-center hub (`cli center|bind|drift|extract-plan`) + named-job dual-gate binder. | P0 | Grok | landed | #850 101-file extract. Skills: `ml-command-center`, `operator-hub-175`. |
