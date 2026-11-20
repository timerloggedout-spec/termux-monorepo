#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: commit_notes.py
@description: Build commit-notes tool that extracts feature summaries from session conversations.
              Uses Router + Archaeologist pattern to identify structured sessions and extract
              full timelines, then generates markdown summaries keyed by session ID.
@author: ArchWizard 🧙‍♂️
@date: 2026-06-11
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# ============================================================
================
# 1. ROUTER AGENT : identifies sessions with dictionaries, tables, structured lists
# ============================================================
================

class RouterAgent:
    """Router Agent: scans session logs for structural patterns (dicts, tables, concept lists)."""
    
    def __init__(self, session_dir: Path):
        self.session_dir = Path(session_dir)
        self.session_patterns = {
            'has_dicts': re.compile(r'\{.*?\:.*?\}', re.DOTALL),
            'has_tables': re.compile(r'(\|.*\|[\r\n]+\|[-:]+\|)|(\+[-+]+\+)|(?:[^\n]+\t[^\n]+)', re.MULTILINE),
            'has_concept_lists': re.compile(r'^[\s]*[-*+]\s+\**([A-Z][a-zA-Z0-9\s]+)\**', re.MULTILINE),
            'structured_json': re.compile(r'