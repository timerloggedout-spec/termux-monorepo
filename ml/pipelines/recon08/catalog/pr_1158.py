"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1158,
    lane='EXTRACT',
    title='📖 Linguist: optimize line-level markdown formatting pattern matching in CedrLang',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-4711132538048573035-c59ae474',
)
