"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1188,
    lane='SUPERSEDE',
    title='feat(ml): recon07 binder — product SHA vs observer tip (Issue #175)',
    reasons=('stale-recon07',),
    action='supersede-with-live-cut',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ml-recon07-20261009',
)
