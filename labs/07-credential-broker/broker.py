"""Local fake credential broker. Never connects to GitHub."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

ALLOWED_REPOSITORY = "opsworld30/sandbox-demo"
ALLOWED_BRANCH_PREFIX = "agent/"


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/git/push":
            self._reply(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16_384:
                self._reply(400, {"error": "invalid_body_size"})
                return
            request = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self._reply(400, {"error": "invalid_json"})
            return

        repository = request.get("repository")
        branch = request.get("branch")
        commit = request.get("commit")
        if repository != ALLOWED_REPOSITORY:
            self._reply(403, {"error": "repository_not_allowed"})
            return
        if not isinstance(branch, str) or not branch.startswith(ALLOWED_BRANCH_PREFIX):
            self._reply(403, {"error": "branch_not_allowed"})
            return
        if not isinstance(commit, str) or len(commit) != 40:
            self._reply(400, {"error": "invalid_commit_sha"})
            return

        # The secret is read only in the Broker process and is never serialized.
        token_present = bool(os.environ.get("FAKE_GITHUB_TOKEN"))
        self._reply(200, {
            "ok": True,
            "operation": "simulated_push",
            "token_present_in_broker": token_present,
        })

    def log_message(self, fmt: str, *args) -> None:
        # Avoid logging request headers or any credential-like material.
        print("broker:", fmt % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Fake Broker listening on http://127.0.0.1:8765")
    print("Fake credential configured:", bool(os.environ.get("FAKE_GITHUB_TOKEN")))
    server.serve_forever()
