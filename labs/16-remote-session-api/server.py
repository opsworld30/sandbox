"""Local-only Session API simulation with a deliberately tiny command allowlist."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

TOKEN = os.environ.get("LAB_SESSION_TOKEN", "local-demo-token")
SESSIONS: dict[str, tempfile.TemporaryDirectory] = {}
COMMANDS = {"pwd": shutil.which("pwd"), "ls": shutil.which("ls"), "echo": shutil.which("echo")}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        return self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_POST(self) -> None:
        if not self.authorized():
            self.reply(401, {"error": "unauthorized"})
            return
        if self.path == "/sessions":
            session_id = uuid.uuid4().hex
            temp = tempfile.TemporaryDirectory(prefix=f"worker-{session_id[:8]}-")
            Path(temp.name, "README.txt").write_text("hello from worker\n", encoding="utf-8")
            SESSIONS[session_id] = temp
            self.reply(201, {"session_id": session_id})
            return

        parts = self.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "sessions" or parts[2] != "exec":
            self.reply(404, {"error": "not_found"})
            return
        session = SESSIONS.get(parts[1])
        if session is None:
            self.reply(404, {"error": "session_not_found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 4096:
                self.reply(400, {"error": "invalid_body_size"})
                return
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                self.reply(400, {"error": "json_object_required"})
                return
        except (ValueError, json.JSONDecodeError):
            self.reply(400, {"error": "invalid_json"})
            return

        argv = body.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
            self.reply(400, {"error": "argv_must_be_string_array"})
            return
        executable = argv[0]
        if executable not in COMMANDS or COMMANDS[executable] is None:
            self.reply(403, {"error": "command_not_allowed"})
            return
        try:
            result = subprocess.run(
                [COMMANDS[executable], *argv[1:]],
                cwd=session.name,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=2,
                check=False,
                shell=False,
                text=True,
                env={"PATH": os.defpath, "LANG": "C"},
            )
        except subprocess.TimeoutExpired:
            self.reply(408, {"error": "command_timeout"})
            return
        self.reply(200, {
            "returncode": result.returncode,
            "output": result.stdout[:4096],
            "output_truncated": len(result.stdout) > 4096,
        })

    def do_DELETE(self) -> None:
        if not self.authorized():
            self.reply(401, {"error": "unauthorized"})
            return
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "sessions":
            self.reply(404, {"error": "not_found"})
            return
        session = SESSIONS.pop(parts[1], None)
        if session is None:
            self.reply(404, {"error": "session_not_found"})
            return
        session.cleanup()
        self.reply(200, {"ok": True})

    def log_message(self, fmt: str, *args) -> None:
        print("api:", fmt % args)


if __name__ == "__main__":
    if not COMMANDS["pwd"] or not COMMANDS["ls"] or not COMMANDS["echo"]:
        raise SystemExit("pwd, ls and echo are required")
    server = ThreadingHTTPServer(("127.0.0.1", 8766), Handler)
    print("Local Session API on http://127.0.0.1:8766")
    try:
        server.serve_forever()
    finally:
        for session in SESSIONS.values():
            session.cleanup()
