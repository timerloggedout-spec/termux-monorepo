"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1092,
    lane='NEED_EVIDENCE',
    title='test(preflight): bootstrap sys.path from checkout root in test_preflight.py',
    reasons=('wrong-base:feat/dashboard-lanes-v2',),
    action='never-retarget',
    base='feat/dashboard-lanes-v2',
    login='timerloggedout-spec',
    head_ref='test/bootstrap-syspath-preflight-plain-48',
)
