"""A deliberately small application-layer AI Sandbox Runtime prototype."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid


class PolicyDenied(PermissionError):
    pass


class MiniRuntime:
    COMMANDS = {
        "pwd": shutil.which("pwd"),
        "ls": shutil.which("ls"),
        "cat": shutil.which("cat"),
        "echo": shutil.which("echo"),
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self._temporary_root = tempfile.TemporaryDirectory(prefix="mini-runtime-") if root is None else None
        self.root = Path(root or self._temporary_root.name).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.sessions: dict[str, Path] = {}
        self.audit_path = self.root / "audit.jsonl"

    def _audit(self, event: str, session_id: str, **attributes) -> None:
        record = {
            "time": time.time(),
            "event": event,
            "session": session_id[:8],
            **attributes,
        }
        with self.audit_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        workspace = self.root / session_id
        workspace.mkdir(mode=0o700)
        (workspace / "README.txt").write_text("hello from isolated workspace\n", encoding="utf-8")
        self.sessions[session_id] = workspace
        self._audit("session.created", session_id)
        return session_id

    def _workspace(self, session_id: str) -> Path:
        workspace = self.sessions.get(session_id)
        if workspace is None:
            raise KeyError("session not found")
        return workspace

    def exec(self, session_id: str, argv: list[str]) -> dict:
        workspace = self._workspace(session_id)
        if not isinstance(argv, list) or not argv or not all(
            isinstance(item, str) for item in argv
        ):
            raise ValueError("argv must be a non-empty list of strings")

        name, *args = argv
        executable = self.COMMANDS.get(name)
        if executable is None:
            self._audit("exec.denied", session_id, command=name, reason="not_allowlisted")
            raise PolicyDenied(f"command not allowlisted: {name}")

        if name in {"pwd", "ls"} and args:
            raise PolicyDenied(f"{name} does not accept path arguments in this demo")
        if name == "cat":
            if len(args) != 1:
                raise ValueError("cat requires exactly one relative path")
            target = (workspace / args[0]).resolve(strict=True)
            try:
                target.relative_to(workspace)
            except ValueError as exc:
                self._audit("exec.denied", session_id, command=name, reason="path_escape")
                raise PolicyDenied("path escapes workspace") from exc
            if not target.is_file():
                raise PolicyDenied("cat target must be a regular file")
            args = [str(target)]
        if name == "echo" and len(args) > 32:
            raise ValueError("too many echo arguments")

        try:
            result = subprocess.run(
                [executable, *args],
                cwd=workspace,
                env={"PATH": os.defpath, "LANG": "C"},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
                timeout=2,
                check=False,
                text=True,
            )
        except subprocess.TimeoutExpired:
            self._audit("exec.timeout", session_id, command=name)
            return {"returncode": -1, "output": "", "timed_out": True}

        output = result.stdout[:4096]
        response = {
            "returncode": result.returncode,
            "output": output,
            "output_truncated": len(result.stdout) > 4096,
        }
        self._audit("exec.completed", session_id, command=name, returncode=result.returncode)
        return response

    def destroy_session(self, session_id: str) -> None:
        workspace = self._workspace(session_id)
        shutil.rmtree(workspace)
        del self.sessions[session_id]
        self._audit("session.destroyed", session_id)

    def close(self) -> None:
        if self._temporary_root is not None:
            self._temporary_root.cleanup()
