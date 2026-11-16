"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1113,
    lane='EXTRACT',
    title='🛡️ Sentinel: Fix symlink hijacking and insecure permissions in mistral_bridge',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='fix/mistral-bridge-token-privileges-103982491902356344',
)
