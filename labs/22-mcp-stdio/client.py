import json
import subprocess
import sys


def send(process, message):
    process.stdin.write(json.dumps(message) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError("MCP server closed stdout")
    return json.loads(line)


def main():
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=1,
    )
    assert process.stdin is not None and process.stdout is not None
    try:
        print("initialize:", send(process, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "lab-client", "version": "0.1"}},
        }))
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()
        print("tools/list:", send(process, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}))
        print("tools/call:", send(process, {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "issue.read", "arguments": {"issue_id": "42"}},
        }))
    finally:
        process.stdin.close()
        process.terminate()
        process.wait(timeout=3)


if __name__ == "__main__":
    main()
