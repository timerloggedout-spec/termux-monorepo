"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=67,
    lane='NEED_EVIDENCE',
    title='docs(ops): PR scope discipline — why src/db.py is not agentic CI/CD (CE-22)',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='docs/pr-scope-discipline-ce22',
)
