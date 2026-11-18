from __future__ import annotations

import hashlib
from pathlib import Path
import shutil


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class CacheStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, source: Path) -> str:
        checksum = digest(source)
        target_dir = self.root / checksum
        target_dir.mkdir(exist_ok=True)
        target = target_dir / source.name
        if not target.exists():
            shutil.copyfile(source, target)
            target.chmod(0o444)
        return checksum

    def materialize(self, checksum: str, filename: str, session_dir: Path) -> Path:
        source = self.root / checksum / filename
        if not source.is_file() or digest(source) != checksum:
            raise ValueError("cache artifact missing or integrity check failed")
        session_dir.mkdir(parents=True, exist_ok=True)
        target = session_dir / filename
        shutil.copyfile(source, target)
        target.chmod(0o644)
        return target
