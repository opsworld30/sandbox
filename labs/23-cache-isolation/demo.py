from pathlib import Path
import tempfile

from cache import CacheStore, digest


with tempfile.TemporaryDirectory(prefix="cache-lab-") as tmp:
    root = Path(tmp)
    source = root / "dependency.whl"
    source.write_bytes(b"fake dependency artifact")
    cache = CacheStore(root / "shared-cache")
    checksum = cache.put(source)
    session_a = cache.materialize(checksum, source.name, root / "session-a")
    session_b = cache.materialize(checksum, source.name, root / "session-b")
    session_a.write_bytes(b"modified by session A")
    print("session A changed:", digest(session_a) != checksum)
    print("session B unchanged:", digest(session_b) == checksum)
    print("base cache unchanged:", digest(root / "shared-cache" / checksum / source.name) == checksum)
