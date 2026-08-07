#!/usr/bin/env python3
"""
Enhanced event-sourced dispatch pipeline for ArchWiz.
Decouples session ingestion from downstream updates (SSOT, Codex, Linear, etc.)
"""
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Callable

# Add root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archwiz.config import ARCHWIZ_ROOT, LOG_DIR, SSOT_DIR

# Setup logging
logging.basicConfig(
    filename=LOG_DIR / "dispatch.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("dispatch")

class DispatchPipeline:
    def __init__(self):
        self.dispatchers: List[Callable[[str, List[Dict[str, Any]]], None]] = []
        self._register_default_dispatchers()

    def register(self, func: Callable[[str, List[Dict[str, Any]]], None]):
        self.dispatchers.append(func)

    def _register_default_dispatchers(self):
        self.register(self.dispatch_ssot)
        self.register(self.dispatch_codex)
        self.register(self.dispatch_linear_hint)

    def dispatch_ssot(self, session_id: str, messages: List[Dict[str, Any]]):
        """Sync to Session SSOT."""
        try:
            from archwiz.session_ssot import SessionSSOT
            ssot = SessionSSOT()
            ssot.sync_session(session_id, messages)
            logger.info(f"SSOT sync successful for {session_id}")
        except Exception as e:
            logger.error(f"SSOT dispatch failed for {session_id}: {e}")

    def dispatch_codex(self, session_id: str, messages: List[Dict[str, Any]]):
        """Harvest code blocks into Codex."""
        try:
            from archwiz.codex import CodexIndex
            # We use a global index for the pipeline
            codex = CodexIndex(provider="pipeline")
            count = codex.harvest(session_id, messages)
            logger.info(f"Codex harvested {count} blocks from {session_id}")
        except Exception as e:
            logger.error(f"Codex dispatch failed for {session_id}: {e}")

    def dispatch_linear_hint(self, session_id: str, messages: List[Dict[str, Any]]):
        """Hint that a session might need Linear sync if it contains task updates."""
        # Simple heuristic: look for "done" or "task" in the last message
        if not messages:
            return
        last_msg = messages[-1].get("content", "").lower()
        if any(kw in last_msg for kw in ["done", "fixed", "implemented", "task"]):
            logger.info(f"Session {session_id} marked for Linear sync review")
            # In a full implementation, we might trigger linear_sync.py here
            # For now, we just log the hint.

    def run(self, session_id: str, messages: List[Dict[str, Any]]):
        """Execute all registered dispatchers."""
        start_time = time.time()
        logger.info(f"Starting dispatch for session {session_id} ({len(messages)} messages)")
        
        for dispatcher in self.dispatchers:
            try:
                dispatcher(session_id, messages)
            except Exception as e:
                logger.error(f"Dispatcher {dispatcher.__name__} crashed: {e}")
        
        duration = time.time() - start_time
        logger.info(f"Dispatch completed for {session_id} in {duration:.2f}s")

def trigger_dispatch(session_id: str, messages: List[Dict[str, Any]]):
    """Entry point for core.py and other ingestors."""
    pipeline = DispatchPipeline()
    pipeline.run(session_id, messages)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: dispatch_pipeline.py <session_id> [path_to_json]")
        sys.exit(1)
    
    sid = sys.argv[1]
    msgs = []
    
    if len(sys.argv) > 2:
        p = Path(sys.argv[2])
        if p.exists():
            msgs = json.loads(p.read_text())
    
    trigger_dispatch(sid, msgs)
