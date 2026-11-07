"""iOS2Termux — iOS to Termux with Gemini Carbon 4 Extended Thinking:
not Termux on the iPhone (impossible), but the honest working routes —
SSH into real Termux on Android, a Termux-style cloud box, command
translation for iOS shells, and shared-storage file transfer.

Created by Darion Kellar.
"""
from .brains import Gate, evaluate
from .carbon4 import Carbon4
from .planner import plan
from .routes import ROUTES, honest_verdict
from .translate import TRANSLATIONS, translate_command, translate_path

__all__ = ["Carbon4", "Gate", "ROUTES", "TRANSLATIONS", "evaluate",
           "honest_verdict", "plan", "translate_command", "translate_path"]
__version__ = "1.0.0"
