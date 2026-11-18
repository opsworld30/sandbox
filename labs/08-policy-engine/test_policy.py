import unittest

from policy import effective_policy, tool_allowed


class PolicyTests(unittest.TestCase):
    def test_allow_is_intersection(self):
        result = effective_policy(
            {"allow_tools": ["shell", "browser"]},
            {"allow_tools": ["shell"]},
        )
        self.assertEqual(result["allow_tools"], ["shell"])

    def test_deny_wins(self):
        result = effective_policy(
            {"allow_tools": ["shell", "mcp.read"]},
            {"deny_tools": ["mcp.read"]},
        )
        self.assertTrue(tool_allowed(result, "shell"))
        self.assertFalse(tool_allowed(result, "mcp.read"))

    def test_network_cannot_be_reenabled_by_later_layer(self):
        result = effective_policy(
            {"network": {"enabled": False}},
            {"network": {"enabled": True, "allowed_hosts": ["github.com"]}},
        )
        self.assertFalse(result["network"]["enabled"])
        self.assertEqual(result["network"]["allowed_hosts"], [])

    def test_host_allowlist_only_narrows(self):
        result = effective_policy(
            {"network": {"allowed_hosts": ["github.com", "pypi.org"]}},
            {"network": {"allowed_hosts": ["github.com"]}},
        )
        self.assertEqual(result["network"]["allowed_hosts"], ["github.com"])


if __name__ == "__main__":
    unittest.main()
