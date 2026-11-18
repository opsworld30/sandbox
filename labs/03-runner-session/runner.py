"""Small POSIX command runner for teaching. Not an OS security sandbox."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


@dataclass
class ExecResult:
    returncode: int
    output: str
    timed_out: bool = False
    output_limited: bool = False


class LocalRunner:
    def __init__(self, workspace: str | Path, timeout: float = 5.0,
                 max_output_bytes: int = 64 * 1024) -> None:
        self.workspace = Path(workspace).resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError("workspace must be a directory")
        self.timeout = timeout
        self.max_output_bytes = max_output_bytes

    def _resolve_cwd(self, relative: str) -> Path:
        candidate = (self.workspace / relative).resolve(strict=True)
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise PermissionError("cwd escapes workspace") from exc
        if not candidate.is_dir():
            raise NotADirectoryError(candidate)
        return candidate

    def run(self, argv: list[str], cwd: str = ".") -> ExecResult:
        if os.name != "posix":
            raise RuntimeError("This teaching runner currently requires POSIX")
        if not isinstance(argv, list) or not argv or not all(
            isinstance(item, str) and item for item in argv
        ):
            raise ValueError("argv must be a non-empty list of strings")

        working_dir = self._resolve_cwd(cwd)
        env = {
            "PATH": os.defpath,
            "LANG": "C.UTF-8",
            "HOME": str(self.workspace),
        }
        proc = subprocess.Popen(
            argv,
            cwd=working_dir,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            start_new_session=True,
            close_fds=True,
        )
        assert proc.stdout is not None

        selector = selectors.DefaultSelector()
        selector.register(proc.stdout, selectors.EVENT_READ)
        output = bytearray()
        deadline = time.monotonic() + self.timeout
        timed_out = False
        output_limited = False

        def kill_process_group() -> None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        try:
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    kill_process_group()
                    break

                events = selector.select(min(0.1, remaining))
                for key, _ in events:
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    room = self.max_output_bytes - len(output)
                    output.extend(chunk[:max(room, 0)])
                    if len(chunk) > room:
                        output_limited = True
                        kill_process_group()
                        break
                if output_limited:
                    break
                if proc.poll() is not None and not selector.get_map():
                    break
        finally:
            selector.close()
            proc.stdout.close()

        if proc.poll() is None:
            kill_process_group()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            kill_process_group()
            proc.wait()

        return ExecResult(
            returncode=proc.returncode if proc.returncode is not None else -1,
            output=output.decode("utf-8", errors="replace"),
            timed_out=timed_out,
            output_limited=output_limited,
        )
