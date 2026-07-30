#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "🔍 Discovering whitelisted projects..."
python3 ~/.monorepo/discover_projects.py
echo "🔐 Scanning..."
python3 ~/.monorepo/scan_whitelist.py
echo "✅ Done. Report: ~/.monorepo/scan_report.txt"
