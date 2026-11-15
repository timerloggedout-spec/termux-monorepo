import importlib.util
import unittest

spec = importlib.util.spec_from_file_location("registry", "scripts/branch_reconciliation_registry.py")
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class ClassificationTests(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(registry.classify(0, 0), "identical")

    def test_ahead_only(self):
        self.assertEqual(registry.classify(3, 0), "ahead-only")

    def test_behind_only(self):
        self.assertEqual(registry.classify(0, 7), "behind-only")

    def test_diverged(self):
        self.assertEqual(registry.classify(2, 4), "diverged")


if __name__ == "__main__":
    unittest.main()
