"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1135,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix insecure token storage & symlink vulnerability in Mistral bridge',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-14410145582528892786-38995331',
)
