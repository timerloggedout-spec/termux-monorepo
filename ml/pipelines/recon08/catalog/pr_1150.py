"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1150,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix symlink hijacking in archwiz listener control',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='fix/listener-control-symlink-privileges-8668155679404712612',
)
