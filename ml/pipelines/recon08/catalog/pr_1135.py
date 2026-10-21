"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1135,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix insecure token storage & symlink vulnerability in Mistral bridg',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-14410145582528892786-38995331',
)
