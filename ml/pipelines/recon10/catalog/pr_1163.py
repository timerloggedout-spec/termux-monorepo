"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1163,
    lane='EXTRACT',
    title='🛡️ Sentinel: Harden conv_branching refs persistence against symlink hijacking',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-conv-branching-symlink-privileges-11739175152869761632',
)
