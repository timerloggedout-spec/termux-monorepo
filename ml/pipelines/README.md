# ml/pipelines — observe-mode keep-alive

Frozen recon stamp: v0.8.0 (`python3 -m ml.pipelines.cli recon`).
Frozen live cut: v0.9.0 (`python3 -m ml.pipelines.cli live`).
Current cut: v0.10.0 (`python3 -m ml.pipelines.cli cut`) on observer tip `df342068` (2026-10-12). That tip is a help-wanted status refresh already on master, not a product promote. Product SHA remains `8d36f149` until dual-gate passes on a newer candidate.

Stdlib only. No network. No secrets. No GPU.

```text
python3 -m ml.pipelines.cli status
python3 -m ml.pipelines.cli run
python3 -m ml.pipelines.cli cut
python3 -m ml.pipelines.cli probe
python3 -m ml.pipelines.cli live
python3 -m ml.pipelines.cli recon
python3 -m unittest discover -s ml/pipelines -p 'test_*.py'
```

Lane vocab v2: EXTRACT | CANDIDATE | NEED_EVIDENCE | SUPERSEDE.
HOLD / WAIT / OBSERVE are invalid parking.

v0.10.0 keeps the DAG. It does not retarget `live` (tests pin 0.9.0).
It classifies Jules as `app/google-labs-jules` and treats "session note" titles as SUPERSEDE.
CodeRabbit's ~100-file budget is advisory. The v0.10.0 cut is 99 files so the whole diff stays reviewable.

v0.11.0 (`python3 -m ml.pipelines.cli probe`) is the 2026-10-19 names-only connector probe on observer tip `fd8c30ac`. It does not retarget `cut`, `live`, or `recon`, and it does not restamp `PRODUCT_SHA`. Status-recon titles are SUPERSEDE. Closed wholesale ML PRs stay in locks. Adaptive-wait canonical content stays on master; this cut does not clobber it.

Do not wholesale-merge #432 / #549 / #601 / #682 / #724 / #746 / #787 / #817.
Do not restamp `docs/ops/LANE-MATRIX.md`.
Do not pulse-comment Issue #175.
Do not overwrite Jules minesweeper peers.
