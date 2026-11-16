"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=750,
    lane='EXTRACT',
    title='fix(core, dashboard): add fallback imports for requests, rich, and curl_cffi',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-13467256833851733900-324583d3',
)
