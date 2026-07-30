#!/usr/bin/env bash
set -e
echo "🔄 Updating whitelist from Caveman index..."
~/.monorepo/generate_whitelist_from_caveman.sh

echo "🔍 Discovering projects..."
~/.monorepo/discover_projects.py

echo "🔐 Running security scans (this may take a moment)..."
~/.monorepo/scan_whitelist.py

echo "✅ Scan complete. Report: ~/.monorepo/scan_report.txt"
echo "   Full report: cat ~/.monorepo/scan_report.txt"
echo "   Summary copied to clipboard (first 1000 chars)."
