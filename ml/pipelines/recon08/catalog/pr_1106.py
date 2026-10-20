"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1106,
    lane='NEED_EVIDENCE',
    title='test(files): first coverage for _v1_files path-allowlist + ruff gate',
    reasons=('wrong-base:feat/dashboard-lanes-v2',),
    action='never-retarget',
    base='feat/dashboard-lanes-v2',
    login='timerloggedout-spec',
    head_ref='test/files-safe-ruffcheck-70',
)
