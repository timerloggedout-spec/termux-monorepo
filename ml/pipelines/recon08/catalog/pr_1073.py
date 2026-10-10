"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1073,
    lane='NEED_EVIDENCE',
    title='fix(tests): fail harness when a test_*.py module contributes 0 tests',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='fix/harness-silent-zero-test-module',
)
