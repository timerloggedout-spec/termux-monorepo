"""Brain/CNS-inspired software coordination analogies and pure primitives."""
from .action_selection import select_actions
from .attention import focus_signals
from .composer import compose_score
from .context import build_context
from .executive import normalize_intent
from .homeostasis import plan_wake
from .prediction import timing_error
from .signals import normalize_signals

__all__ = ["select_actions", "focus_signals", "compose_score", "build_context", "normalize_intent", "plan_wake", "timing_error", "normalize_signals"]
