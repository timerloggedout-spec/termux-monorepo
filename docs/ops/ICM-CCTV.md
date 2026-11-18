# ICM-CCTV ops surface

Stepie goal 2087 step 10023: wire icm-cctv and visualization surfaces into Ops Dashboards.

This file records the **ML lane-observability projection contract**:

- Producer: `python3 -m ml.pipelines.cli cctv`
- Schema: `docs/schemas/icm-cctv.json`
- Code: `ml/pipelines/viz/cctv.py`
- Consumed by operator dashboards as a read-only PR-lane projection.

No secrets. Counts, lane labels, and master SHA only. The projection is not promotion authority; the repository’s dual-gate remains authoritative.

## Published ICM card board

The separate file-backed ICM visual-review board publication target is:

`https://timerloggedout-spec.github.io/tribute/icm-cctv.html`

It is generated from canonical Markdown cards under `docs/icm/_tv/screens/` by `scripts/build_icm_cctv_board.py` and included in the existing Tribute GitHub Pages publisher. It is a static mirror only; the canonical source records remain under `docs/icm/`.

The card board and ML lane projection share the ICM-CCTV label but retain separate data contracts:

| Surface | Input | Role |
|---|---|---|
| ICM card board | `docs/icm/_tv/screens/**/*.md` | Human review of ICM outcomes and checkpoints |
| ML lane projection | latest ML pipeline fixture via `python3 -m ml.pipelines.cli cctv` | Read-only PR lane counts, labels, and provenance |

Neither surface authorizes promotion, provider execution, or runtime routing changes.
