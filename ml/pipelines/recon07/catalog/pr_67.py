"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=67,
    lane='NEED_EVIDENCE',
    title='docs(ops): PR scope discipline — why src/db.py is not agentic CI/CD',
    reasons=('state:unknown',),
    action='hold-for-evidence',
    base='master',
)
