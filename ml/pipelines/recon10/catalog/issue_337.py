"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=337,
    lane='NEED_EVIDENCE',
    title='gh-Actions Continuous Evaluation',
    reasons=('continuous-eval',),
    action='not-a-promote-gate',
    base='',
    login='',
    head_ref='',
)
