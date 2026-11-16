"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=337,
    lane='NEED_EVIDENCE',
    title='gh-Actions Continuous Evaluation',
    reasons=('non-gate',),
    action='not-a-promote-blocker',
    base='master',
    login='',
    head_ref='',
)
