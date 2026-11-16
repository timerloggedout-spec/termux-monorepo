"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1223,
    lane='SUPERSEDE',
    title='ops(skills): live status recon 2026-10-14T06:26Z',
    reasons=('session-pulse',),
    action='supersede-generated-board-is-ssot',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/skills-recon-2026-10-14T06-26Z',
)
