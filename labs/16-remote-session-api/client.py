import json
import os
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8766"
TOKEN = os.environ.get("LAB_SESSION_TOKEN", "local-demo-token")


def request(method: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(req, timeout=4) as response:
        return json.loads(response.read())


session = request("POST", "/sessions")
session_id = session["session_id"]
print("created:", session_id)
try:
    for argv in (["pwd"], ["ls"], ["echo", "hello from client"]):
        print(argv, "=>", request("POST", f"/sessions/{session_id}/exec", {"argv": argv}))
    try:
        request("POST", f"/sessions/{session_id}/exec", {"argv": ["sh", "-c", "id"]})
    except Exception as exc:
        print("shell rejected:", type(exc).__name__)
finally:
    print("destroyed:", request("DELETE", f"/sessions/{session_id}"))
