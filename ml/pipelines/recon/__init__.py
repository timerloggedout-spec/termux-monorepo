"""Observe-only tip reconciliation for Issue #175.

MLP-KEEP-006. Stdlib only. No network. No secrets. Does not restamp
``docs/ops/LANE-MATRIX.md`` and does not mutate v0.6.0 command-center constants.
"""
from ml.pipelines.recon.receipt import build_receipt

__all__ = ["build_receipt"]
