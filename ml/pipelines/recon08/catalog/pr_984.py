"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=984,
    lane='NEED_EVIDENCE',
    title='fix(ci): stop deepseek branch zero-job workflow failures',
    reasons=('wrong-base:feat/gh-actions/deepseek-integrates-itself',),
    action='never-retarget',
    base='feat/gh-actions/deepseek-integrates-itself',
    login='timerloggedout-spec',
    head_ref='fix/deepseek-zero-job-runner-temp',
)
