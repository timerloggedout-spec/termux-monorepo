"""Model selection market — equal-weight bootstrap, ledger, modes, DSPy-DoE stub, bets/cards.

Implements MSM-001..005. Free-first. Observe-mode weights. No secrets.
"""

from .bootstrap import bootstrap_equal_weights, load_static_free_seed
from .ledger import PerformanceLedger, LedgerSample
from .selector import select_models, SelectionMode
from .dspy_doe import DspyDoeStub, DoeArm
from .market import TradingCard, BetEntry, MarketGraph

__all__ = [
    "bootstrap_equal_weights",
    "load_static_free_seed",
    "PerformanceLedger",
    "LedgerSample",
    "select_models",
    "SelectionMode",
    "DspyDoeStub",
    "DoeArm",
    "TradingCard",
    "BetEntry",
    "MarketGraph",
]
