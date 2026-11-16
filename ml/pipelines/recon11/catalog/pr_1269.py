"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1269,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix path traversal and symlink hijacking in session cache',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-15282184680619337725-696787eb',
)
