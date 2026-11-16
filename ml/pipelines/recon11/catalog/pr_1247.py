"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1247,
    lane='EXTRACT',
    title='🛡️ Sentinel: Harden provider availability probe output security',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules/security-harden-provider-availability-probe-10170932010595748102',
)
