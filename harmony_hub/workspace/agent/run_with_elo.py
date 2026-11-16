#!/usr/bin/env python3
"""Run the multi-agent pipeline and update ELO after completion."""
import subprocess, sys, os
from pathlib import Path

# Run the original agent
agent_dir = Path.home() / 'termux-multi-agent'
result = subprocess.run([sys.executable, 'run.py'] + sys.argv[1:], cwd=agent_dir)

# Update ELO based on run_history verdicts
elo_updater = Path.home() / 'harmony_hub' / 'workspace' / 'elo' / 'elo_updater.py'
if elo_updater.exists():
    subprocess.run([sys.executable, elo_updater])

sys.exit(result.returncode)
