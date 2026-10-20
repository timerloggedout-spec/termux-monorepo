"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=884,
    lane='EXTRACT',
    title='📖 Linguist: optimize SYMBOL_MAP pattern compilation and substitution',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='linguist-symbol-pattern-tuples-2979301438966234469',
)
