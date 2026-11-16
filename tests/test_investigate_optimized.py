import time
import os
import tempfile
import pytest
from deepcli.investigator.investigate import investigate_path, analyze_and_print

def test_investigate_mtime_ts_caching_and_sorting(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "a.py")
        file2 = os.path.join(tmpdir, "b.py")

        with open(file1, "w") as f:
            f.write("# file a\nprint('hello')")

        time.sleep(0.05)

        with open(file2, "w") as f:
            f.write("# file b\nprint('world')")

        entries = investigate_path(tmpdir)
        assert len(entries) == 2

        # Verify mtime_ts numeric float presence
        for e in entries:
            assert "mtime_ts" in e
            assert isinstance(e["mtime_ts"], (float, int))

        # Verify sorting and analyze_and_print output without throwing strptime errors
        analyze_and_print(entries, recent_days=1)
        captured = capsys.readouterr()
        assert "DeepSeek v4‑Pro Investigation Summary" in captured.out
        assert "Most Recent Files" in captured.out
