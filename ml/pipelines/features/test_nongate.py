import unittest
from ml.pipelines.features.nongate import is_nongate_context

class Nongate(unittest.TestCase):
    def test_vercel(self):
        self.assertTrue(is_nongate_context("Vercel – termux-monorepo"))

    def test_coderabbit(self):
        self.assertTrue(is_nongate_context("CodeRabbit"))

    def test_repo_gate_is_gate(self):
        self.assertFalse(is_nongate_context("hygiene + portability gate"))
