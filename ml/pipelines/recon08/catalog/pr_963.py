"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=963,
    lane='NEED_EVIDENCE',
    title='fix(ci): repair silent control-plane YAML breakage and gate the class',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='fix/control-plane-yaml-structure-gate',
)
