#!/usr/bin/env python3
"""
NexusCLI Launcher
"""

import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import main

if __name__ == "__main__":
    main()
