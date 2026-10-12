"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1211,
    lane='EXTRACT',
    title='⚡ Bolt: Optimize CI telemetry throughput and skill evaluation processing',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='bolt-ci-telemetry-optimization-10724079765498160567',
)
