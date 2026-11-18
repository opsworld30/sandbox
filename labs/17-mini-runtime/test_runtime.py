import unittest

from runtime import MiniRuntime, PolicyDenied


class MiniRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = MiniRuntime()
        self.session = self.runtime.create_session()
        (self.runtime.root / "outside.txt").write_text("outside", encoding="utf-8")

    def tearDown(self):
        self.runtime.close()

    def test_allowlisted_command(self):
        result = self.runtime.exec(self.session, ["cat", "README.txt"])
        self.assertEqual(result["returncode"], 0)
        self.assertIn("hello from isolated workspace", result["output"])

    def test_shell_is_not_allowlisted(self):
        with self.assertRaises(PolicyDenied):
            self.runtime.exec(self.session, ["sh", "-c", "id"])

    def test_path_escape_is_denied(self):
        with self.assertRaises(PolicyDenied):
            self.runtime.exec(self.session, ["cat", "../outside.txt"])

    def test_destroy_removes_session(self):
        self.runtime.destroy_session(self.session)
        with self.assertRaises(KeyError):
            self.runtime.exec(self.session, ["pwd"])


if __name__ == "__main__":
    unittest.main()
