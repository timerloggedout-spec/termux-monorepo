"""Hindsight client shim — prefer official hindsight_client, fall back to local."""
from __future__ import annotations

import os

try:
    from hindsight_client import Hindsight as _OfficialHindsight

    def client():
        return _OfficialHindsight(
            base_url=os.environ["HINDSIGHT_BASE_URL"],
            api_key=os.environ.get("HINDSIGHT_API_KEY"),
        )

    KIND = "official"

except ImportError:
    from ._v1_hindsight import HindsightClient as _LocalHindsight

    def client():
        return _LocalHindsight()

    KIND = "local"
