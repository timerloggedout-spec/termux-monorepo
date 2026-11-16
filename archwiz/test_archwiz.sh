#!/bin/bash
# Automated smoke test for ArchWiz cockpit
echo "=== Testing ArchWiz ==="
# Test that dashboard starts and exits
echo -e "0" | timeout 5 python3 ~/archwiz/archwiz.py && echo "PASS: Dashboard exits cleanly" || echo "FAIL: Dashboard"

# Test task builder (if it takes piped input)
echo -e "test-001\nTest Task\nTest\nhigh\ndeveloper\nJust a test.\nn\nn" | timeout 10 python3 ~/archwiz/task_builder.py && echo "PASS: Task builder" || echo "FAIL: Task builder"

# Test timeline editor search
echo -e "6\nbranch\n0\n0" | timeout 10 python3 ~/archwiz/timeline_editor.py && echo "PASS: Timeline editor" || echo "FAIL: Timeline editor"

echo "=== Tests complete ==="
