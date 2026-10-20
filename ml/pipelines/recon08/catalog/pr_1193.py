"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1193,
    lane='EXTRACT',
    title='ops(consolidation): align timing quotas, cooldowns and lane tests',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='ops/lane-consolidation-upgrades-6953068778775386736',
)
