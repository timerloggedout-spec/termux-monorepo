"""Model selection market — equal-weight bootstrap, ledger, modes, DSPy-DoE stub, bets/cards.

Implements MSM-001..007. Free-first. Observe-mode weights. No secrets.
"""

from .bootstrap import bootstrap_equal_weights, load_static_free_seed
from .catalog_join import join_catalog, normalize_catalog_models
from .ledger import PerformanceLedger, LedgerSample
from .selector import select_models, SelectionMode
from .dspy_doe import DspyDoeStub, DoeArm
from .market import TradingCard, BetEntry, MarketGraph
from .router_peer import observe_peers_for_role, peers_as_router_pairs

__all__ = [
    "bootstrap_equal_weights",
    "load_static_free_seed",
    "join_catalog",
    "normalize_catalog_models",
    "PerformanceLedger",
    "LedgerSample",
    "select_models",
    "SelectionMode",
    "DspyDoeStub",
    "DoeArm",
    "TradingCard",
    "BetEntry",
    "MarketGraph",
    "observe_peers_for_role",
    "peers_as_router_pairs",
]
