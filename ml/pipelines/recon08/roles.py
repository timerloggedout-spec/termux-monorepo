"""SHA roles for the 2026-10-10 cut. Observer tip is not a promote."""
from __future__ import annotations

VERSION = "0.8.0"
PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"
OBSERVER_TIP = "677a2d72d6c251e4f12e81e1bdba3b787671b2d6"
OPEN_PRS_OBSERVED = 202
PREDECESSOR_PR = 1188
AGENT = "Grok (Administrator)"

# Last command-center dual-gate record. Do not restamp from a help-wanted
# or sweep commit. A newer SHA promotes only after named jobs on THAT sha.
PRODUCT_NOTE = "last recorded dual-gate in command-center constants"
OBSERVER_NOTE = "sweep accountability receipt on master; not a product promote"
