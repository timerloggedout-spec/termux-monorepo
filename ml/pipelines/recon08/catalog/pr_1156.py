"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1156,
    lane='EXTRACT',
    title='ops(consolidation): consolidate lane upgrades, timing quotas, and audit tracking',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-8265505709842582653-6195d2c0',
)
