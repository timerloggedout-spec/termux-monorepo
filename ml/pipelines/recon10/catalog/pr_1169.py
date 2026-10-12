"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1169,
    lane='EXTRACT',
    title='Consolidate Upgrades, Audits & Development Lanes',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-lane-consolidation-audit-2026-8400965583254461280',
)
