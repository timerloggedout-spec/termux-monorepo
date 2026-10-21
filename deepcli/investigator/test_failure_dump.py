#!/usr/bin/env python3
"""Read the most recent DeepSeek test report and runtime logs to find failures."""
import json, os, glob, sys
from pathlib import Path

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def main():
    REPORTS = Path.home() / 'deepseek-cli' / 'test-reports'
    reports = sorted(glob.glob(str(REPORTS / 'report-*.json')), reverse=True)
    runtimes = sorted(glob.glob(str(REPORTS / 'runtime-*.json')), reverse=True)

    # Get latest report
    if not reports:
        print("No test reports found.")
        sys.exit(1)

    latest_report = load_json(reports[0])
    print("📋 Latest Test Report:", os.path.basename(reports[0]))
    if latest_report:
        # Try to find failures
        if isinstance(latest_report, list):
            for suite in latest_report:
                if isinstance(suite, dict):
                    suite_name = suite.get('suite','') or suite.get('name','')
                    tests = suite.get('tests',[]) or suite.get('results',[])
                    failures = [t for t in tests if t.get('status') == 'fail' or t.get('passed') == False]
                    if failures:
                        print(f"\n🔴 Suite: {suite_name} - {len(failures)} failures")
                        for f in failures[:5]:
                            print(f"  ❌ {f.get('name','')}: {f.get('error','')[:200]}")
                    else:
                        print(f"  ✅ {suite_name}: all passed")
        elif isinstance(latest_report, dict):
            print(json.dumps(latest_report, indent=2)[:2000])

    # Get latest runtime log (often contains console errors)
    if runtimes:
        print("\n📄 Latest Runtime Log:", os.path.basename(runtimes[0]))
        rt = load_json(runtimes[0])
        if rt:
            print(json.dumps(rt, indent=2)[:2000])
    else:
        print("No runtime logs found.")

if __name__ == "__main__":
    main()
