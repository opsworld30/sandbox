import unittest

from policy import CapabilityDenied, ToolBroker


class ToolCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.broker = ToolBroker()

    def test_shell_can_read_workspace(self):
        self.assertIn("workspace", self.broker.read_workspace("shell"))

    def test_browser_cannot_read_workspace(self):
        with self.assertRaises(CapabilityDenied):
            self.broker.read_workspace("browser")

    def test_shell_cannot_use_browser_network(self):
        with self.assertRaises(CapabilityDenied):
            self.broker.fetch_example("shell")

    def test_mcp_reader_can_read_issue(self):
        self.assertIn("issue", self.broker.read_issue("mcp.issue.read"))


if __name__ == "__main__":
    unittest.main()
