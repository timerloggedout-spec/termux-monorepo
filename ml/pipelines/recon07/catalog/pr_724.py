"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind="pr",
    number=724,
    lane="EXTRACT",
    title="feat(ml): slim keep-alive pipelines re-extract",
    reasons=("ml-keep-alive-rebase-required",),
    action="extract-slice-only",
    base="master",
)
