"""labbook — the lab's own ML platform (v1).

Design: SYNTHESIS.md (~/workspace/lab-platforms/SYNTHESIS.md). Every design
decision in this package cites a row of that ledger; see README.md beside
this package for the mapping.

Contract: `labbook/1` — a small, versioned API surface (ledger row 11).
The entire v1 surface is:

    run(ir, params)                       -> verdict (every node enumerated)
    get_run(run_id)                       -> full run record
    materializations(asset_name)          -> append-only history
    latest(asset_name)                    -> latest materialization + metadata
    compare(run_a, run_b)                 -> param/metric/artifact-hash diff
    promote(asset, alias, materialization)-> alias set (attribution-stamped)
    verify(run_id | bundle)               -> per-check PASS/FAIL, named
    export_bundle(run_id)                 -> portable zip

Anything else is a new version of the contract, not a quiet addition.
"""

__version__ = "0.1.0"
CONTRACT = "labbook/1"

from .errors import LabbookError, IntegrityError, MissingBytesError

try:
    from .api import Labbook
except ImportError:  # partial checkout: submodules still importable
    Labbook = None  # type: ignore

__all__ = [
    "__version__",
    "CONTRACT",
    "Labbook",
    "LabbookError",
    "IntegrityError",
    "MissingBytesError",
]
