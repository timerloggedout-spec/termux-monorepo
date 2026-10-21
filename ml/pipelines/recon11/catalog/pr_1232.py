"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1232,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix symlink hijacking and permission exposure in model router',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-10734065785488144684-b71f206f',
)
