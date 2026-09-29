#!/usr/bin/env python3
"""Optimized model router with evidence-driven candidate selection.

There is no provider hierarchy. Candidates are admitted by capability, credential,
catalog, quota, and evidence gates, then selected by the active routing policy.
Topology (single/series/dynamic/parallel/nested/co-working/volley) is an orchestration
concern and is recorded as experiment metadata rather than encoded as provider rank.
"""

import json
import os
import re
import sys
import time

from scripts import capability_spine

COUNTER_DIR = os.environ.get("COUNTER_DIR", "/tmp/model-router")
KEY_VAL_RE = re.compile(r'^("[^"]+"|\'[^\']+\'|[^:]+):\s*(.*)$')
