"""Brain/CNS-inspired coordination primitives; a software analogy, not neuroscience."""
from .action_selection import select_actions
from .composer import compose_score
from .context import build_context
from .executive import normalize_intent
from .homeostasis import plan_wake
from .prediction import timing_error
from .signals import normalize_signals

__all__ = ["select_actions", "compose_score", "build_context", "normalize_intent", "plan_wake", "timing_error", "normalize_signals"]
