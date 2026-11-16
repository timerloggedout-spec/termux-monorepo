#!/usr/bin/env python3
"""Estimate RAM needed for orchestrator on a given target file."""
import json, sys, os
from pathlib import Path

HOME = Path.home()
GRAPH = HOME / 'workspace/llm_map/file_graph.json'

def estimate(target_file):
    """Return estimated peak RSS in KB."""
    # Base overhead for orchestrator process
    base = 80_000  # 80 MB
    
    # Target file size
    target_path = HOME / target_file
    target_size = os.path.getsize(target_path) if target_path.exists() else 0
    
    # Dependency file sizes (direct only)
    dep_size = 0
    if GRAPH.exists():
        graph = json.loads(GRAPH.read_text())
        for dep in graph.get(target_file, []):
            dep_path = HOME / dep
            if dep_path.exists():
                dep_size += os.path.getsize(dep_path)
    
    # Python objects ~3x file size in RAM
    total = base + (target_size + dep_size) * 3 // 1024  # KB
    return max(base, total)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: estimate_mem.py <target_file>")
        sys.exit(1)
    est = estimate(sys.argv[1])
    print(est)
