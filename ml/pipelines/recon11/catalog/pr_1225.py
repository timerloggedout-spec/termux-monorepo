"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1225,
    lane='EXTRACT',
    title='⚡ Bolt: Fast-path field set equality check in SWE evaluation contract validation',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='perf/swe-evaluation-fastpath-keys-12832393979879147060',
)
