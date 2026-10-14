"""Frozen recon11 observation. Not a merge decision. 2026-10-14."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1209,
    lane='SUPERSEDE',
    title='ops(skills): session note 2026-10-12 06:22 UTC — master green, continue monitoring',
    reasons=('session-pulse',),
    action='supersede-generated-board-is-ssot',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/session-note-20261012-0622',
)
