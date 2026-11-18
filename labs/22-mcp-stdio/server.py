"""Tiny newline-delimited JSON-RPC MCP stdio teaching server."""
import json
import sys


def response(message_id, result):
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def error(message_id, code, message):
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def handle(message):
    method = message.get("method")
    message_id = message.get("id")
    if method == "initialize":
        return response(message_id, {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "sandbox-lab-mcp", "version": "0.1.0"},
        })
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return response(message_id, {})
    if method == "tools/list":
        return response(message_id, {
            "tools": [{
                "name": "issue.read",
                "description": "Read a fake issue from an in-memory fixture",
                "inputSchema": {
                    "type": "object",
                    "properties": {"issue_id": {"type": "string"}},
                    "required": ["issue_id"],
                    "additionalProperties": False,
                },
            }]
        })
    if method == "tools/call":
        params = message.get("params", {})
        if params.get("name") != "issue.read":
            return error(message_id, -32602, "unknown tool")
        args = params.get("arguments", {})
        issue_id = args.get("issue_id")
        if issue_id != "42":
            return response(message_id, {
                "content": [{"type": "text", "text": "Issue not found"}],
                "isError": True,
            })
        return response(message_id, {
            "content": [{"type": "text", "text": "Fake issue #42: Sandbox lab fixture"}],
            "isError": False,
        })
    return error(message_id, -32601, "method not found")


def main():
    for line in sys.stdin:
        try:
            message = json.loads(line)
            result = handle(message)
            if result is not None:
                sys.stdout.write(json.dumps(result) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            # Protocol output must stay on stdout; diagnostics go to stderr.
            print(f"server error: {exc}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
