"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1224,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix path traversal and symlink hijacking in official export script',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-12531710281297676926-a90de56f',
)
