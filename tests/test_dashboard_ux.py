import sys
import os
from pathlib import Path

# Add termux-multi-agent to python path so we can import dashboard
sys.path.insert(0, str(Path(__file__).parent.parent / "termux-multi-agent"))

import dashboard
import pytest
from unittest.mock import patch, mock_open
from rich.panel import Panel
from rich.text import Text

def test_make_dashboard_empty_state():
    # Test dashboard with no telemetry logs
    with patch("os.path.exists", return_value=False):
        panel = dashboard.make_dashboard()
        assert isinstance(panel, Panel)

        # Since panel.renderable is a Group, let's inspect the renderable elements
        group = panel.renderable
        header_panel, body_panel = group.renderables

        # Verify the header contains "LIVE" and the pulsing dot "●"
        header_text = header_panel.renderable
        text_content = str(header_text)
        assert "LIVE" in text_content
        assert "●" in text_content

        # Verify the empty body contains helpful guidance to start the pipeline
        body_text = str(body_panel.renderable)
        assert "Waiting for background" in body_text
        assert "run_agent.sh" in body_text

def test_make_dashboard_with_jobs():
    # Mock telemetry entries
    mock_data = (
        '{"timestamp": "2026-08-01 12:00:00", "level": "SUCCESS", "agent": "A1", "target": "file1.py", "attempt": 1, "message": "Success!"}\n'
        '{"timestamp": "2026-08-01 12:00:05", "level": "RETRY", "agent": "A2", "target": "file2.py", "attempt": 2, "message": "Retrying..."}\n'
        '{"timestamp": "2026-08-01 12:00:10", "level": "CRITICAL", "agent": "A3", "target": "file3.py", "attempt": 3, "message": "Failed!"}\n'
        '{"timestamp": "2026-08-01 12:00:15", "level": "PROCESSING", "agent": "A4", "target": "file4.py", "attempt": 1, "message": "Working..."}\n'
    )

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=mock_data)):

        panel = dashboard.make_dashboard()
        assert isinstance(panel, Panel)

        group = panel.renderable
        header_panel, table, footer = group.renderables

        # Verify header contains "●" and "LIVE"
        header_text = header_panel.renderable
        assert "●" in str(header_text)
        assert "LIVE" in str(header_text)

        # Verify table has correct columns and rows
        assert len(table.columns) == 6
        assert table.columns[0].header == "Target File"
        assert table.columns[3].header == "Status"

        # Retrieve column contents
        targets = [str(c) for c in table.columns[0].cells]
        agents = [str(c) for c in table.columns[1].cells]
        statuses = [str(c) for c in table.columns[3].cells]

        assert len(targets) == 4
        assert len(agents) == 4
        assert len(statuses) == 4

        # SUCCESS row
        assert "file1.py" in targets[0]
        assert "A1" in agents[0]
        assert "🟢 SUCCESS" in statuses[0]

        # RETRYING row
        assert "file2.py" in targets[1]
        assert "A2" in agents[1]
        assert "🔄 RETRYING" in statuses[1]

        # CRITICAL row
        assert "file3.py" in targets[2]
        assert "A3" in agents[2]
        assert "🚨 CRITICAL" in statuses[2]

        # PROCESSING row
        assert "file4.py" in targets[3]
        assert "A4" in agents[3]
        assert "🔵 PROCESSING" in statuses[3]
