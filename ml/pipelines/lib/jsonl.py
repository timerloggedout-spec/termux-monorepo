"""Re-export replay JSONL at lib layer for CLI."""
from ml.pipelines.replay.jsonl import append_row, read_rows

__all__ = ["append_row", "read_rows"]
