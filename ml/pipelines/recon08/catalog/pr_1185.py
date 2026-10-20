"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1185,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix symlink hijacking in termux DB',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-11023333518494621232-d609c1b6',
)
