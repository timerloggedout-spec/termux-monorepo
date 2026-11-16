"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1235,
    lane='EXTRACT',
    title='📖 Linguist: optimize PhaseCodec normalization and path regex pre-filtering',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='jules-linguist-phase-codec-path-guard-opt-8345547215966704407',
)
