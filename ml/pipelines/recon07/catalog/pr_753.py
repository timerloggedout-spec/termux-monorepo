"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=753,
    lane='CANDIDATE',
    title='fix(help-wanted): publish Vercel master alias in status',
    reasons=('state:unknown',),
    action='dual-gate-before-promote',
    base='master',
)
