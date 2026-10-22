"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1239,
    lane='EXTRACT',
    title='fix(context): enforce collector path safety with lane verification evidence',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='ops/consolidate-upgrades-and-production-improvements-12666893236111238812',
)
