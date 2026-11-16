#!/usr/bin/env python3
"""BatchResumer — incremental processing with crash‑proof checkpointing."""
import json, os
from pathlib import Path
from datetime import datetime, timezone

class BatchResumer:
    """
    Wraps an iterable and tracks progress in a state file.
    On restart, resumes from the last successfully processed item.
    
    Usage:
        items = load_my_data()          # list or generator
        br = BatchResumer("my_progress.state", len(items), flush_every=100)
        for item, i in br.process(items):
            # process item
            # every flush_every items, output is saved and state is written
            br.checkpoint(write_output_callback)
    """
    def __init__(self, state_file: str, total_items: int, flush_every: int = 100):
        self.state_path = Path(state_file)
        self.total = total_items
        self.flush_every = flush_every
        self.processed = self._load_state()
        self.current = self.processed
        self.start_time = datetime.now(timezone.utc)

    def _load_state(self) -> int:
        if self.state_path.exists():
            try:
                return int(self.state_path.read_text().strip())
            except (ValueError, OSError):
                return 0
        return 0

    def _save_state(self, n: int):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(str(n))

    def process(self, items):
        """
        Yields (item, index, is_checkpoint) tuples.
        Skips items before self.processed.
        Automatically saves state every flush_every items.
        """
        for i in range(self.processed, self.total):
            try:
                item = items[i]
            except IndexError:
                break
            self.current = i + 1
            is_checkpoint = (self.current % self.flush_every == 0) or (self.current == self.total)
            yield item, i, is_checkpoint
        # Final save
        self._save_state(self.current)

    def checkpoint(self, flush_fn=None):
        """Call this after processing each batch to persist progress."""
        self._save_state(self.current)
        if flush_fn:
            flush_fn()
        elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        pct = (self.current / self.total * 100) if self.total else 0
        print(f"  🔄 {self.current}/{self.total} ({pct:.1f}%) — {elapsed:.0f}s elapsed", end='\r')

    def finalize(self):
        """Clean up state file after complete success."""
        if self.state_path.exists():
            self.state_path.unlink()
        print(f"\n✅ Complete: {self.total} items in {(datetime.now(timezone.utc) - self.start_time).total_seconds():.1f}s")
