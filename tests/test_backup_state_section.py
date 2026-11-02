"""Backups displayed (owner order, 2026-11-01): admin.html renders the
backup-state feed (backup-state/v1, Tracking's single-writer feed) with
the chart standard applied - last-export stamp, STALE when the state
hash moved past the last export, drill verdict visible."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/help-wanted-dashboard"


def test_admin_backup_state_section():
    html = (APP / "admin.html").read_text()
    assert "./data/backup-state-feed.json" in html
    assert "loadBackup" in html
    assert "state_hash===ex.state_hash" in html
    assert "summary.last_export_id" in html  # newest-first feed contract (PR #3617)
    assert "Restore drill verdict" in html
    assert "CK.bars(" in html and "stampState" in html
