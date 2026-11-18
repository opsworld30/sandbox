import unittest

from policy import EgressPolicy


class EgressPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = EgressPolicy({"github.com", "pypi.org"})

    def test_exact_match_allowed(self):
        self.assertTrue(self.policy.decide("github.com")[0])

    def test_subdomain_is_not_implicitly_allowed(self):
        self.assertFalse(self.policy.decide("api.github.com")[0])

    def test_suffix_attack_is_denied(self):
        self.assertFalse(self.policy.decide("github.com.evil.test")[0])

    def test_local_ip_is_denied(self):
        self.assertFalse(self.policy.decide("127.0.0.1")[0])

    def test_local_hostname_is_denied_even_if_listed(self):
        local_policy = EgressPolicy({"localhost", "service.local"})
        self.assertFalse(local_policy.decide("localhost")[0])
        self.assertFalse(local_policy.decide("service.local")[0])

    def test_scheme_is_not_a_hostname(self):
        self.assertFalse(self.policy.decide("https://github.com")[0])

    def test_trailing_dot_is_normalized(self):
        self.assertTrue(self.policy.decide("pypi.org.")[0])


if __name__ == "__main__":
    unittest.main()
