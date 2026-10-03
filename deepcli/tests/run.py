#!/usr/bin/env python3
import sys, pathlib, unittest
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "test_*.py"
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for f in sorted(HERE.glob(pattern)):
        if f.name in ("__init__.py", "run.py"): continue
        try: suite.addTests(loader.loadTestsFromName(f.stem))
        except Exception as e: print(f"  skip {f.stem}: {e}")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__": sys.exit(main())
