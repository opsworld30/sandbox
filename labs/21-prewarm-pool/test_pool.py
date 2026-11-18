import unittest

from pool import PrewarmPool


class PrewarmPoolTests(unittest.TestCase):
    def setUp(self):
        self.pool = PrewarmPool()
        self.env = self.pool.create("e1", now=0)

    def test_unattached_prewarm_expires(self):
        self.assertEqual(self.pool.tick("e1", now=301), "EXPIRED")

    def test_multiple_sessions_share_environment(self):
        self.pool.attach("e1", "a", now=10)
        self.pool.attach("e1", "b", now=10)
        self.assertEqual(self.env.sessions, {"a", "b"})

    def test_idle_environment_suspends(self):
        self.pool.attach("e1", "a", now=10)
        self.assertEqual(self.pool.tick("e1", now=1210), "SUSPENDED")

    def test_detach_does_not_delete_environment(self):
        self.pool.attach("e1", "a", now=10)
        self.pool.detach("e1", "a", now=20)
        self.assertEqual(self.env.state, "ATTACHED")
        self.assertIn("e1", self.pool.environments)


if __name__ == "__main__":
    unittest.main()
