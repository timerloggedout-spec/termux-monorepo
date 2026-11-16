"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=103,
    lane='NEED_EVIDENCE',
    title='feat(comms): CAVEMAN-micro seed + success matrix + dual-file + CLAUDE.md Cheat_C',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='feature/caveman-micro-seed-matrices',
)
