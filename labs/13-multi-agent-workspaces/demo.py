from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path


class ArtifactBroker:
    def __init__(self, root: Path, max_bytes: int = 1024 * 1024):
        self.root = root.resolve()
        self.max_bytes = max_bytes

    def publish(self, source_agent: str, relative_path: str, target_agent: str) -> str:
        source_root = (self.root / source_agent).resolve()
        target_root = (self.root / target_agent).resolve()
        source = (source_root / relative_path).resolve(strict=True)
        source.relative_to(source_root)
        target_root.relative_to(self.root)
        if not source.is_file() or source.stat().st_size > self.max_bytes:
            raise ValueError("artifact must be a regular file within size limit")

        inbox = target_root / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        destination = inbox / source.name
        shutil.copyfile(source, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        return digest


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="multi-agent-lab-") as tmp:
        root = Path(tmp)
        for name in ("agent-a", "agent-b"):
            (root / name).mkdir()
        (root / "agent-a" / "result.txt").write_text("artifact from A\n", encoding="utf-8")
        (root / "agent-b" / "private.txt").write_text("private data of B\n", encoding="utf-8")

        broker = ArtifactBroker(root)
        digest = broker.publish("agent-a", "result.txt", "agent-b")
        copied = root / "agent-b" / "inbox" / "result.txt"
        print("published:", copied.read_text(encoding="utf-8").strip())
        print("sha256:", digest)
        print("agent B private file remains:", (root / "agent-b" / "private.txt").exists())


if __name__ == "__main__":
    main()
