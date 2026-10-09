"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='issue',
    number=956,
    lane='NEED_EVIDENCE',
    title='ops(deepcli): make deepAgent.py + agent.py operational through CI/Termux bridge',
    reasons=('open-ops',),
    action='keep-on-board',
)
