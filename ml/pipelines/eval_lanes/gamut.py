"""facebookresearch/GAMUT stays observational. AR-22 slice, not a merge of #809."""
from __future__ import annotations

from ml.pipelines.eval_lanes.contract import EvidenceContract

GAMUT = EvidenceContract(
    name="gamut",
    scope="observational benchmark behind the gamut-evaluation environment",
    is_promote_gate=False,
)
