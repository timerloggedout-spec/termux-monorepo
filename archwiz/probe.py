#!/usr/bin/env python3
"""Probe – lightweight testing layer for task verification."""
import sys, subprocess, ast, json
from pathlib import Path

HOME = Path.home()

def syntax_check(filepath):
    """Check if Python file compiles without syntax errors."""
    try:
        p = HOME / filepath
        if not p.exists():
            return False, f"File {filepath} not found."
        source = p.read_text()
        ast.parse(source)
        return True, "Syntax valid."
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def import_check(filepath):
    """Check if Python file can be imported (basic smoke test)."""
    try:
        p = HOME / filepath
        if not p.exists():
            return False, f"File {filepath} not found."
        import importlib.util
        spec = importlib.util.spec_from_file_location("module_under_test", p)
        if spec is None:
            return False, "Could not create module spec."
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, "Import successful."
    except Exception as e:
        return False, f"Import failed: {e}"

def run_pytest(filepath):
    """Run pytest on the file if test file exists."""
    test_file = HOME / filepath.replace('.py', '_test.py')
    if not test_file.exists():
        test_file = HOME / filepath.replace('.py', '.test.py')
    if not test_file.exists():
        test_dir = HOME / 'tests' / filepath.replace('.py', '_test.py')
        if not test_dir.exists():
            return None, "No test file found."  # Neutral — not a failure
    try:
        result = subprocess.run(
            ['python3', '-m', 'pytest', str(test_file), '--tb=short', '-q'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True, f"Tests passed.\n{result.stdout[-200:]}"
        else:
            return False, f"Tests failed.\n{result.stdout[-300:]}"
    except subprocess.TimeoutExpired:
        return False, "Test timeout (60s)."
    except Exception as e:
        return False, str(e)

def probe(filepath):
    """Run all available tests. Returns (passed, detail)."""
    results = []
    
    # Syntax check (always run)
    syn, syn_detail = syntax_check(filepath)
    results.append(("Syntax", syn, syn_detail))
    
    # Import check for Python files
    if filepath.endswith('.py'):
        imp, imp_detail = import_check(filepath)
        results.append(("Import", imp, imp_detail))
    
    # Unit tests if available
    test, test_detail = run_pytest(filepath)
    if test is not None:
        results.append(("Tests", test, test_detail))
    else:
        results.append(("Tests", True, "No test file (neutral)."))
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: probe.py <filepath> [--json]")
        sys.exit(1)
    filepath = sys.argv[1]
    json_out = '--json' in sys.argv
    results = probe(filepath)
    if json_out:
        print(json.dumps([{"check": r[0], "passed": r[1], "detail": r[2]} for r in results], indent=2))
    else:
        for name, passed, detail in results:
            icon = '✓' if passed else '✗'
            print(f"  {icon} {name}: {detail}")
    # Exit code: 0 if all passed, 1 if any failed
    all_pass = all(r[1] for r in results)
    sys.exit(0 if all_pass else 1)
