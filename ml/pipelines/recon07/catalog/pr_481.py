"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=481,
    lane='EXTRACT',
    title='ops: make Jules PR handoffs observable',
    reasons=('state:unknown', 'minesweeper-title',),
    action='do-not-overwrite-peer',
    base='master',
)
