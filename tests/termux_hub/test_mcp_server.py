from __future__ import annotations

import unittest

from termux_hub.mcp_server import RISH_RULES, SHELL_RULES, _allowed


class HubMcpPolicyTests(unittest.TestCase):
    def test_readonly_shell_allowlist(self):
        self.assertTrue(_allowed(["id"], SHELL_RULES))
        self.assertTrue(_allowed(["git", "status", "--short"], SHELL_RULES))
        self.assertFalse(_allowed(["sh", "-c", "id"], SHELL_RULES))
        self.assertFalse(_allowed(["rm", "-rf", "/"], SHELL_RULES))

    def test_readonly_shizuku_allowlist(self):
        self.assertTrue(_allowed(["pm", "list", "packages"], RISH_RULES))
        self.assertTrue(_allowed(["settings", "get", "secure", "enabled_accessibility_services"], RISH_RULES))
        self.assertFalse(_allowed(["am", "start", "-a", "android.intent.action.VIEW"], RISH_RULES))


if __name__ == "__main__":
    unittest.main()
