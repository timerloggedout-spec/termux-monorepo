"""CodeRabbit file-window disposition. Advisory, not a dual-gate."""
from __future__ import annotations

from ml.pipelines.recon.catalog import BOT_EXTRACT_THRESHOLD, CODERABBIT_ADVISORY_MAX

def disposition(changed_files: int, *, bot: bool) -> str:
    count = int(changed_files)
    if count < 0:
        raise ValueError("changed_files must be >= 0")
    if count == 0:
        return "SUPERSEDE"
    if bot and count > BOT_EXTRACT_THRESHOLD:
        return "EXTRACT"
    return "CANDIDATE"

def over_advisory(changed_files: int) -> bool:
    return int(changed_files) > CODERABBIT_ADVISORY_MAX
