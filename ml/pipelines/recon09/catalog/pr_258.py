"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=258,
    lane='NEED_EVIDENCE',
    title='feat(eval): add repository development performance suite',
    reasons=('wrong-base:master-staging',),
    action='never-retarget',
    base='master-staging',
    login='timerloggedout-spec',
    head_ref='feat/swe-performance-evaluation',
)
