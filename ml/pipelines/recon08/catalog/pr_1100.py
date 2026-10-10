"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1100,
    lane='NEED_EVIDENCE',
    title='fix(core): stream_completion NameError on retry exhaustion (unbound final_text)',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='fix/get-session-sessions-nameerror',
)
