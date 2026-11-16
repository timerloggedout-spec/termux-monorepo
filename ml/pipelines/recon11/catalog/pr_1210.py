"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1210,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix symlink hijacking in deepcli core file ops',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='sentinel-hardened-deepcli-file-ops-7975844610174716272',
)
