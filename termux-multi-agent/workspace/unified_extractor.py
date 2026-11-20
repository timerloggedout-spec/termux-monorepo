#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ UNIFIED EXTRACTOR v4-PRO ⚡
Streams message_index.json → extracts code blocks, thinking_content, messages
Delimiter-resilient | Nested backticks | Malformed block recovery
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='🎯 %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Un1c0rnExtr4ct0r:
    """1337 ArchWizard extraction engine 🔱"""
    
    def __init__(self):
        self.code_pattern = re.compile(
            r'