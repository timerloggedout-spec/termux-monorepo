"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=73,
    lane='NEED_EVIDENCE',
    title='fix(connectors): resolve critical bugs in connector_manager.py',
    reasons=('wrong-base:vibe/project-management-refresh-48caeb-staging',),
    action='never-retarget',
    base='vibe/project-management-refresh-48caeb-staging',
    login='timerloggedout-spec',
    head_ref='tembo/fix-connector-manager-bugs',
)
