import tempfile
import unittest
from pathlib import Path

from cache import CacheStore


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "dependency.bin"
        self.source.write_bytes(b"known artifact")
        self.cache = CacheStore(self.root / "cache")
        self.checksum = self.cache.put(self.source)

    def tearDown(self):
        self.tmp.cleanup()

    def test_materialize_creates_session_copy(self):
        target = self.cache.materialize(self.checksum, self.source.name, self.root / "session")
        self.assertEqual(target.read_bytes(), b"known artifact")
        target.write_bytes(b"session mutation")
        base = self.root / "cache" / self.checksum / self.source.name
        self.assertEqual(base.read_bytes(), b"known artifact")

    def test_tampered_cache_is_rejected(self):
        base = self.root / "cache" / self.checksum / self.source.name
        base.chmod(0o644)
        base.write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            self.cache.materialize(self.checksum, self.source.name, self.root / "session")

    def test_path_traversal_filename_is_rejected(self):
        with self.assertRaises(ValueError):
            self.cache.materialize(self.checksum, "../secret", self.root / "session")


if __name__ == "__main__":
    unittest.main()
