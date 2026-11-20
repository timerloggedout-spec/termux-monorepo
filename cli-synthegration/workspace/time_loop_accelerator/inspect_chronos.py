#!/usr/bin/env python3
"""Examine existing Chronos/accelerator module to avoid duplication."""
import sys
from pathlib import Path
HOME = Path.home()
sys.path.insert(0, str(HOME / "cli-synthegration"))
try:
    from Chronos import accelerator
    print("=== Chronos.accelerator functions ===")
    for name in dir(accelerator):
        if not name.startswith('_'):
            obj = getattr(accelerator, name)
            if callable(obj):
                import inspect
                try:
                    sig = inspect.signature(obj)
                    print(f"  {name}{sig}")
                except:
                    print(f"  {name}()")
            else:
                print(f"  {name} = {obj}")
except Exception as e:
    print(f"Import failed: {e}")
