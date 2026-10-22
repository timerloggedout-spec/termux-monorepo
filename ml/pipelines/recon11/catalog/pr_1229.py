"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1229,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix token file persistence in mistral_bridge.py',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='fix/mistral-bridge-secure-token-persistence-14587553620701960129',
)
