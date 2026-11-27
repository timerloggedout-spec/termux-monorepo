#!/usr/bin/env python3
"""Compatibility entry point for the bounded, symlink-safe data-path scanner."""
import sys
from trace_data_flow_safe import main

if __name__ == "__main__":
    sys.exit(main())
