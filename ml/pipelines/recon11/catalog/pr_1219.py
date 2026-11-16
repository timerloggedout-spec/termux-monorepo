"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1219,
    lane='EXTRACT',
    title='⚡ Bolt: optimize CI provenance auditing, thread pool mapping, and scout issue ranking',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-833638555890319800-88927820',
)
