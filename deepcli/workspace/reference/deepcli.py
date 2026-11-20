#!/usr/bin/env python3
"""DeepCLI launcher."""
import sys
from pathlib import Path

# Ensure ~/deepcli is on path so 'import deepcli.cli' works
sys.path.insert(0, str(Path(__file__).parent))
from deepcli.cli import main
main()
