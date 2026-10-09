"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=1057,
    lane='NEED_EVIDENCE',
    title='fix(preflight): implement documented check_action()',
    reasons=('state:unknown',),
    action='hold-for-evidence',
    base='master',
)
