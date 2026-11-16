"""Manual read-only GitHub App capability probe. AR-21 slice, not a merge of #806.

The probe must not create checks, comments, branches, or secret values.
Missing APP_CLIENT_ID / APP_PRIVATE_KEY blocks the probe, not the dual-gate.
"""
from __future__ import annotations

from ml.pipelines.eval_lanes.contract import EvidenceContract

APP_PROBE = EvidenceContract(
    name="github-app-capability-probe",
    scope="manual read-only Checks permission probe",
    is_promote_gate=False,
    manual_only=True,
)


def probe_blocked(has_client_id: bool, has_private_key: bool) -> tuple[bool, str]:
    if has_client_id and has_private_key:
        return False, "configured"
    return True, "missing-app-credentials"
