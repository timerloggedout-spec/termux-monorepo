# ICM-CCTV ops surface

Stepie goal 2087 step 10023: wire icm-cctv && visualization surfaces into Ops Dashboards.

This is the **projection contract**, not a runtime GitHub Pages app.

- Producer: `python3 -m ml.pipelines.cli cctv`
- Schema: `docs/schemas/icm-cctv.json`
- Code: `ml/pipelines/viz/cctv.py`
- Consumed by operator dashboards (Command Center + future GitHub Pages)

No secrets. Counts + lane labels + master SHA only.
Primary Stepie goal 2149 is not reordered by this surface.
