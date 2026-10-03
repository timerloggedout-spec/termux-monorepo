"""_v1_hindsight_shim -- compatibility shim over the recapitulation package.

Keeps a stable ``normalize_bank`` / ``shim_specs`` surface even if the
underlying recap module moves. Import order is safe: this module only
depends on ``_v1_recap`` which performs no I/O at import time.
"""

from __future__ import annotations

from ._v1_recap import (
    DEFAULT_BANK_ID,
    RECAP_VERSION,
    RecapEntry,
    normalize_bank,
    recap,
    shim_specs,
)

__all__ = [
    "DEFAULT_BANK_ID",
    "RECAP_VERSION",
    "RecapEntry",
    "normalize_bank",
    "recap",
    "shim_specs",
]
