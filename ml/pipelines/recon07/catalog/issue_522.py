"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='issue',
    number=522,
    lane='NEED_EVIDENCE',
    title='ops: govern Historical Corpus Actions Backfill and Hex artifact provenance',
    reasons=('open-ops',),
    action='keep-on-board',
)
