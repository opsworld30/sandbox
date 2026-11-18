import unittest

from expansion import CommandPolicy, ExpansionRequest


class ExpansionTests(unittest.TestCase):
    def test_approval_is_scoped_to_one_command(self):
        policy = CommandPolicy()
        request = ExpansionRequest("cmd-1", "registry.npmjs.org", "install")
        policy.approve(request)
        self.assertTrue(policy.network_allowed("cmd-1", "registry.npmjs.org"))
        self.assertFalse(policy.network_allowed("cmd-2", "registry.npmjs.org"))

    def test_other_hosts_remain_denied(self):
        policy = CommandPolicy()
        policy.approve(ExpansionRequest("cmd-1", "registry.npmjs.org", "install"))
        self.assertFalse(policy.network_allowed("cmd-1", "evil.example"))

    def test_base_deny_remains_unchanged(self):
        policy = CommandPolicy()
        policy.approve(ExpansionRequest("cmd-1", "registry.npmjs.org", "install"))
        self.assertFalse(policy.base_network_enabled)


if __name__ == "__main__":
    unittest.main()
