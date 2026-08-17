import sys
import os
from pathlib import Path

# Insert termux-multi-agent and deepcli directories into sys.path automatically during test discovery
repo_root = Path(__file__).resolve().parent.parent
multi_agent_dir = repo_root / "termux-multi-agent"
deepcli_dir = repo_root / "deepcli"

if str(multi_agent_dir) not in sys.path:
    sys.path.insert(0, str(multi_agent_dir))
if str(deepcli_dir) not in sys.path:
    sys.path.insert(0, str(deepcli_dir))
